from langchain_community.document_loaders import WebBaseLoader


def load_web(page_url):

    loader = WebBaseLoader(page_url)

    docs = loader.load()

    return docs

