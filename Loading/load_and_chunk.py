import os
from langchain_community.document_loaders import PyMuPDFLoader, WebBaseLoader, TextLoader,  UnstructuredPowerPointLoader, UnstructuredEmailLoader, Docx2txtLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import pytesseract
from Loading.ocr_to_text_file import parse_image
import sys
sys.path.insert(0, '..')
def load_chunk_files_from_directory():
    directory_path = "/Users/nadadroussi/Desktop/Search_engine/data"
    pytesseract_path = r'/opt/homebrew/bin/tesseract' #You should install tessetact and include its path here
    documents = []
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        file_extension = os.path.splitext(file_name)[1].lower()
        filename = os.path.splitext(file_path)[0].lower()

        # Use loaders based on file extension
        if file_extension == ".txt":
            loader = TextLoader(file_path)
        elif file_extension == ".pdf":
            loader = PyMuPDFLoader(file_path)
        elif file_extension == ".docx":
            loader = Docx2txtLoader(file_path)
        elif file_extension == ".csv":
            loader = CSVLoader(file_path)
        elif file_extension == ".eml":
            loader = UnstructuredEmailLoader(file_path)

        elif file_extension in [".png", ".jpg", ".jpeg"]:
            output_path = filename + ".txt"
            print(output_path)
            parse_image(file_path, pytesseract_path, output_path)
            loader = TextLoader(output_path)
        else:
            print(f"Unsupported file type: {file_extension}. Skipping file: {file_name}")
            continue

        # Load documents from the file
        documents.extend(loader.load())
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100) # Modify the chunk_size and chunk_overlap

    chunks = text_splitter.split_documents(documents)


    return chunks


#chunks = load_chunk_files_from_directory()
#for chunk in chunks:
    #print(chunk)
    #print("-----------------------")