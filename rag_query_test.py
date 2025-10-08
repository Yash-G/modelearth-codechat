import os
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI
import google.generativeai as genai

# Load credentials
load_dotenv()

# Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
genai.configure(api_key=GOOGLE_API_KEY)
pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

# Pinecone index config
INDEX_NAME = "model-earth-jam-stack"
index = pinecone_client.Index(INDEX_NAME)
gemini_model = genai.GenerativeModel("gemini-2.5-flash-lite")

# Get all namespaces once
def get_all_namespaces():
    stats = index.describe_index_stats()
    return list(stats["namespaces"].keys())

# Main function: query all namespaces and merge top_k results
def query_all_namespaces(question, top_k=10, per_ns_k=5, min_score=None):
    try:
        embed_response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=question
        )
        query_vector = embed_response.data[0].embedding
    except Exception as e:
        return f"❌ Embedding error: {e}"

    # Collect results from all namespaces
    combined_matches = []
    for ns in get_all_namespaces():
        try:
            results = index.query(
                vector=query_vector,
                top_k=per_ns_k,
                include_metadata=True,
                namespace=ns
            )
            matches = results["matches"]
            if min_score:
                matches = [m for m in matches if m["score"] >= min_score]
            combined_matches.extend(matches)
        except Exception as e:
            continue  # ignore broken namespaces

    # Sort combined matches by score
    combined_matches = sorted(combined_matches, key=lambda x: x["score"], reverse=True)
    top_matches = combined_matches[:top_k]

    if not top_matches:
        return f"❌ No relevant context found for: {question}"

    # Extract context
    context = "\n\n---\n\n".join(
    f"[File: {m['metadata'].get('file_path', 'unknown')}]\n{m['metadata'].get('content', '')}"
    for m in top_matches
    if "content" in m["metadata"]
)


    prompt = f"""
You are a helpful, professional AI assistant supporting developers in exploring a large, multi-repository codebase.

Below is a developer's question and a set of relevant content snippets retrieved from indexed files (code or documentation).
Each snippet includes optional metadata such as file paths to help you reference the source.

---

**Question:**
{question}

---

**Context:**
{context}

---

**Instructions:**

- Your response must be strictly grounded in the above context.
- DO NOT make assumptions or fabricate implementation details not present in the content.
- If the context includes partial logic, mention what's provided and what is not.
- If available, include relevant `file_path` references to help locate source files.
- Format your response with clear paragraphs or bullet points for readability.
- If the answer is not available in the context, reply exactly:
  **"The answer is not available in the indexed codebase."**

Be clear, friendly, and accurate — like an expert ChatGPT assistant who knows how to say “not enough info” when needed.
"""



    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini error: {e}"

# Run some questions
if __name__ == "__main__":
    questions = [
        "How many sub modules are in this project?",
        "Is there any code for embedding or chunking files?"
    ]

    for q in questions:
        print(f"\n🔍 Question: {q}")
        answer = query_all_namespaces(q, top_k=10, per_ns_k=3)  # 3 per ns × 10 ns = ~30 results to sort
        print(f"✅ Answer:\n{answer}")

