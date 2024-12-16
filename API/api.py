from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from API.model_integration import generate_answer, create_vector_store  # Import updated functions

# Initialize the FastAPI application
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Define the input data model for the query endpoint
class QueryRequest(BaseModel):
    question: str  # The question input by the user

# Define the response data model for the query endpoint
class QueryResponse(BaseModel):
    answer: str  # The generated answer from the model

# Define the response data model for the vector store creation endpoint
class VectorStoreResponse(BaseModel):
    message: str  # Success or error message

# Define the API endpoint for generating answers
@app.post("/query", response_model=QueryResponse)
async def get_answer(query: QueryRequest):
    """
    Takes the question and returns the answer
    """
    try:
        # Call the model integration to generate an answer
        answer = generate_answer(query.question)
        return QueryResponse(answer=answer)
    except RuntimeError as e:
        # If the vector store has not been created
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # If another error occurs, return a 500 error
        raise HTTPException(status_code=500, detail="Error generating answer")

# Define the API endpoint for creating the vector store
@app.post("/vector_store", response_model=VectorStoreResponse)
async def create_vector_store_endpoint():
    """
    Preprocesses documents and creates the vector store
    """
    try:
        # Call the function to create a vector store
        create_vector_store()
        return VectorStoreResponse(message="Vector store created successfully.")
    except ValueError as e:
        # If an error occurs during preprocessing or chunking
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # If another error occurs, return a 500 error
        raise HTTPException(status_code=500, detail=f"Error creating vector store: {str(e)}")
