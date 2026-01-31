from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from typing import List, Dict
from config import (
    EMBEDDING_MODEL,
    COLLECTION_NAME,
    PERSIST_DIRECTORY
)

class DocumentRetriever:
    def __init__(self):
        print("🔄 Loading retriever...")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Connect to existing ChromaDB
        self.client = chromadb.Client(Settings(
            persist_directory=PERSIST_DIRECTORY,
            anonymized_telemetry=False
        ))
        
        self.collection = self.client.get_collection(COLLECTION_NAME)
        print(f"✅ Connected to collection with {self.collection.count()} chunks")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant document chunks"""
        print(f"\n🔍 Searching for: '{query}'")
        
        # Generate query embedding
        query_embedding = self.model.encode(query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        # Format results
        formatted_results = []
        
        if results['documents'] and results['documents'][0]:
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                formatted_results.append({
                    'rank': i + 1,
                    'content': doc,
                    'source_url': metadata['source_url'],
                    'title': metadata['title'],
                    'relevance_score': 1 - distance  # Convert distance to similarity
                })
        
        print(f"✅ Found {len(formatted_results)} relevant chunks\n")
        
        return formatted_results
    
    def print_results(self, results: List[Dict]):
        """Pretty print search results"""
        for result in results:
            print(f"Rank {result['rank']} | Score: {result['relevance_score']:.3f}")
            print(f"Source: {result['title']}")
            print(f"URL: {result['source_url']}")
            print(f"Content: {result['content'][:200]}...")
            print("-" * 80)


def main():
    """Test the retriever"""
    retriever = DocumentRetriever()
    
    # Test queries
    test_queries = [
        "How do I install Python?",
        "What are functions?",
        "How to use loops?"
    ]
    
    for query in test_queries:
        results = retriever.search(query, top_k=3)
        retriever.print_results(results)
        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()