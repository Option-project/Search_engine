import os
import numpy as np
from split_documents import split
from load_pdf import load_pdf
from load_docx import load_docx
from load_email import load_email
from load_ppt import load_ppt
from load_csv import load_csv
from load_webpage import load_web
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import logging


class dataPreprocessing:
    """
    Classe pour charger des données, les chunker, générer des embeddings normalisés,
    et gérer un index FAISS avec métadonnées et indexation incrémentielle.
    """

    def __init__(self, model_name="sentence-transformers/msmarco-distilbert-base-v3", index_file="faiss_index"):
        """
        Initialise le modèle d'embedding et le fichier d'index FAISS.
        Args:
            model_name (str): Modèle Hugging Face pour les embeddings.
            index_file (str): Chemin pour sauvegarder l'index FAISS.
        """
        self.model_name = model_name
        self.index_file = index_file
        self.embeddings_model = HuggingFaceEmbeddings(model_name=model_name)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("UnifiedDataProcessor")

        # Mapping des loaders pour différents types de fichiers
        self.loader_mapping = {
            ".pdf": load_pdf,
            ".docx": load_docx,
            ".csv": load_csv,
            ".ppt": load_ppt,
            ".eml": load_email,
            "web": load_web
        }

    def load_file(self, file_path):
        """
        Charge un fichier en fonction de son extension.
        Args:
            file_path (str): Chemin du fichier à charger.
        Returns:
            list: Documents chargés sous forme de texte.
        """
        try:
            _, file_extension = os.path.splitext(file_path)
            file_extension = file_extension.lower()

            if file_extension in self.loader_mapping:
                loader_function = self.loader_mapping[file_extension]
                documents = loader_function(file_path)
                return documents
            else:
                raise ValueError(f"Type de fichier non supporté : {file_extension}")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du fichier {file_path} : {e}")
            return []

    def split_documents(self, documents):
        """
        Divise les documents en chunks textuels en utilisant une méthode avancée.
        Args:
            documents (list): Liste de documents.
        Returns:
            list: Liste de chunks textuels.
        """
        self.logger.info("Découpage des documents en chunks...")
        chunks = split(documents)  # Utilise la fonction existante
        self.logger.info(f"{len(chunks)} chunks générés.")
        return chunks

    def normalize_embeddings(self, embeddings):
        """
        Normalise les embeddings pour garantir une norme unitaire.
        Args:
            embeddings (list): Liste d'embeddings.
        Returns:
            list: Liste des embeddings normalisés.
        """
        self.logger.info("Normalisation des embeddings...")
        return [embedding / np.linalg.norm(embedding) for embedding in embeddings]

    def generate_embeddings(self, chunks, batch_size=32):
        """
        Génère les embeddings pour une liste de chunks avec traitement par lot.
        Args:
            chunks (list): Liste de chunks textuels.
            batch_size (int): Taille des lots pour le traitement.
        Returns:
            list: Liste des embeddings normalisés.
        """
        if not chunks:
            raise ValueError("La liste de chunks est vide.")
        
        self.logger.info(f"Génération des embeddings pour {len(chunks)} chunks...")
        embeddings = []
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_embeddings = self.embeddings_model.embed_documents(batch_chunks)
            embeddings.extend(batch_embeddings)
        
        normalized_embeddings = self.normalize_embeddings(embeddings)
        self.logger.info("Embeddings générés et normalisés avec succès.")
        return normalized_embeddings

    def create_or_update_faiss_index(self, chunks, embeddings, metadata=None):
        """
        Ajoute ou met à jour un index FAISS avec de nouveaux chunks et embeddings.
        Args:
            chunks (list): Texte des chunks.
            embeddings (list): Embeddings correspondants.
            metadata (list): Métadonnées associées.
        """
        try:
            self.logger.info("Chargement ou création de l'index FAISS...")
            vectorstore = FAISS.load_local(self.index_file, self.embeddings_model)
        except Exception:
            self.logger.info("Index FAISS introuvable. Création d'un nouvel index...")
            vectorstore = FAISS.from_texts([], self.embeddings_model)

        vectorstore.add_texts(
            texts=chunks,
            embeddings=embeddings,
            metadatas=metadata or [{} for _ in chunks]
        )
        vectorstore.save_local(self.index_file)
        self.logger.info(f"Index FAISS mis à jour et sauvegardé dans {self.index_file}.")

    def process_file(self, file_path_or_url, metadata=None):
        """
        Traite un fichier ou une URL pour le charger, le chunker, et mettre à jour l'index FAISS.
        Args:
            file_path_or_url (str): Chemin ou URL.
            metadata (dict): Métadonnées associées au fichier.
        """
        try:
            # Charger les documents
            if file_path_or_url.startswith("http"):
                documents = load_web(file_path_or_url)
            else:
                documents = self.load_file(file_path_or_url)

            # Diviser en chunks
            chunks = self.split_documents(documents)

            # Générer les embeddings
            embeddings = self.generate_embeddings(chunks)

            # Mettre à jour l'index FAISS
            self.create_or_update_faiss_index(chunks, embeddings, metadata=metadata)
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de {file_path_or_url} : {e}")

    def search(self, query, k=5):
        """
        Effectue une recherche dans l'index FAISS et retourne des résultats enrichis.
        Args:
            query (str): Requête textuelle.
            k (int): Nombre de résultats à retourner.
        Returns:
            list: Résultats enrichis avec contenu, métadonnées et scores.
        """
        try:
            self.logger.info("Recherche dans l'index FAISS...")
            vectorstore = FAISS.load_local(self.index_file, self.embeddings_model)
            results = vectorstore.similarity_search_with_score(query, k=k)
            enriched_results = [
                {"content": res[0].page_content, "metadata": res[0].metadata, "score": res[1]}
                for res in results
            ]
            self.logger.info(f"{len(enriched_results)} résultats trouvés.")
            return enriched_results
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche : {e}")
            return []
