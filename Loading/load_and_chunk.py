# import os
# from langchain_community.document_loaders import PyMuPDFLoader, WebBaseLoader, TextLoader,  UnstructuredPowerPointLoader, UnstructuredEmailLoader, Docx2txtLoader, CSVLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.schema import Document
# import pytesseract
# from Loading.ocr_to_text_file import parse_image
# import sys
# sys.path.insert(0, '..')
# def load_chunk_files_from_directory():
#     directory_path = "/Users/nadadroussi/Desktop/Search_engine/data"
#     pytesseract_path = r'/opt/homebrew/bin/tesseract' #You should install tessetact and include its path here
#     documents = []
#     for file_name in os.listdir(directory_path):
#         file_path = os.path.join(directory_path, file_name)
#         file_extension = os.path.splitext(file_name)[1].lower()
#         filename = os.path.splitext(file_path)[0].lower()

#         # Use loaders based on file extension
#         if file_extension == ".txt":
#             loader = TextLoader(file_path)
#         elif file_extension == ".pdf":
#             loader = PyMuPDFLoader(file_path)
#         elif file_extension == ".docx":
#             loader = Docx2txtLoader(file_path)
#         elif file_extension == ".csv":
#             loader = CSVLoader(file_path)
#         elif file_extension == ".eml":
#             loader = UnstructuredEmailLoader(file_path)

#         elif file_extension in [".png", ".jpg", ".jpeg"]:
#             output_path = filename + ".txt"
#             print(output_path)
#             parse_image(file_path, pytesseract_path, output_path)
#             loader = TextLoader(output_path)
#         else:
#             print(f"Unsupported file type: {file_extension}. Skipping file: {file_name}")
#             continue

#         # Load documents from the file
#         documents.extend(loader.load())
    
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100) # Modify the chunk_size and chunk_overlap

#     chunks = text_splitter.split_documents(documents)


#     return chunks


# #chunks = load_chunk_files_from_directory()
# #for chunk in chunks:
#     #print(chunk)
#     #print("-----------------------")

import os 
import fitz  # PyMuPDF
import pandas as pd
import pytesseract
from PIL import Image
import email
from email import policy
from bs4 import BeautifulSoup
import spacy
from sentence_transformers import SentenceTransformer, util
from dataclasses import dataclass

# Initialisation des modèles NLP
nlp = spacy.load("en_core_web_sm")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  
# Configuration Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

@dataclass
class Document:
    page_content: str
    metadata: dict

# Fonction de chunking sémantique
def semantic_chunking(text, metadata, similarity_threshold=0.75):
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]

    embeddings = embedding_model.encode(sentences)

    chunks = []
    current_chunk = [sentences[0]]
    for i in range(1, len(sentences)):
        similarity = util.cos_sim(embeddings[i], embeddings[i-1])[0][0]
        if similarity >= similarity_threshold:
            current_chunk.append(sentences[i])
        else:
            chunks.append(Document(
                page_content=" ".join(current_chunk),
                metadata=metadata
            ))
            current_chunk = [sentences[i]]

    if current_chunk:
        chunks.append(Document(
            page_content=" ".join(current_chunk),
            metadata=metadata
        ))

    return chunks

# Extraction des données des fichiers
def load_chunk_files_from_directory(directory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
):
    documents = []

    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        file_extension = os.path.splitext(file_name)[1].lower()
        
        metadata = {
            "source": file_path,
            "file_type": file_extension[1:],  # Remove the dot
            "file_name": file_name
        }

        # Cas des fichiers PDF
        if file_extension == ".pdf":
            text = extract_text_from_pdf(file_path)
            chunks = chunk_pdf(text, metadata)

        # Cas des fichiers CSV
        elif file_extension == ".csv":
            text = extract_text_from_csv(file_path)
            chunks = chunk_csv(text, metadata)

        # Cas des fichiers EML (emails)
        elif file_extension == ".eml":
            text = extract_text_from_eml(file_path)
            chunks = chunk_email(text, metadata)

        # Cas des fichiers PNG (OCR)
        elif file_extension in [".png"]:
            text = extract_text_from_image(file_path)
            chunks = chunk_image(text, metadata)

        else:
            print(f"Unsupported file type: {file_extension}. Skipping file: {file_name}")
            continue

        documents.extend(chunks)

    return documents

# Extraction du texte des fichiers PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text() + "\n"
    return text

# Extraction du texte des fichiers CSV
def extract_text_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    return df.to_string(index=False)

# Extraction du texte des fichiers Email (EML)
def extract_text_from_eml(eml_path):
    with open(eml_path, "r", encoding="utf-8") as f:
        msg = email.message_from_file(f, policy=policy.default)
    
    text = f"Subject: {msg['subject']}\nFrom: {msg['from']}\nTo: {msg['to']}\n\n"
    
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            text += part.get_payload(decode=True).decode("utf-8", errors="ignore")
        elif part.get_content_type() == "text/html":
            soup = BeautifulSoup(part.get_payload(decode=True), "html.parser")
            text += soup.get_text()
    
    return text

# Extraction du texte des fichiers PNG (OCR)
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

#  Chunking des fichiers PDF (Section -> Semantic)
def chunk_pdf(text, metadata):
    sections = text.split("\n\n")  # Découpage par paragraphes
    return semantic_chunking(" ".join(sections), metadata)

#  Chunking des fichiers CSV (Row -> Semantic)
def chunk_csv(text, metadata):
    rows = text.split("\n")
    return semantic_chunking(" ".join(rows), metadata)

# Chunking des fichiers EML (Topic -> Semantic)
def chunk_email(text, metadata):
    topic_sections = text.split("\n\n")  # Découpage par blocs de texte
    return semantic_chunking(" ".join(topic_sections), metadata)

# Chunking des fichiers PNG (OCR -> Semantic)
def chunk_image(text, metadata):
    paragraphs = text.split("\n\n")  # Découpage par paragraphes détectés
    return semantic_chunking(" ".join(paragraphs), metadata)

# Exécution du script principal
if __name__ == "__main__":
    chunks = load_chunk_files_from_directory()
    print("\nExtracted Chunks:")
    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i}:")
        print(f"Content: {chunk.page_content}")
        print(f"Metadata: {chunk.metadata}")
        print("-" * 40)