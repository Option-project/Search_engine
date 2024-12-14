import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOllama
from utils import get_pdf_text, get_text_chunks, get_vector_store, get_conversation_chain


def conv(question):
    # get the extracted text from multiple pdfs
    pdf_docs = ['../data/CoursOptimisation.pdf']
    raw_text = get_pdf_text(pdf_docs)
    # print(raw_text)


    # get the text chunks
    text_chunks = get_text_chunks(raw_text)
    # print(text_chunks)


    # create the vector store 
    vector_store = get_vector_store(text_chunks)
    
    # create conversation chain
    conversation = get_conversation_chain(vector_store)


    # Example
    question = "What is this data science?"

    # Get the answer from the conversation chain
    try:
        answer = conversation.run(question)
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        return answer
    except Exception as e:
        print(f"Error during conversation: {e}")
        return None


# if __name__ == '__main__':
#     # Call the main function
#     final_answer = main()
#     if final_answer:
#         print("Final Answer:")
#         print(final_answer)