from langchain.text_splitter import RecursiveCharacterTextSplitter

def split(documents):

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20) # you should define chunk size and chunk overlap based on documents type

    splits = text_splitter.split_documents(documents)

    return splits