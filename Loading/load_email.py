from langchain_community.document_loaders import UnstructuredEmailLoader

def load_email(path):
    loader = UnstructuredEmailLoader(path)

    docs = loader.load()

    return docs