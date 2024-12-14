from langchain_google_community import GoogleDriveLoader
import os
from langchain_community.document_loaders import UnstructuredFileIOLoader, PyMuPDFLoader


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "" #Credentials Placement

def load_googledrive(folder_id):
    """
    Loads files from a specific google drive folder
    folder_id : google drive folder id
    """
    loader = GoogleDriveLoader(
        folder_id=folder_id,
        file_loader_cls=UnstructuredFileIOLoader
    )

    docs = loader.load()

    return docs
