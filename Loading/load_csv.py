from langchain_community.document_loaders.csv_loader import CSVLoader


def load_csv(path):
    
    loader = CSVLoader(file_path=path)

    docs = loader.load()

    return docs