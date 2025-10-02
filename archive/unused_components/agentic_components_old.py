"""
Intelligent Repository-Specific Agentic Search Components for CodeChat
Performs targeted searches within specific GitHub repositories based on query intent
Enhanced with repository-aware search strategies - v3.0
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

class QueryType(Enum):
    CONCEPTUAL = "conceptual"      # "what is this about?"
    FUNCTIONAL = "functional"      # "how does this work?" 
    EXAMPLE = "example"           # "show me examples"
    COMPARISON = "comparison"     # "compare A vs B"
    DEBUGGING = "debugging"       # "why doesn't this work?"
    IMPLEMENTATION = "implementation"  # "how to implement X"
    FILE_SEARCH = "file_search"   # "find file X" or "where is Y"
    CODE_SEARCH = "code_search"   # "find function/class X"

@dataclass
class QueryAnalysis:
    query_type: QueryType
    entities: List[str]
    scope: str  # 'file', 'module', 'cross-cutting'
    complexity: str  # 'simple', 'medium', 'complex'
    intent_keywords: List[str]
    search_strategies: List[str]
    confidence: float
    specific_targets: List[str]  # Specific files, functions, classes mentioned
    repository_context: str     # Which repository is most relevant

class RepositoryIntelligentSearchAgent:
    """Performs intelligent, repository-aware searches based on query analysis"""
    
    def __init__(self, index, repo_namespace_map, bedrock_client, openai_client=None):
        self.index = index
        self.repo_namespace_map = repo_namespace_map
        self.bedrock_client = bedrock_client
        self.openai_client = openai_client
        
        # Repository-specific patterns and contexts
        self.repo_patterns = {
            "webroot": {
                "keywords": ["frontend", "web", "ui", "html", "css", "javascript", "components"],
                "file_types": [".html", ".css", ".js", ".md"],
                "structure_clues": ["components", "css", "js", "views", "pages"]
            },
            "localsite": {
                "keywords": ["local", "development", "setup", "configuration", "environment"],
                "file_types": [".py", ".md", ".json", ".yml", ".yaml"],
                "structure_clues": ["local", "dev", "config", "setup"]
            },
            "io": {
                "keywords": ["data", "io", "input", "output", "processing", "models"],
                "file_types": [".py", ".json", ".csv", ".md"],
                "structure_clues": ["data", "models", "io", "processing"]
            },
            "codechat": {
                "keywords": ["chat", "lambda", "api", "backend", "search", "embedding"],
                "file_types": [".py", ".md", ".json", ".tf"],
                "structure_clues": ["lambda", "backend", "api", "src"]
            }
        }

    def intelligent_repository_search(self, query: str, analysis: QueryAnalysis, target_namespaces: List[str]) -> List[Dict]:
        """Perform intelligent search targeted to specific repository contexts"""
        all_results = []
        
        for namespace in target_namespaces:
            if not namespace:
                continue
                
            # Get repository-specific search strategies
            repo_strategies = self._get_repository_strategies(namespace, analysis)
            
            # Execute targeted searches for this repository
            for strategy in repo_strategies:
                try:
                    results = self._execute_strategy(strategy, query, analysis, namespace)
                    if results:
                        # Mark results with strategy and repository context
                        for result in results:
                            result['search_strategy'] = strategy['name']
                            result['repository'] = namespace
                            result['strategy_confidence'] = strategy['confidence']
                        all_results.extend(results)
                except Exception as e:
                    print(f"Strategy {strategy['name']} failed for {namespace}: {e}")
                    continue
        
        return self._deduplicate_and_rank(all_results, analysis)

    def _get_repository_strategies(self, namespace: str, analysis: QueryAnalysis) -> List[Dict]:
        """Get repository-specific search strategies based on query analysis"""
        strategies = []
        repo_context = self.repo_patterns.get(namespace, {})
        
        # Strategy 1: Direct entity search (high priority for specific targets)
        if analysis.specific_targets:
            strategies.append({
                'name': 'direct_entity_search',
                'confidence': 0.9,
                'filters': self._build_entity_filters(analysis.specific_targets, repo_context),
                'query_expansion': analysis.specific_targets
            })
        
        # Strategy 2: Contextual keyword search
        contextual_keywords = self._extract_contextual_keywords(analysis, repo_context)
        if contextual_keywords:
            strategies.append({
                'name': 'contextual_search',
                'confidence': 0.8,
                'filters': self._build_contextual_filters(contextual_keywords, repo_context),
                'query_expansion': contextual_keywords
            })
        
        # Strategy 3: Repository-specific semantic search
        strategies.append({
            'name': 'semantic_repository_search',
            'confidence': 0.7,
            'filters': self._build_semantic_filters(analysis, repo_context),
            'query_expansion': repo_context.get('keywords', [])
        })
        
        # Strategy 4: File structure search (for file/path queries)
        if analysis.query_type == QueryType.FILE_SEARCH:
            strategies.append({
                'name': 'file_structure_search',
                'confidence': 0.95,
                'filters': self._build_file_structure_filters(analysis, repo_context),
                'query_expansion': []
            })
        
        return strategies

    def _execute_strategy(self, strategy: Dict, query: str, analysis: QueryAnalysis, namespace: str) -> List[Dict]:
        """Execute a specific search strategy"""
        strategy_name = strategy['name']
        
        if strategy_name == 'direct_entity_search':
            return self._direct_entity_search(query, analysis, namespace, strategy)
        elif strategy_name == 'contextual_search':
            return self._contextual_search(query, analysis, namespace, strategy)
        elif strategy_name == 'semantic_repository_search':
            return self._semantic_repository_search(query, analysis, namespace, strategy)
        elif strategy_name == 'file_structure_search':
            return self._file_structure_search(query, analysis, namespace, strategy)
        else:
            return []

    def _direct_entity_search(self, query: str, analysis: QueryAnalysis, namespace: str, strategy: Dict) -> List[Dict]:
        """Search for specific entities (functions, classes, files) mentioned in the query"""
        results = []
        
        for target in analysis.specific_targets:
            try:
                # Search for exact matches in file paths
                path_results = self.index.query(
                    vector=self._get_query_vector(f"{target} {query}"),
                    top_k=3,
                    include_metadata=True,
                    namespace=namespace,
                    filter={
                        "$or": [
                            {"file_path": {"$regex": f"(?i).*{re.escape(target)}.*"}},
                            {"chunk_content": {"$regex": f"(?i)\\b{re.escape(target)}\\b"}},
                            {"function_names": {"$in": [target]}},
                            {"class_names": {"$in": [target]}}
                        ]
                    }
                )
                if path_results and "matches" in path_results:
                    results.extend(path_results["matches"])
            except Exception as e:
                print(f"Direct entity search error for {target}: {e}")
                continue
        
        return results

    def _contextual_search(self, query: str, analysis: QueryAnalysis, namespace: str, strategy: Dict) -> List[Dict]:
        """Search using contextual keywords relevant to the repository"""
        contextual_query = f"{query} {' '.join(strategy.get('query_expansion', []))}"
        
        try:
            results = self.index.query(
                vector=self._get_query_vector(contextual_query),
                top_k=5,
                include_metadata=True,
                namespace=namespace,
                filter=strategy.get('filters', {})
            )
            return results.get("matches", []) if results else []
        except Exception as e:
            print(f"Contextual search error: {e}")
            return []

    def _semantic_repository_search(self, query: str, analysis: QueryAnalysis, namespace: str, strategy: Dict) -> List[Dict]:
        """Perform semantic search enhanced with repository-specific context"""
        repo_keywords = strategy.get('query_expansion', [])
        enhanced_query = f"{query} {' '.join(repo_keywords[:3])}"  # Limit to top 3 keywords
        
        try:
            results = self.index.query(
                vector=self._get_query_vector(enhanced_query),
                top_k=7,
                include_metadata=True,
                namespace=namespace,
                filter=strategy.get('filters', {})
            )
            return results.get("matches", []) if results else []
        except Exception as e:
            print(f"Semantic repository search error: {e}")
            return []

    def _file_structure_search(self, query: str, analysis: QueryAnalysis, namespace: str, strategy: Dict) -> List[Dict]:
        """Search specifically for files and directory structures"""
        file_patterns = []
        
        # Extract potential file names from query
        for entity in analysis.entities:
            if '.' in entity or '/' in entity:
                file_patterns.append(entity)
        
        if not file_patterns:
            # Look for common file indicators
            words = query.lower().split()
            for word in words:
                if any(ext in word for ext in ['.py', '.js', '.html', '.css', '.md', '.json']):
                    file_patterns.append(word)
        
        results = []
        for pattern in file_patterns:
            try:
                file_results = self.index.query(
                    vector=self._get_query_vector(f"file {pattern}"),
                    top_k=3,
                    include_metadata=True,
                    namespace=namespace,
                    filter={
                        "file_path": {"$regex": f"(?i).*{re.escape(pattern.replace('.', '\\.'))}.*"}
                    }
                )
                if file_results and "matches" in file_results:
                    results.extend(file_results["matches"])
            except Exception as e:
                print(f"File structure search error for {pattern}: {e}")
                continue
        
        return results

    def _extract_contextual_keywords(self, analysis: QueryAnalysis, repo_context: Dict) -> List[str]:
        """Extract keywords that are relevant to the specific repository context"""
        query_keywords = analysis.intent_keywords + analysis.entities
        repo_keywords = repo_context.get('keywords', [])
        
        # Find intersection and relevant combinations
        contextual = []
        for qkw in query_keywords:
            for rkw in repo_keywords:
                if qkw.lower() in rkw.lower() or rkw.lower() in qkw.lower():
                    contextual.append(rkw)
        
        # Add query type specific keywords
        if analysis.query_type == QueryType.EXAMPLE:
            contextual.extend(['example', 'demo', 'usage', 'how to'])
        elif analysis.query_type == QueryType.DEBUGGING:
            contextual.extend(['error', 'fix', 'debug', 'issue'])
        elif analysis.query_type == QueryType.IMPLEMENTATION:
            contextual.extend(['implement', 'create', 'build'])
        
        return list(set(contextual))

    def _build_entity_filters(self, entities: List[str], repo_context: Dict) -> Dict:
        """Build Pinecone filters for entity-specific searches"""
        filters = {"$or": []}
        
        for entity in entities:
            entity_filters = [
                {"file_path": {"$regex": f"(?i).*{re.escape(entity)}.*"}},
                {"chunk_content": {"$regex": f"(?i)\\b{re.escape(entity)}\\b"}}
            ]
            filters["$or"].extend(entity_filters)
        
        return filters

    def _build_contextual_filters(self, keywords: List[str], repo_context: Dict) -> Dict:
        """Build filters based on contextual keywords"""
        file_types = repo_context.get('file_types', [])
        
        filters = {}
        if file_types:
            filters["file_path"] = {"$regex": f"(?i).*({'|'.join(re.escape(ft) for ft in file_types)})$"}
        
        return filters

    def _build_semantic_filters(self, analysis: QueryAnalysis, repo_context: Dict) -> Dict:
        """Build filters for semantic searches based on repository structure"""
        filters = {}
        
        # Filter by file types relevant to the repository
        file_types = repo_context.get('file_types', [])
        if file_types:
            filters["file_path"] = {"$regex": f"(?i).*({'|'.join(re.escape(ft) for ft in file_types)})$"}
        
        # Add complexity-based filtering
        if analysis.complexity == 'simple':
            filters["code_complexity"] = {"$lt": 0.7}
        elif analysis.complexity == 'complex':
            filters["code_complexity"] = {"$gte": 0.7}
        
        return filters

    def _build_file_structure_filters(self, analysis: QueryAnalysis, repo_context: Dict) -> Dict:
        """Build filters specifically for file structure searches"""
        structure_clues = repo_context.get('structure_clues', [])
        
        filters = {"$or": []}
        for clue in structure_clues:
            filters["$or"].append({"file_path": {"$regex": f"(?i).*{re.escape(clue)}.*"}})
        
        return filters

    def _deduplicate_and_rank(self, results: List[Dict], analysis: QueryAnalysis) -> List[Dict]:
        """Remove duplicates and rank results based on repository intelligence"""
        # Remove duplicates by file path and line number
        seen = set()
        unique_results = []
        
        for result in results:
            metadata = result.get('metadata', {})
            key = f"{metadata.get('file_path', '')}:{metadata.get('line_start', 0)}"
            
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        # Rank by strategy confidence and relevance
        def rank_score(result):
            base_score = result.get('score', 0)
            strategy_confidence = result.get('strategy_confidence', 0.5)
            
            # Boost for direct entity matches
            if result.get('search_strategy') == 'direct_entity_search':
                return base_score * 1.5 * strategy_confidence
            
            # Boost for file structure matches when looking for files
            if (analysis.query_type == QueryType.FILE_SEARCH and 
                result.get('search_strategy') == 'file_structure_search'):
                return base_score * 1.4 * strategy_confidence
            
            return base_score * strategy_confidence
        
        return sorted(unique_results, key=rank_score, reverse=True)

    def _get_query_vector(self, query: str):
        """Get embedding vector for query"""
        if not self.openai_client:
            print("Warning: No OpenAI client available for embedding generation")
            return None
            
        try:
            embed_response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            return embed_response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding for query '{query}': {e}")
            return None


class QueryAnalysisAgent:
    """Enhanced query analysis with better entity extraction and repository awareness"""
    
    def __init__(self, bedrock_client):
        self.bedrock_client = bedrock_client
        
        # Enhanced patterns for better classification
        self.patterns = {
            QueryType.CONCEPTUAL: [
                r'\b(what is|describe|explain|overview|about|understand|concept)\b',
                r'\b(purpose|goal|meaning|definition)\b'
            ],
            QueryType.FUNCTIONAL: [
                r'\b(how does|how to|mechanism|process|work|function|operate)\b',
                r'\b(algorithm|logic|flow|procedure)\b'
            ],
            QueryType.EXAMPLE: [
                r'\b(example|sample|demo|show me|usage|demonstrate)\b',
                r'\b(how to use|implement|apply|tutorial)\b'
            ],
            QueryType.COMPARISON: [
                r'\b(compare|difference|vs|versus|better|alternative)\b',
                r'\b(option|choice|between|against)\b'
            ],
            QueryType.DEBUGGING: [
                r'\b(error|bug|issue|problem|fix|debug|troubleshoot)\b',
                r'\b(not working|broken|fails|wrong)\b'
            ],
            QueryType.IMPLEMENTATION: [
                r'\b(create|build|implement|add|develop|make)\b',
                r'\b(new feature|functionality|construct)\b'
            ],
            QueryType.FILE_SEARCH: [
                r'\b(find file|locate file|where is|file location)\b',
                r'\b(\.py|\.js|\.html|\.css|\.md|\.json)\b',
                r'\b(file|folder|directory|path)\b'
            ],
            QueryType.CODE_SEARCH: [
                r'\b(find function|find class|find method|locate code)\b',
                r'\b(function|class|method|variable|constant)\b'
            ]
        }

    def analyze_query(self, query: str, repository_context: str = None) -> QueryAnalysis:
        """Enhanced query analysis with repository awareness"""
        
        if not query or not isinstance(query, str):
            return QueryAnalysis(
                query_type=QueryType.CONCEPTUAL,
                entities=[],
                scope='file',
                complexity='simple',
                intent_keywords=[],
                search_strategies=['semantic_repository_search'],
                confidence=0.1,
                specific_targets=[],
                repository_context=repository_context or ''
            )
        
        query_lower = query.lower()
        
        try:
            # Enhanced classification
            query_type = self._classify_query_type(query_lower)
            entities = self._extract_enhanced_entities(query)
            specific_targets = self._extract_specific_targets(query)
            scope = self._determine_scope(query_lower, entities)
            complexity = self._assess_complexity(query, entities)
            intent_keywords = self._extract_intent_keywords(query_lower)
            search_strategies = self._determine_intelligent_strategies(query_type, scope, entities, specific_targets)
            
            return QueryAnalysis(
                query_type=query_type,
                entities=entities,
                scope=scope,
                complexity=complexity,
                intent_keywords=intent_keywords,
                search_strategies=search_strategies,
                confidence=0.9,
                specific_targets=specific_targets,
                repository_context=repository_context or ''
            )
        except Exception as e:
            print(f"Enhanced query analysis error: {e}")
            return QueryAnalysis(
                query_type=QueryType.CONCEPTUAL,
                entities=[],
                scope='file',
                complexity='simple',
                intent_keywords=[],
                search_strategies=['semantic_repository_search'],
                confidence=0.1,
                specific_targets=[],
                repository_context=repository_context or ''
            )

    def _extract_enhanced_entities(self, query: str) -> List[str]:
        """Enhanced entity extraction with better patterns"""
        entities = []
        
        # Enhanced patterns for different entity types
        patterns = [
            r'\b[A-Z][a-zA-Z]*(?:[A-Z][a-zA-Z]*)*\b',  # CamelCase (classes, components)
            r'\b[a-z_][a-z0-9_]*\(\)\b',  # function calls with parentheses
            r'\b[a-z_][a-z0-9_]*\b',  # snake_case variables/functions
            r'\b[A-Z_][A-Z0-9_]*\b',  # CONSTANTS
            r'[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*',  # method calls
            r'[a-zA-Z0-9_/.-]+\.[a-z]{2,4}',  # file names with extensions
            r'/[a-zA-Z0-9_/.-]+',  # file paths
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query)
            entities.extend(matches)
        
        # Filter out common words and very short entities
        common_words = {
            'the', 'and', 'or', 'but', 'how', 'what', 'why', 'where', 'when', 
            'this', 'that', 'with', 'for', 'from', 'can', 'you', 'me', 'it'
        }
        entities = [e.strip('()') for e in entities if len(e) > 2 and e.lower() not in common_words]
        
        return list(set(entities))

    def _extract_specific_targets(self, query: str) -> List[str]:
        """Extract specific files, functions, or classes that the user is looking for"""
        targets = []
        
        # Look for quoted entities (highest confidence)
        quoted_pattern = r'["\']([^"\']+)["\']'
        quoted_matches = re.findall(quoted_pattern, query)
        targets.extend(quoted_matches)
        
        # Look for file extensions (files)
        file_pattern = r'\b([a-zA-Z0-9_-]+\.[a-zA-Z]{2,4})\b'
        file_matches = re.findall(file_pattern, query)
        targets.extend(file_matches)
        
        # Look for function/method patterns
        func_patterns = [
            r'\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\)',
        ]
        for pattern in func_patterns:
            matches = re.findall(pattern, query)
            targets.extend(matches)
        
        # Look for class patterns
        class_patterns = [
            r'\bclass\s+([A-Z][a-zA-Z0-9_]*)',
            r'\b([A-Z][a-zA-Z]*(?:[A-Z][a-zA-Z]*)*)\b',  # CamelCase likely to be classes
        ]
        for pattern in class_patterns:
            matches = re.findall(pattern, query)
            targets.extend(matches)
        
        return list(set(targets))

    def _classify_query_type(self, query_lower: str) -> QueryType:
        """Enhanced query type classification"""
        scores = {}
        
        for query_type, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower))
                score += matches
            scores[query_type] = score
        
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                return max(scores.items(), key=lambda x: x[1])[0]
        
        # Default classification based on content
        if any(word in query_lower for word in ['find', 'locate', 'where']):
            if any(ext in query_lower for ext in ['.py', '.js', '.html', '.css', '.md']):
                return QueryType.FILE_SEARCH
            else:
                return QueryType.CODE_SEARCH
        
        return QueryType.CONCEPTUAL

    def _determine_scope(self, query_lower: str, entities: List[str]) -> str:
        """Determine query scope based on content and entities"""
        if any(word in query_lower for word in ['architecture', 'system', 'project', 'repository']):
            return 'cross-cutting'
        elif any(word in query_lower for word in ['module', 'package', 'component']):
            return 'module'
        elif len(entities) == 1 and any(word in query_lower for word in ['function', 'method', 'class']):
            return 'file'
        elif len(entities) > 3:
            return 'cross-cutting'
        else:
            return 'module'

    def _assess_complexity(self, query: str, entities: List[str]) -> str:
        """Assess query complexity with better heuristics"""
        word_count = len(query.split())
        entity_count = len(entities)
        
        # Simple: short query, few entities, basic keywords
        if word_count <= 5 and entity_count <= 1:
            return 'simple'
        
        # Complex: long query, many entities, complex patterns
        elif word_count > 15 or entity_count > 4:
            return 'complex'
        
        # Medium: everything else
        else:
            return 'medium'

    def _extract_intent_keywords(self, query_lower: str) -> List[str]:
        """Extract enhanced intent keywords"""
        intent_words = []
        
        # Technical terms
        tech_terms = [
            'function', 'class', 'method', 'variable', 'import', 'module',
            'api', 'endpoint', 'database', 'query', 'response', 'request',
            'test', 'debug', 'error', 'exception', 'config', 'setup',
            'component', 'service', 'model', 'view', 'controller',
            'authentication', 'authorization', 'validation', 'form',
            'frontend', 'backend', 'client', 'server', 'middleware'
        ]
        
        for term in tech_terms:
            if term in query_lower:
                intent_words.append(term)
        
        return intent_words

    def _determine_intelligent_strategies(self, query_type: QueryType, scope: str, entities: List[str], specific_targets: List[str]) -> List[str]:
        """Determine intelligent search strategies based on enhanced analysis"""
        strategies = []
        
        # Always start with repository-aware semantic search
        strategies.append('semantic_repository_search')
        
        # Add specific strategies based on query type
        if specific_targets:
            strategies.insert(0, 'direct_entity_search')  # Highest priority
        
        if query_type == QueryType.FILE_SEARCH:
            strategies.insert(0, 'file_structure_search')
        elif query_type == QueryType.CODE_SEARCH:
            strategies.append('direct_entity_search')
        elif query_type in [QueryType.FUNCTIONAL, QueryType.IMPLEMENTATION]:
            strategies.append('contextual_search')
        elif query_type == QueryType.EXAMPLE:
            strategies.append('contextual_search')
        elif query_type == QueryType.DEBUGGING:
            strategies.append('contextual_search')
        
        # Add contextual search for multi-entity queries
        if len(entities) > 1:
            strategies.append('contextual_search')
        
        return strategies
                matches = len(re.findall(pattern, query_lower))
                score += matches
            scores[query_type] = score
        
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                return max(scores.items(), key=lambda x: x[1])[0]
        
        # Default classification based on content
        if any(word in query_lower for word in ['find', 'locate', 'where']):
            if any(ext in query_lower for ext in ['.py', '.js', '.html', '.css', '.md']):
                return QueryType.FILE_SEARCH
            else:
                return QueryType.CODE_SEARCH
        
        return QueryType.CONCEPTUAL

    def _determine_scope(self, query_lower: str, entities: List[str]) -> str:
        """Determine query scope based on content and entities"""
        if any(word in query_lower for word in ['architecture', 'system', 'project', 'repository']):
            return 'cross-cutting'
        elif any(word in query_lower for word in ['module', 'package', 'component']):
            return 'module'
        elif len(entities) == 1 and any(word in query_lower for word in ['function', 'method', 'class']):
            return 'file'
        elif len(entities) > 3:
            return 'cross-cutting'
        else:
            return 'module'

    def _assess_complexity(self, query: str, entities: List[str]) -> str:
        """Assess query complexity with better heuristics"""
        word_count = len(query.split())
        entity_count = len(entities)
        
        # Simple: short query, few entities, basic keywords
        if word_count <= 5 and entity_count <= 1:
            return 'simple'
        
        # Complex: long query, many entities, complex patterns
        elif word_count > 15 or entity_count > 4:
            return 'complex'
        
        # Medium: everything else
        else:
            return 'medium'

    def _extract_intent_keywords(self, query_lower: str) -> List[str]:
        """Extract enhanced intent keywords"""
        intent_words = []
        
        # Technical terms
        tech_terms = [
            'function', 'class', 'method', 'variable', 'import', 'module',
            'api', 'endpoint', 'database', 'query', 'response', 'request',
            'test', 'debug', 'error', 'exception', 'config', 'setup',
            'component', 'service', 'model', 'view', 'controller',
            'authentication', 'authorization', 'validation', 'form',
            'frontend', 'backend', 'client', 'server', 'middleware'
        ]
        
        for term in tech_terms:
            if term in query_lower:
                intent_words.append(term)
        
        return intent_words

    def _determine_intelligent_strategies(self, query_type: QueryType, scope: str, entities: List[str], specific_targets: List[str]) -> List[str]:
        """Determine intelligent search strategies based on enhanced analysis"""
        strategies = []
        
        # Always start with repository-aware semantic search
        strategies.append('semantic_repository_search')
        
        # Add specific strategies based on query type
        if specific_targets:
            strategies.insert(0, 'direct_entity_search')  # Highest priority
        
        if query_type == QueryType.FILE_SEARCH:
            strategies.insert(0, 'file_structure_search')
        elif query_type == QueryType.CODE_SEARCH:
            strategies.append('direct_entity_search')
        elif query_type in [QueryType.FUNCTIONAL, QueryType.IMPLEMENTATION]:
            strategies.append('contextual_search')
        elif query_type == QueryType.EXAMPLE:
            strategies.append('contextual_search')
        elif query_type == QueryType.DEBUGGING:
            strategies.append('contextual_search')
        
        # Add contextual search for multi-entity queries
        if len(entities) > 1:
            strategies.append('contextual_search')
        
        return strategies
            intent_keywords = self._extract_intent_keywords(query_lower)
            
            return QueryAnalysis(
                query_type=query_type,
                entities=entities,
                scope=scope,
                complexity=complexity,
                intent_keywords=intent_keywords,
                search_strategies=search_strategies,
                confidence=0.8  # Pattern-based has decent confidence
            )
        except Exception as e:
            print(f"Query analysis error: {e}")
            # Return safe fallback
            return QueryAnalysis(
                query_type=QueryType.CONCEPTUAL,
                entities=[],
                scope='file',
                complexity='simple',
                intent_keywords=[],
                search_strategies=['documentation_search'],
                confidence=0.1
            )
    
    def _classify_query_type(self, query_lower: str) -> QueryType:
        """Classify query type using pattern matching"""
        scores = {}
        
        for query_type, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    score += 1
            scores[query_type] = score
        
        # Return highest scoring type, default to CONCEPTUAL
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return QueryType.CONCEPTUAL
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract potential code entities from query"""
        entities = []
        
        # Look for code-like terms
        code_patterns = [
            r'\b[A-Z][a-zA-Z]*\b',  # CamelCase (classes)
            r'\b[a-z_][a-z0-9_]*\(\)\b',  # function calls
            r'\b[a-z_][a-z0-9_]*\b',  # snake_case variables/functions
            r'\.[a-z]+$',  # file extensions
            r'/[a-zA-Z0-9_/]+',  # file paths
        ]
        
        for pattern in code_patterns:
            matches = re.findall(pattern, query)
            entities.extend(matches)
        
        # Remove common words
        common_words = {'the', 'and', 'or', 'but', 'how', 'what', 'why', 'where', 'when'}
        entities = [e for e in entities if e.lower() not in common_words]
        
        return list(set(entities))  # Remove duplicates
    
    def _determine_scope(self, query_lower: str) -> str:
        """Determine the scope of the query"""
        for scope, patterns in self.scope_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return scope
        return 'module'  # Default scope
    
    def _assess_complexity(self, query: str, entities: List[str]) -> str:
        """Assess query complexity"""
        # Simple heuristics
        if len(query.split()) <= 5 and len(entities) <= 1:
            return 'simple'
        elif len(query.split()) <= 15 and len(entities) <= 3:
            return 'medium'
        else:
            return 'complex'
    
    def _determine_search_strategies(self, query_type: QueryType, scope: str, complexity: str) -> List[str]:
        """Determine which search strategies to use"""
        strategies = ['vector']  # Always include vector search
        
        if query_type == QueryType.FUNCTIONAL:
            strategies.extend(['structural', 'documentation'])
        elif query_type == QueryType.EXAMPLE:
            strategies.extend(['examples', 'tests'])
        elif query_type == QueryType.CONCEPTUAL:
            strategies.extend(['documentation', 'overview'])
        elif query_type == QueryType.DEBUGGING:
            strategies.extend(['tests', 'issues'])
        elif query_type == QueryType.IMPLEMENTATION:
            strategies.extend(['structural', 'examples'])
        
        if scope == 'cross-cutting':
            strategies.append('architectural')
        
        return strategies
    
    def _extract_intent_keywords(self, query_lower: str) -> List[str]:
        """Extract keywords that indicate user intent"""
        intent_words = []
        
        # Programming-specific terms
        prog_terms = [
            'function', 'class', 'method', 'variable', 'import', 'module',
            'api', 'endpoint', 'database', 'query', 'response', 'request',
            'test', 'debug', 'error', 'exception', 'config', 'setup'
        ]
        
        for term in prog_terms:
            if term in query_lower:
                intent_words.append(term)
        
        return intent_words

