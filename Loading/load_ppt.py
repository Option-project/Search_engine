from langchain_community.document_loaders import UnstructuredPowerPointLoader


def load_ppt(path):

    loader = UnstructuredPowerPointLoader(path)

    docs = loader.load()

    return docs