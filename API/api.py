from model_integration import IntegratedRAGService
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel



class Question(BaseModel):
    text: str

app = FastAPI()


# Create a global service instance
rag_service = IntegratedRAGService()


@app.post("/start_monitoring")
async def start_monitoring():
    """Start monitoring Google Drive for changes."""
    rag_service.start_monitoring()
    return {"message": "Monitoring started successfully"}

@app.post("/stop_monitoring")
async def stop_monitoring():
    """Stop monitoring Google Drive for changes."""
    rag_service.stop_monitoring()
    return {"message": "Monitoring stopped successfully"}

@app.post("/ask")
async def ask_question(question: Question):
    """Ask a question to the RAG system."""
    try:
        answer = rag_service.generate_answer(question.text)
        return {"answer": answer}
    except RuntimeError as e:
        return {"error": str(e)}

@app.get("/status")
async def get_status():
    """Get the current status of the RAG system."""
    return {
        "is_monitoring": rag_service.is_monitoring,
        "vector_store_exists": rag_service.vector_store is not None,
        "known_files_count": len(rag_service.known_files),
        "last_update": rag_service.last_update_time.isoformat() if rag_service.last_update_time else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)