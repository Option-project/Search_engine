import sys
sys.path.insert(0, 'C:/Users/User/Desktop/Search_engine')

import threading
from typing import Optional, List
import os
import time
from datetime import datetime, timezone
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from langchain_community.document_loaders import PyMuPDFLoader, WebBaseLoader, TextLoader, UnstructuredPowerPointLoader, UnstructuredEmailLoader, Docx2txtLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from llm.utils import get_vector_store, get_conversation_chain
import pytesseract
from Loading.ocr_to_text_file import parse_image
from Loading.audio_to_text_file import transcribe_audio
from huggingface_hub import InferenceClient





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
        

        # Initialize the Hugging Face client
        self.client = InferenceClient("meta-llama/Meta-Llama-3-8B-Instruct")

        # Ensure data directory exists
        os.makedirs(local_data_dir, exist_ok=True)
        
        # Initialize Google Drive service
        _credential_path = 'C:/Users/User/Desktop/Search_engine/google_drive_integration/credential.json'
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

    def process_file(self, file_path):
        if not file_path:
            return None
            
        file_extension = os.path.splitext(file_path)[1].lower()
        filename = os.path.splitext(file_path)[0].lower()
        documents = []

        try:
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
                pytesseract_path = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
                parse_image(file_path, pytesseract_path, output_path)
                loader = TextLoader(output_path)
            elif file_extension in [".mp3", ".wav"]:
                output_path = filename + ".txt"
                transcribe_audio(file_path, output_path)
                loader = TextLoader(output_path)
            else:
                print(f"Unsupported file type: {file_extension}. Skipping file: {file_path}")
                return None

            documents.extend(loader.load())
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_documents(documents)
            return chunks

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