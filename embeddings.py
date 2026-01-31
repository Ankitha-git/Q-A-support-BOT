import json
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from config import (
    EMBEDDING_MODEL, 
    CHUNK_SIZE, 
    CHUNK_OVERLAP,
    COLLECTION_NAME,
    PERSIST_DIRECTORY
)

class EmbeddingProcessor:
    def __init__(self):
        print("🔄 Loading embedding model...")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        print("✅ Model loaded!")
        
        # Initialize ChromaDB
        self.client = chromadb.Client(Settings(
            persist_directory=PERSIST_DIRECTORY,
            anonymized_telemetry=False
        ))
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(COLLECTION_NAME)
            print(f"📚 Using existing collection: {COLLECTION_NAME}")
        except:
            self.collection = self.client.create_collection(COLLECTION_NAME)
            print(f"📚 Created new collection: {COLLECTION_NAME}")
    
    def chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE, 
                   overlap: int = CHUNK_OVERLAP) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # At least 50% of chunk
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return [c for c in chunks if len(c) > 50]  # Filter tiny chunks
    
    def process_documents(self, documents: List[Dict]) -> int:
        """Process documents, create chunks, generate embeddings"""
        all_chunks = []
        all_metadatas = []
        all_ids = []
        
        chunk_id = 0
        
        for doc in documents:
            print(f"Processing: {doc['title'][:50]}...")
            
            # Create chunks
            chunks = self.chunk_text(doc['content'])
            
            for chunk in chunks:
                all_chunks.append(chunk)
                all_metadatas.append({
                    'source_url': doc['url'],
                    'title': doc['title'],
                    'chunk_index': len(all_chunks) - 1
                })
                all_ids.append(f"chunk_{chunk_id}")
                chunk_id += 1
        
        print(f"\n📊 Total chunks created: {len(all_chunks)}")
        print("🔄 Generating embeddings...")
        
        # Generate embeddings
        embeddings = self.model.encode(all_chunks, show_progress_bar=True)
        
        print("💾 Storing in vector database...")
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=all_chunks,
            metadatas=all_metadatas,
            ids=all_ids
        )
        
        print(f"✅ Stored {len(all_chunks)} chunks in database!")
        
        return len(all_chunks)
    
    def get_stats(self):
        """Get collection statistics"""
        count = self.collection.count()
        print(f"\n📊 Database Stats:")
        print(f"Total chunks: {count}")
        return count


def main():
    """Process crawled data and create embeddings"""
    # Load crawled data
    print("📖 Loading crawled data...")
    with open('crawled_data.json', 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    print(f"Found {len(documents)} documents\n")
    
    # Process and embed
    processor = EmbeddingProcessor()
    processor.process_documents(documents)
    processor.get_stats()


if __name__ == "__main__":
    main()