from llm.utils import get_vector_store, get_conversation_chain
from Loading.load_and_chunk import load_chunk_files_from_directory
from embedding.embedding_generator import dataPreprocessing
import os

# Global variable to hold the vector store
vector_store = None

# Initialize the Hugging Face inference client
client = InferenceClient("meta-llama/Meta-Llama-3-8B-Instruct") # use public model only

def create_vector_store():
    """
    Initializes the vector store by processing documents in the specified folder.
    - Loads and chunks documents using a custom function.
    - Creates the vector store from the processed chunks.
    """
    global vector_store
    # Load and chunk documents from the directory
    text_chunks = load_chunk_files_from_directory()
    # Create the vector store from the loaded text chunks
    vector_store = get_vector_store(text_chunks)

def generate_answer(question: str) -> str:
    """
    Generates an answer to the given question using a Hugging Face model and vector store retrieval.
    - If the vector store is not initialized, it initializes it automatically.
    - Uses a predefined prompt template to structure the query for the language model.
    
    Args:
        question (str): The question to be answered.
    
    Returns:
        str: The generated answer.
    """
    global vector_store

    # Check if the vector store is initialized, and create it if not
    if vector_store is None:
        create_vector_store()

    # Retrieve relevant context from the vector store
    retrieved_docs = vector_store.as_retriever(search_kwargs={"k": 3}).invoke(question)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    # Define the prompt template for the language model
    prompt_template = (
        "Use the following context to answer the question. "
        "If the answer is unknown, respond with 'I don't know'.\n\n"
        "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    )
    formatted_prompt = prompt_template.format(context=context, question=question)

    # Get the answer from the conversation chain
    simulated_answer = conversation.run(question)
    return simulated_answer
