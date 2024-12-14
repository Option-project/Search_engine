from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.embeddings.ollama import OllamaEmbeddings
from langchain.vectorstores import Chroma

def get_retriever_from_vector_db(chunks):
    # Add documents to vector database
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=OllamaEmbeddings(model="nomic-embed-text", show_progress=True),
        collection_name="local-rag"
    )
    # Return a simple retriever without using an LLM
    retriever = vector_db.as_retriever()
    return retriever