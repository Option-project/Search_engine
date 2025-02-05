
import sys
sys.path.insert(0, 'C:/Users/User/Desktop/Search_engine')

import os
import time
from datetime import datetime, timezone
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from langchain_community.document_loaders import PyMuPDFLoader, WebBaseLoader, TextLoader, UnstructuredPowerPointLoader, UnstructuredEmailLoader, Docx2txtLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import pytesseract
from Loading.ocr_to_text_file import parse_image
from Loading.audio_to_text_file import transcribe_audio
import io

class GoogleDriveRAGService:
    def __init__(self, local_data_dir="data", check_interval=60):
        self._SCOPES = ['https://www.googleapis.com/auth/drive']
        self.local_data_dir = local_data_dir
        self.check_interval = check_interval
        self.last_check_time = None
        self.known_files = set()
        
        # Ensure data directory exists
        os.makedirs(local_data_dir, exist_ok=True)
        
        # Initialize Google Drive service
        _base_path = os.path.dirname(__file__)
        _credential_path = os.path.join(_base_path, 'C:/Users/User/Desktop/Search_engine/google_drive_integration/credential.json')
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _credential_path
        self.service = self._build_service()

        # Google Workspace MIME types mapping
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
                # Handle Google Workspace files
                export_mime_type, extension = self.GOOGLE_MIME_TYPES[mime_type]
                request = self.service.files().export_media(
                    fileId=file_id,
                    mimeType=export_mime_type
                )
                # Update filename with correct extension
                file_path = os.path.splitext(file_path)[0] + extension
            else:
                # Handle regular files
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
            # Select appropriate loader based on file extension
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

            # Load and chunk the document
            documents.extend(loader.load())
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_documents(documents)
            return chunks

        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            return None

    def check_for_new_files(self):
        current_files = self._list_drive_files()
        new_files = []
        
        for file in current_files:
            file_id = file['id']
            if file_id not in self.known_files:
                new_files.append(file)
                self.known_files.add(file_id)
        
        return new_files

    def start_monitoring(self):
        print(f"Starting Google Drive monitoring. Checking every {self.check_interval} seconds...")
        
        while True:
            try:
                new_files = self.check_for_new_files()
                
                for file in new_files:
                    print(f"New file detected: {file['name']} (MIME type: {file['mimeType']})")
                    file_path = self._download_file(
                        file['id'], 
                        file['name'],
                        file['mimeType']
                    )
                    
                    if file_path:
                        chunks = self.process_file(file_path)
                        if chunks:
                            print(f"Successfully processed {file['name']} into {len(chunks)} chunks")
                            # Here you can add your code to handle the chunks
                            # For example, store them in your vector database
                        else:
                            print(f"Failed to process {file['name']}")
                    else:
                        print(f"Failed to download {file['name']}")
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Error during monitoring: {str(e)}")
                time.sleep(self.check_interval)

# Usage example
if __name__ == "__main__":
    rag_service = GoogleDriveRAGService(check_interval=60)  # Check every 60 seconds
    rag_service.start_monitoring()