class MultiModalSearchAgent:
    """Performs different types of searches based on query analysis"""
    
    def __init__(self, index, repo_namespace_map, bedrock_client, openai_client=None):
        self.index = index
        self.repo_namespace_map = repo_namespace_map
        self.bedrock_client = bedrock_client
        self.openai_client = openai_client
    
    def documentation_search(self, matches: List[Dict]) -> List[Dict]:
        """Apply documentation boost to existing matches"""
        for match in matches:
            metadata = match.get('metadata', {})
            file_path = metadata.get('file_path', '').lower()
            
            # Boost documentation files
            if any(doc_indicator in file_path for doc_indicator in ['readme', 'doc', '.md']):
                match['score'] = match.get('score', 0) * 1.3
                match['documentation_boost'] = True
            
            # Boost chunks with good documentation
            if metadata.get('has_docstring', False):
                match['score'] = match.get('score', 0) * 1.1
                match['docstring_boost'] = True
        
        return matches
    
    def example_search(self, matches: List[Dict]) -> List[Dict]:
        """Apply example boost to existing matches"""
        for match in matches:
            metadata = match.get('metadata', {})
            file_path = metadata.get('file_path', '').lower()
            
            # Boost test and example files
            if any(example_indicator in file_path for example_indicator in ['test', 'example', 'demo', 'sample']):
                match['score'] = match.get('score', 0) * 1.2
                match['example_boost'] = True
            
            # Boost chunks that look like examples
            chunk_content = metadata.get('chunk_content', '').lower()
            if any(keyword in chunk_content for keyword in ['example', 'usage', 'how to', 'demo']):
                match['score'] = match.get('score', 0) * 1.1
                match['usage_boost'] = True
        
        return matches
    
    def search_documentation(self, query: str, entities: List[str], namespaces: List[str]) -> List[Dict]:
        """Search for documentation and README content"""
        results = []
        
        for namespace in namespaces:
            try:
                # Use metadata filtering to prioritize documentation
                doc_results = self.index.query(
                    vector=self._get_query_vector(query),
                    top_k=3,
                    include_metadata=True,
                    namespace=namespace,
                    filter={
                        "$or": [
                            {"file_path": {"$regex": "(?i)readme"}},
                            {"file_path": {"$regex": "(?i)doc"}},
                            {"chunk_type": {"$in": ["markdown", "comment", "docstring"]}}
                        ]
                    }
                )
                results.extend(doc_results.get("matches", []))
            except Exception as e:
                print(f"Documentation search error in {namespace}: {e}")
                continue
        
        return results
    
    def search_examples(self, query: str, entities: List[str], namespaces: List[str]) -> List[Dict]:
        """Search for examples and usage patterns"""
        results = []
        
        # Look for test files and example usage
        for namespace in namespaces:
            try:
                example_results = self.index.query(
                    vector=self._get_query_vector(f"example usage {query}"),
                    top_k=3,
                    include_metadata=True,
                    namespace=namespace,
                    filter={
                        "$or": [
                            {"file_path": {"$regex": "(?i)test"}},
                            {"file_path": {"$regex": "(?i)example"}},
                            {"file_path": {"$regex": "(?i)demo"}},
                            {"chunk_type": {"$eq": "test_case"}}
                        ]
                    }
                )
                results.extend(example_results.get("matches", []))
            except Exception as e:
                print(f"Example search error in {namespace}: {e}")
                continue
        
        return results
    
    def search_structural(self, query: str, entities: List[str], namespaces: List[str]) -> List[Dict]:
        """Search based on code structure and relationships"""
        results = []
        
        # Search for class definitions, function definitions, imports
        for entity in entities:
            for namespace in namespaces:
                try:
                    structural_results = self.index.query(
                        vector=self._get_query_vector(f"definition implementation {entity}"),
                        top_k=2,
                        include_metadata=True,
                        namespace=namespace,
                        filter={
                            "$or": [
                                {"chunk_type": {"$in": ["class_definition", "function_definition"]}},
                                {"tags": {"$in": ["definition", "implementation", "interface"]}}
                            ]
                        }
                    )
                    results.extend(structural_results.get("matches", []))
                except Exception as e:
                    print(f"Structural search error for {entity} in {namespace}: {e}")
                    continue
        
        return results
    
    def search_architectural(self, query: str, namespaces: List[str]) -> List[Dict]:
        """Search for architectural and overview information"""
        results = []
        
        # Look for high-level architectural components
        arch_queries = [
            f"architecture overview {query}",
            f"system design {query}",
            f"project structure {query}"
        ]
        
        for arch_query in arch_queries:
            for namespace in namespaces:
                try:
                    arch_results = self.index.query(
                        vector=self._get_query_vector(arch_query),
                        top_k=2,
                        include_metadata=True,
                        namespace=namespace,
                        filter={
                            "$or": [
                                {"file_path": {"$regex": "(?i)(main|index|app|core|config)"}},
                                {"centrality_score": {"$gte": 0.7}},
                                {"chunk_type": {"$in": ["module_header", "main_function"]}}
                            ]
                        }
                    )
                    results.extend(arch_results.get("matches", []))
                except Exception as e:
                    print(f"Architectural search error in {namespace}: {e}")
                    continue
        
        return results[:5]  # Limit architectural results
    
    def _get_query_vector(self, query: str):
        """Get embedding vector for query"""
        if not self.openai_client:
            print("Warning: No OpenAI client available for embedding generation")
            return None
            
        try:
            embed_response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            return embed_response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding for query '{query}': {e}")
            return None

