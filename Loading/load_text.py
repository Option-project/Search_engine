from langchain_community.document_loaders import TextLoader

def load_text(text_path):

    loader = TextLoader(text_path)
    docs = loader.load()

    return docs