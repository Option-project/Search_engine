import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.utils import get_vector_store, get_conversation_chain
from Loading.load_and_chunk import load_chunk_files_from_directory
from embedding.embedding_generator import dataPreprocessing



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
    chain_output = conversation({"question": question}, return_only_outputs=True)
    
    # Extract the answer from the output (adjust the key if necessary)
    answer = chain_output.get("answer", "No answer found.")
    
    # Retrieve the source documents from the output
    source_docs = chain_output.get("source_documents", [])
    
    # Extract the 'source' metadata from each document (or set a default if not available)
    references = [doc.metadata.get("source", "Unknown source") for doc in source_docs]
    
    return answer, references