class ResultFusionAgent:
    """Intelligently combines and ranks results from multiple search strategies"""
    
    def __init__(self, bedrock_client):
        self.bedrock_client = bedrock_client
    
    def fuse_results(
        self,
        query: str,
        analysis: QueryAnalysis,
        vector_results: List[Dict],
        doc_results: List[Dict] = None,
        example_results: List[Dict] = None,
        structural_results: List[Dict] = None,
        architectural_results: List[Dict] = None
    ) -> Tuple[List[Dict], str]:
        """Fuse results from multiple search strategies"""
        
        all_results = []
        strategy_info = []
        
        # Add vector results with source annotation
        for result in vector_results or []:
            result['search_strategy'] = 'vector'
            all_results.append(result)
        strategy_info.append(f"Vector search: {len(vector_results or [])} results")
        
        # Add documentation results with higher weight for conceptual queries
        if doc_results:
            weight = 1.2 if analysis.query_type == QueryType.CONCEPTUAL else 1.0
            for result in doc_results:
                result['search_strategy'] = 'documentation'
                result['fusion_weight'] = weight
                all_results.append(result)
            strategy_info.append(f"Documentation search: {len(doc_results)} results")
        
        # Add example results with higher weight for example queries
        if example_results:
            weight = 1.3 if analysis.query_type == QueryType.EXAMPLE else 1.0
            for result in example_results:
                result['search_strategy'] = 'examples'
                result['fusion_weight'] = weight
                all_results.append(result)
            strategy_info.append(f"Example search: {len(example_results)} results")
        
        # Add structural results with higher weight for functional queries
        if structural_results:
            weight = 1.2 if analysis.query_type == QueryType.FUNCTIONAL else 1.0
            for result in structural_results:
                result['search_strategy'] = 'structural'
                result['fusion_weight'] = weight
                all_results.append(result)
            strategy_info.append(f"Structural search: {len(structural_results)} results")
        
        # Add architectural results
        if architectural_results:
            for result in architectural_results:
                result['search_strategy'] = 'architectural'
                result['fusion_weight'] = 1.1
                all_results.append(result)
            strategy_info.append(f"Architectural search: {len(architectural_results)} results")
        
        # Remove duplicates based on content similarity
        unique_results = self._deduplicate_results(all_results)
        
        # Rank results based on multiple factors
        ranked_results = self._rank_results(unique_results, analysis)
        
        # Generate fusion explanation
        fusion_explanation = self._generate_fusion_explanation(query, analysis, strategy_info, len(ranked_results))
        
        return ranked_results, fusion_explanation
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on file path and content similarity"""
        seen_files = set()
        unique_results = []
        
        for result in results:
            file_path = result.get('metadata', {}).get('file_path', '')
            line_start = result.get('metadata', {}).get('line_start', 0)
            
            # Create a unique identifier for the chunk
            chunk_id = f"{file_path}:{line_start}"
            
            if chunk_id not in seen_files:
                seen_files.add(chunk_id)
                unique_results.append(result)
        
        return unique_results
    
    def _rank_results(self, results: List[Dict], analysis: QueryAnalysis) -> List[Dict]:
        """Rank results based on multiple factors"""
        
        def calculate_score(result):
            base_score = result.get('score', 0)
            fusion_weight = result.get('fusion_weight', 1.0)
            
            # Boost based on metadata quality
            metadata = result.get('metadata', {})
            quality_boost = 0
            
            if metadata.get('has_docstring', False):
                quality_boost += 0.1
            if metadata.get('centrality_score', 0) > 0.5:
                quality_boost += 0.05
            if metadata.get('docstring_quality', 0) > 0.7:
                quality_boost += 0.05
            
            # Penalize high complexity for simple queries
            if analysis.complexity == 'simple' and metadata.get('code_complexity', 0) > 0.8:
                quality_boost -= 0.1
            
            return (base_score * fusion_weight) + quality_boost
        
        # Sort by calculated score
        return sorted(results, key=calculate_score, reverse=True)
    
    def _generate_fusion_explanation(
        self, 
        query: str, 
        analysis: QueryAnalysis, 
        strategy_info: List[str],
        result_count: int
    ) -> str:
        """Generate explanation of the search process"""
        
        explanation = f"""
🔍 **Agentic Search Analysis for:** "{query}"

**Query Understanding:**
- Type: {analysis.query_type.value.title()}
- Scope: {analysis.scope}
- Complexity: {analysis.complexity}
- Key entities: {', '.join(analysis.entities) if analysis.entities else 'None detected'}

**Search Strategies Used:**
{chr(10).join(f"• {info}" for info in strategy_info)}

**Result Fusion:**
- Combined {result_count} unique results from multiple search strategies
- Ranked by relevance, quality metrics, and query-specific weights
- Prioritized {analysis.query_type.value} content based on query type
"""
        return explanation