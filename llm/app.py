from utils import get_pdf_text, get_text_chunks, get_vector_store, get_conversation_chain
import sys
sys.path.insert(0, '/Users/nadadroussi/Desktop/Search_engine')
from Loading.load_and_chunk import load_chunk_files_from_directory

def conv(question):


    text_chunks = load_chunk_files_from_directory()
    # print(text_chunks)


    # create the vector store 
    vector_store = get_vector_store(text_chunks)
    
    # create conversation chain
    conversation = get_conversation_chain(vector_store)

    # Get the answer from the conversation chain
    try:
        answer = conversation.run(question)
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        return answer
    except Exception as e:
        print(f"Error during conversation: {e}")
        return None


if __name__ == '__main__':
    # Call the main function
    # Example
    question = "What is this data science?"
    final_answer = conv(question)
    if final_answer:
        print("Final Answer:")
        print(final_answer)