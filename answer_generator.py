from retriever import DocumentRetriever
from typing import List, Dict

class AnswerGenerator:
    def __init__(self):
        self.retriever = DocumentRetriever()
    
    def generate_answer(self, question: str) -> Dict:
        """Generate answer from retrieved context"""
        # Retrieve relevant chunks
        results = self.retriever.search(question, top_k=3)
        
        if not results:
            return {
                'answer': "I couldn't find relevant information to answer this question.",
                'sources': [],
                'context_used': []
            }
        
        # Combine context
        context = "\n\n".join([
            f"[Source {i+1}]: {r['content']}" 
            for i, r in enumerate(results)
        ])
        
        # Simple rule-based answer (we'll use LLM in API)
        answer = self._create_answer(question, results)
        
        # Extract unique sources
        sources = list(set([r['source_url'] for r in results]))
        
        return {
            'answer': answer,
            'sources': sources,
            'context_used': [r['content'][:150] + '...' for r in results]
        }
    
    def _create_answer(self, question: str, results: List[Dict]) -> str:
        """Create answer from context (simplified version)"""
        # For now, return the most relevant chunk
        if results:
            return f"Based on the documentation:\n\n{results[0]['content'][:400]}..."
        return "No answer found."


def main():
    generator = AnswerGenerator()
    
    questions = [
        "How do I install Python?",
        "What are Python functions?",
    ]
    
    for question in questions:
        print(f"\n❓ Question: {question}")
        print("="*80)
        
        result = generator.generate_answer(question)
        
        print(f"\n💡 Answer:\n{result['answer']}")
        print(f"\n📚 Sources:")
        for source in result['sources']:
            print(f"  - {source}")
        print("\n" + "="*80)


if __name__ == "__main__":
    main()