from llm.utils import get_vector_store, get_conversation_chain
from Loading.load_and_chunk import load_chunk_files_from_directory
from embedding.embedding_generator import dataPreprocessing
import os

# Global variable to hold the vector store
vector_store = None

def create_vector_store():
    """
    Precomputes the vector store by processing documents in the given folder.
    """
    global vector_store


    # Preprocess and chunk text
    text_chunks = load_chunk_files_from_directory()

    # Create and store the vector store globally
    vector_store = get_vector_store(text_chunks)

def generate_answer(question):
    """
    Generates an answer using the existing vector store.
    """
    global vector_store

    if vector_store is None:
        raise RuntimeError("Vector store has not been created. Please call the /vector_store endpoint first.")

    # Create the conversation chain
    conversation = get_conversation_chain(vector_store)

    # Get the answer from the conversation chain
    simulated_answer = conversation.run(question)
    return simulated_answer
