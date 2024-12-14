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

load_dotenv()

# read pdf and extract text from pdf's pages:
def get_pdf_text(pdf_docs):
    text = ''
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text

# get the text chunks
def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size = 1000,
        chunk_overlap = 200,
        length_function = len
    )
    chunks = text_splitter.split_text(text)
    return chunks



def get_vector_store(chunks):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(texts = chunks, embedding = embeddings)
    return vectorstore

# create conversation chain
def get_conversation_chain(vectorstore):
    llm = ChatOllama(model_name="llama2:latest", temperature=0)

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(), 
        memory=memory
    )
    return conversation_chain

    


def main():
    # get the extracted text from multiple pdfs
    pdf_docs = ['pdf_data/exp1.pdf', 'pdf_data/exp2.pdf']
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


if __name__ == '__main__':
    # Call the main function
    final_answer = main()
    if final_answer:
        print("Final Answer:")
        print(final_answer)