"""
Agentic Search System for CodeChat
More intelligent, adaptive approach to code search and understanding
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

class QueryType(Enum):
    CONCEPTUAL = "conceptual"  # "what is this about?"
    FUNCTIONAL = "functional"  # "how does this work?"
    EXAMPLE = "example"        # "show me examples"
    COMPARISON = "comparison"  # "compare A vs B"
    DEBUGGING = "debugging"    # "why doesn't this work?"

@dataclass
class SearchResult:
    content: str
    source: str
    confidence: float
    reasoning: str
    relationships: List[str]

class QueryAnalysisAgent:
    """Analyzes queries to determine search strategy"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def analyze_query(self, query: str, context: Dict) -> Dict[str, Any]:
        """Determine query type and optimal search strategy"""
        
        analysis_prompt = f"""
        Analyze this code-related query and determine the best search strategy:
        
        Query: "{query}"
        Context: {context}
        
        Determine:
        1. Query type: conceptual, functional, example, comparison, or debugging
        2. Key entities mentioned (functions, classes, concepts)
        3. Scope: single file, module, or cross-cutting
        4. Complexity: simple lookup or complex analysis needed
        5. Best search strategies to use (vector, structural, example, graph)
        
        Return JSON with analysis.
        """
        
        response = self.llm.generate_content(analysis_prompt)
        return json.loads(response.text)

class StructuralSearchAgent:
    """Searches based on code structure and relationships"""
    
    def __init__(self, dependency_graph, ast_parser):
        self.dep_graph = dependency_graph
        self.ast_parser = ast_parser
    
    def search(self, entities: List[str], scope: str) -> List[SearchResult]:
        """Find code based on structural relationships"""
        results = []
        
        for entity in entities:
            # Find in dependency graph
            related = self.dep_graph.find_related(entity)
            
            # Find in AST
            definitions = self.ast_parser.find_definitions(entity)
            usages = self.ast_parser.find_usages(entity)
            
            results.extend(self.format_structural_results(
                entity, related, definitions, usages
            ))
        
        return results

class ExampleSearchAgent:
    """Finds examples and usage patterns"""
    
    def search(self, query: str, entities: List[str]) -> List[SearchResult]:
        """Find examples of how code is used"""
        results = []
        
        # Look for test files
        test_examples = self.find_test_examples(entities)
        
        # Look for documentation examples
        doc_examples = self.find_doc_examples(entities)
        
        # Look for usage patterns in codebase
        usage_patterns = self.find_usage_patterns(entities)
        
        return results

class SemanticFusionAgent:
    """Combines results from multiple search strategies"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def fuse_results(
        self, 
        query: str,
        vector_results: List[SearchResult],
        structural_results: List[SearchResult],
        example_results: List[SearchResult]
    ) -> List[SearchResult]:
        """Intelligently combine and rank results from different agents"""
        
        fusion_prompt = f"""
        You are combining search results from different strategies for this query: "{query}"
        
        Vector Search Results (semantic similarity):
        {self.format_results(vector_results)}
        
        Structural Search Results (code relationships):
        {self.format_results(structural_results)}
        
        Example Search Results (usage patterns):
        {self.format_results(example_results)}
        
        Intelligently combine these results:
        1. Remove duplicates and near-duplicates
        2. Rank by relevance to the query
        3. Ensure diverse perspectives are included
        4. Provide reasoning for ranking decisions
        
        Return the top 10 most relevant results with explanations.
        """
        
        response = self.llm.generate_content(fusion_prompt)
        return self.parse_fused_results(response.text)

class AdaptiveLearningAgent:
    """Learns from user interactions to improve search"""
    
    def __init__(self):
        self.interaction_history = []
        self.strategy_performance = {}
    
    def record_interaction(
        self, 
        query: str, 
        results: List[SearchResult], 
        user_feedback: Optional[str] = None
    ):
        """Record user interaction for learning"""
        interaction = {
            'query': query,
            'results': results,
            'feedback': user_feedback,
            'timestamp': self.get_timestamp()
        }
        self.interaction_history.append(interaction)
        self.update_strategy_weights(interaction)
    
    def get_personalized_weights(self, user_context: Dict) -> Dict[str, float]:
        """Get personalized search strategy weights"""
        # Analyze user's typical queries and preferences
        # Return weights for different search strategies
        return {
            'vector_search': 0.4,
            'structural_search': 0.3,
            'example_search': 0.2,
            'graph_search': 0.1
        }

class AgenticSearchOrchestrator:
    """Main orchestrator for agentic search system"""
    
    def __init__(self, llm_client, vector_index, dependency_graph):
        self.query_analyzer = QueryAnalysisAgent(llm_client)
        self.structural_agent = StructuralSearchAgent(dependency_graph, None)
        self.example_agent = ExampleSearchAgent()
        self.fusion_agent = SemanticFusionAgent(llm_client)
        self.learning_agent = AdaptiveLearningAgent()
        
        self.vector_index = vector_index
        self.llm = llm_client
    
    async def search(
        self, 
        query: str, 
        context: Dict,
        user_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Execute agentic search with multiple strategies"""
        
        # 1. Analyze query to determine strategy
        analysis = self.query_analyzer.analyze_query(query, context)
        
        # 2. Get personalized weights
        weights = self.learning_agent.get_personalized_weights(user_profile or {})
        
        # 3. Execute multiple search strategies in parallel
        vector_results = await self.vector_search(query, analysis)
        structural_results = await self.structural_agent.search(
            analysis.get('entities', []), 
            analysis.get('scope', 'module')
        )
        example_results = await self.example_agent.search(
            query, 
            analysis.get('entities', [])
        )
        
        # 4. Fuse results intelligently
        final_results = self.fusion_agent.fuse_results(
            query, vector_results, structural_results, example_results
        )
        
        # 5. Generate contextual explanation
        explanation = self.generate_explanation(query, final_results, analysis)
        
        return {
            'results': final_results,
            'explanation': explanation,
            'query_analysis': analysis,
            'search_strategies_used': weights
        }
    
    def generate_explanation(
        self, 
        query: str, 
        results: List[SearchResult],
        analysis: Dict
    ) -> str:
        """Generate explanation of search process and results"""
        
        explanation_prompt = f"""
        Explain the search process and results for this query: "{query}"
        
        Query Analysis: {analysis}
        
        Results Found:
        {self.format_results(results)}
        
        Provide a clear explanation of:
        1. How you interpreted the query
        2. What search strategies were used and why
        3. Key insights from the results
        4. How the results answer the original query
        5. Suggestions for follow-up questions
        """
        
        response = self.llm.generate_content(explanation_prompt)
        return response.text

# Usage Example:
"""
# Replace simple vector search with agentic search
agentic_search = AgenticSearchOrchestrator(llm_client, vector_index, dep_graph)

results = await agentic_search.search(
    query="How does the chunking system work?",
    context={'repo': 'codechat', 'user_role': 'developer'},
    user_profile={'experience_level': 'intermediate'}
)

# Results include:
# - Multiple perspectives (vector, structural, examples)
# - Intelligent fusion and ranking
# - Contextual explanations
# - Learning from interactions
"""