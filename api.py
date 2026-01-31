from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from answer_generator import AnswerGenerator
from config import API_HOST, API_PORT
import uvicorn

# Initialize FastAPI
app = FastAPI(
    title="RAG Support Bot API",
    description="Q&A bot using Retrieval Augmented Generation",
    version="1.0.0"
)

# Initialize answer generator
generator = AnswerGenerator()

# Request/Response models
class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]
    context_used: List[str]

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "message": "RAG Support Bot API is running!",
        "endpoints": {
            "ask": "/ask",
            "health": "/health"
        }
    }

@app.get("/health")
async def health():
    """Check if system is ready"""
    try:
        count = generator.retriever.collection.count()
        return {
            "status": "healthy",
            "chunks_in_database": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question and get an answer based on crawled documentation
    """
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Generate answer
        result = generator.generate_answer(request.question)
        
        return AnswerResponse(
            question=request.question,
            answer=result['answer'],
            sources=result['sources'],
            context_used=result['context_used']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    count = generator.retriever.collection.count()
    return {
        "total_chunks": count,
        "collection_name": generator.retriever.collection.name
    }


def main():
    """Run the API server"""
    print(f"""
    🚀 Starting RAG Support Bot API...
    
    📍 API will be available at:
       - Local: http://localhost:{API_PORT}
       - Docs: http://localhost:{API_PORT}/docs
    
    Press Ctrl+C to stop
    """)
    
    uvicorn.run(app, host=API_HOST, port=API_PORT)


if __name__ == "__main__":
    main()