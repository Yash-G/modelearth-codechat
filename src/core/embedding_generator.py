import openai
from typing import List, Dict, Any, Optional, Union
import hashlib
import json
from pathlib import Path

class CodeEmbeddingGenerator:
    """Enhanced embedding generator for code chunks with summary integration"""

    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.embedding_cache = {}  # Cache for expensive embeddings

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text with caching"""
        try:
            # Create cache key
            text_hash = hashlib.md5(text.encode()).hexdigest()
            if text_hash in self.embedding_cache:
                return self.embedding_cache[text_hash]

            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )

            embedding = response.data[0].embedding
            self.embedding_cache[text_hash] = embedding
            return embedding

        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts in batch with caching"""
        try:
            # Check cache first
            uncached_texts = []
            uncached_indices = []
            cached_embeddings = []

            for i, text in enumerate(texts):
                text_hash = hashlib.md5(text.encode()).hexdigest()
                if text_hash in self.embedding_cache:
                    cached_embeddings.append((i, self.embedding_cache[text_hash]))
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)

            # Generate embeddings for uncached texts
            if uncached_texts:
                response = self.client.embeddings.create(
                    input=uncached_texts,
                    model=self.model
                )

                # Cache new embeddings
                for j, data in enumerate(response.data):
                    text_hash = hashlib.md5(uncached_texts[j].encode()).hexdigest()
                    embedding = data.embedding
                    self.embedding_cache[text_hash] = embedding
                    cached_embeddings.append((uncached_indices[j], embedding))

            # Sort by original index and return
            cached_embeddings.sort(key=lambda x: x[0])
            return [emb for _, emb in cached_embeddings]

        except Exception as e:
            print(f"Error generating embeddings batch: {e}")
            return [None] * len(texts)

    def generate_hybrid_embedding(self, chunk_content: str, summary: str,
                                full_code_summary: Optional[Dict[str, Any]] = None,
                                weights: Optional[Dict[str, float]] = None) -> Optional[List[float]]:
        """
        Generate hybrid embedding combining chunk content, summary, and full code context

        Args:
            chunk_content: The actual code chunk content
            summary: Summary of the chunk
            full_code_summary: Summary of the full code file (optional)
            weights: Weights for combining different text sources

        Returns:
            Combined embedding vector
        """
        if weights is None:
            weights = {
                'chunk': 0.5,
                'summary': 0.3,
                'full_context': 0.2
            }

        try:
            texts_to_embed = []
            weights_list = []

            # Chunk content
            if chunk_content:
                texts_to_embed.append(chunk_content)
                weights_list.append(weights['chunk'])

            # Chunk summary
            if summary:
                texts_to_embed.append(summary)
                weights_list.append(weights['summary'])

            # Full code context
            if full_code_summary and full_code_summary.get('summary'):
                context_text = f"File context: {full_code_summary['summary']}"
                if full_code_summary.get('key_functions'):
                    context_text += f" Key functions: {', '.join(full_code_summary['key_functions'][:3])}"
                texts_to_embed.append(context_text)
                weights_list.append(weights['full_context'])

            if not texts_to_embed:
                return None

            # Generate embeddings
            embeddings = self.generate_embeddings_batch(texts_to_embed)

            if not embeddings or None in embeddings:
                return None

            # Weighted combination
            combined_embedding = [0.0] * len(embeddings[0])
            total_weight = sum(weights_list)

            for embedding, weight in zip(embeddings, weights_list):
                if embedding:
                    for i, val in enumerate(embedding):
                        combined_embedding[i] += val * (weight / total_weight)

            return combined_embedding

        except Exception as e:
            print(f"Error generating hybrid embedding: {e}")
            return None

    def add_embeddings_to_chunks(self, chunks: List[Dict[str, Any]],
                               full_code_summary: Optional[Dict[str, Any]] = None,
                               use_hybrid: bool = True) -> None:
        """
        Add embeddings to chunks using hybrid approach

        Args:
            chunks: List of chunk dictionaries
            full_code_summary: Summary of the full code file
            use_hybrid: Whether to use hybrid embedding approach
        """
        if use_hybrid and full_code_summary:
            # Use hybrid embeddings
            for chunk in chunks:
                chunk_content = chunk.get("content", "")
                summary = chunk.get("summary", "")

                embedding = self.generate_hybrid_embedding(
                    chunk_content, summary, full_code_summary
                )
                chunk["embedding"] = embedding
        else:
            # Use traditional approach
            texts = []
            for chunk in chunks:
                if chunk.get("summary"):
                    texts.append(chunk["summary"])
                else:
                    texts.append(chunk.get("content", ""))

            embeddings = self.generate_embeddings_batch(texts)

            for i, chunk in enumerate(chunks):
                chunk["embedding"] = embeddings[i]

    def generate_file_level_embedding(self, full_code_summary: Dict[str, Any],
                                    chunks: List[Dict[str, Any]]) -> Optional[List[float]]:
        """
        Generate file-level embedding from full code summary and all chunks

        Args:
            full_code_summary: Summary of the full code file
            chunks: All chunks from the file

        Returns:
            File-level embedding
        """
        try:
            # Combine file summary with key chunk information
            file_context = full_code_summary.get('summary', '')

            # Add key chunk summaries
            key_chunks = []
            for chunk in chunks[:5]:  # Use first 5 chunks for context
                if chunk.get('summary'):
                    key_chunks.append(chunk['summary'])

            if key_chunks:
                file_context += f"\nKey components: {'; '.join(key_chunks)}"

            return self.generate_embedding(file_context)

        except Exception as e:
            print(f"Error generating file-level embedding: {e}")
            return None

    def clear_cache(self):
        """Clear the embedding cache"""
        self.embedding_cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "cached_embeddings": len(self.embedding_cache),
            "cache_memory_mb": len(self.embedding_cache) * 0.004  # Rough estimate
        }

    def save_cache(self, file_path: str):
        """Save embedding cache to file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.embedding_cache, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def load_cache(self, file_path: str):
        """Load embedding cache from file"""
        try:
            with open(file_path, 'r') as f:
                self.embedding_cache = json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")


# Backward compatibility
class EmbeddingGenerator(CodeEmbeddingGenerator):
    """Legacy EmbeddingGenerator class for backward compatibility"""
    pass
