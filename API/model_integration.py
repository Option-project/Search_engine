import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import threading
from typing import Optional, List
import time
from datetime import datetime, timezone
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
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
from huggingface_hub import InferenceClient
from langchain.schema import Document
from llm.utils import get_vector_store, get_conversation_chain
from Loading.audio_to_text_file import transcribe_audio

# Initialisation des modèles NLP
nlp = spacy.load("en_core_web_trf")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

@dataclass
class Document:
    page_content: str
    metadata: dict

class IntegratedRAGService:
    def __init__(self, local_data_dir="data", check_interval=60):
        self._SCOPES = ['https://www.googleapis.com/auth/drive']
        self.local_data_dir = local_data_dir
        self.check_interval = check_interval
        self.vector_store = None
        self.monitoring_thread = None
        self.is_monitoring = False
        self.known_files = set()
        self.last_update_time = None
        
        # Configuration Tesseract OCR
        pytesseract.pytesseract.tesseract_cmd =  r'/opt/homebrew/bin/tesseract'

        # Initialize the Hugging Face client
        self.client = InferenceClient("mistralai/Mistral-7B-Instruct-v0.3")

        # Ensure data directory exists
        os.makedirs(local_data_dir, exist_ok=True)
        
        # Initialize Google Drive service
        _credential_path = 'google_drive_integration/credential.json'
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _credential_path
        self.service = self._build_service()

        self.GOOGLE_MIME_TYPES = {
            'application/vnd.google-apps.document': ('application/pdf', '.pdf'),
            'application/vnd.google-apps.spreadsheet': ('application/pdf', '.pdf'),
            'application/vnd.google-apps.presentation': ('application/pdf', '.pdf'),
            'application/vnd.google-apps.drawing': ('application/pdf', '.pdf'),
        }

    def _build_service(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS"), 
            self._SCOPES
        )
        return build('drive', 'v3', credentials=creds)

    def _list_drive_files(self):
        selected_fields = "files(id,name,webViewLink,modifiedTime,mimeType)"
        results = self.service.files().list(fields=selected_fields).execute()
        return results.get('files', [])

    def _download_file(self, file_id, file_name, mime_type):
        file_path = os.path.join(self.local_data_dir, file_name)
        
        try:
            if mime_type in self.GOOGLE_MIME_TYPES:
                export_mime_type, extension = self.GOOGLE_MIME_TYPES[mime_type]
                request = self.service.files().export_media(
                    fileId=file_id,
                    mimeType=export_mime_type
                )
                file_path = os.path.splitext(file_path)[0] + extension
            else:
                request = self.service.files().get_media(fileId=file_id)

            file_content = request.execute()
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            return file_path

        except Exception as e:
            print(f"Error downloading file {file_name}: {str(e)}")
            return None

    def semantic_chunking(self, text, metadata, similarity_threshold=0.75):
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

    def extract_text_from_pdf(self, pdf_path):
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"
        return text

    def extract_text_from_csv(self, csv_path):
        df = pd.read_csv(csv_path)
        return df.to_string(index=False)

    def extract_text_from_eml(self, eml_path):
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

    def extract_text_from_image(self, image_path):
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    
    def extract_text_from_audio(self, audio_path):
        output_path = audio_path + '.transcript.txt'
        text = transcribe_audio(audio_path, output_path)
        return text
    
    def chunk_pdf(self, text, metadata):
        sections = text.split("\n\n")  # Découpage par paragraphes
        return self.semantic_chunking(" ".join(sections), metadata)

    def chunk_csv(self, text, metadata):
        rows = text.split("\n")  # Découpage par lignes
        return self.semantic_chunking(" ".join(rows), metadata)

    def chunk_email(self, text, metadata):
        topic_sections = text.split("\n\n")  # Découpage par blocs de texte
        return self.semantic_chunking(" ".join(topic_sections), metadata)

    def chunk_image(self, text, metadata):
        paragraphs = text.split("\n\n")  # Découpage par paragraphes détectés
        return self.semantic_chunking(" ".join(paragraphs), metadata)
    
    def chunk_audio(self, text, metadata):
        paragraphs = text.split("\n\n")  # Découpage par paragraphes détectés
        return self.semantic_chunking(" ".join(paragraphs), metadata)
    
    def chunk_txt(self, text, metadata):
        topic_sections = text.split("\n\n")  # Découpage par blocs de texte
        return self.semantic_chunking(" ".join(topic_sections), metadata)
    
    def chunk_docx(self, text, metadata):
        sections = text.split("\n\n")  # Découpage par paragraphes
        return self.semantic_chunking(" ".join(sections), metadata)

    def process_file(self, file_path):
        if not file_path:
            return None
            
        file_extension = os.path.splitext(file_path)[1].lower()
        metadata = {
            "source": file_path,
            "file_type": file_extension[1:],
            "file_name": os.path.basename(file_path)
        }

        try:
            if file_extension == ".pdf":
                text = self.extract_text_from_pdf(file_path)
                return self.chunk_pdf(text, metadata)
            
            elif file_extension == ".csv":
                text = self.extract_text_from_csv(file_path)
                return self.chunk_csv(text, metadata)
            
            elif file_extension == ".eml":
                text = self.extract_text_from_eml(file_path)
                return self.chunk_email(text, metadata)
            
            elif file_extension in [".png", ".jpg", ".jpeg"]:
                text = self.extract_text_from_image(file_path)
                return self.chunk_image(text, metadata)
            
            elif file_extension in [".mp3", ".wav"]:
                text = self.extract_text_from_audio(file_path)
                return self.chunk_audio(text, metadata)
            
            elif file_extension == ".txt":
                text = self.extract_text_from_pdf(file_path)
                return self.chunk_txt(text, metadata)
            
            elif file_extension == ".docx":
                text = self.extract_text_from_pdf(file_path)
                return self.chunk_docx(text, metadata)
            
            else:
                print(f"Unsupported file type: {file_extension}. Skipping file: {file_path}")
                return None

        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            return None

    def update_vector_store(self, new_chunks: List[Document]):
        """Update the vector store with new chunks."""
        if not new_chunks:
            return

        if self.vector_store is None:
            self.vector_store = get_vector_store(new_chunks)
        else:
            # Add new documents to existing vector store
            self.vector_store.add_documents(new_chunks)
        
        self.last_update_time = datetime.now()

    def monitor_drive(self):
        print(f"Starting Google Drive monitoring. Checking every {self.check_interval} seconds...")
        
        while self.is_monitoring:
            try:
                new_files = self._list_drive_files()
                all_chunks = []
                
                for file in new_files:
                    file_id = file['id']
                    if file_id not in self.known_files:
                        print(f"New file detected: {file['name']}")
                        file_path = self._download_file(
                            file['id'], 
                            file['name'],
                            file['mimeType']
                        )
                        
                        if file_path:
                            chunks = self.process_file(file_path)
                            if chunks:
                                all_chunks.extend(chunks)
                                print(f"Successfully processed {file['name']}")
                            else:
                                print(f"Failed to process {file['name']}")
                        
                        self.known_files.add(file_id)
                
                if all_chunks:
                    self.update_vector_store(all_chunks)
                    print(f"Vector store updated with {len(all_chunks)} new chunks")
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Error during monitoring: {str(e)}")
                time.sleep(self.check_interval)

    def start_monitoring(self):
        """Start the monitoring thread if it's not already running."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self.monitor_drive)
            self.monitoring_thread.start()

    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()

    def generate_answer(self, question: str) -> str:
        """
        Generates an answer to the given question using Meta-Llama-3-8B-Instruct and vector store retrieval.
        
        Args:
            question (str): The question to be answered.
        
        Returns:
            str: The generated answer.
        
        Raises:
            RuntimeError: If the vector store hasn't been initialized yet.
        """
        if self.vector_store is None:
            raise RuntimeError("Vector store has not been created yet. Please wait for initial synchronization.")

        # Retrieve relevant context from the vector store
        retrieved_docs = self.vector_store.as_retriever(search_kwargs={"k": 3}).invoke(question)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        # Define the prompt template for the language model
        prompt = f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
Use the following context to answer the question. If the answer cannot be determined from the context, respond with 'I don't know'.

### Input:
Context:
{context}

Question: {question}

### Response:"""

        # Get response from the model
        response = self.client.text_generation(
            prompt,
            max_new_tokens=500,
            temperature=0.7,
            repetition_penalty=1.1,
            do_sample=True,
        )
        
        return response.strip()

