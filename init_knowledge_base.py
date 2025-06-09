#!/usr/bin/env python3
"""
Script d'initialisation de la base de connaissances avec LangChain
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Fonction principale d'initialisation"""
    try:
        # Charger les variables d'environnement
        load_dotenv()
        
        # Vérifier la clé API
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY non trouvée dans le fichier .env")
        
        logger.info("🚀 Initialisation de la base de connaissances avec LangChain")
        
        # Configuration des chemins
        knowledge_path = Path("knowledges")
        chroma_db_path = "./chroma_langchain_db"
        
        # Vérifier que le dossier knowledges existe
        if not knowledge_path.exists():
            logger.error(f"❌ Dossier {knowledge_path} non trouvé")
            return
        
        # Supprimer l'ancienne base si elle existe
        if os.path.exists(chroma_db_path):
            import shutil
            shutil.rmtree(chroma_db_path)
            logger.info(f"🗑️ Ancienne base supprimée: {chroma_db_path}")
        
        # Initialiser les embeddings
        logger.info("🔧 Initialisation des embeddings OpenAI...")
        embeddings = OpenAIEmbeddings(
            openai_api_key=api_key,
            model="text-embedding-3-small"
        )
        
        # Initialiser le text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Charger tous les documents
        logger.info(f"📁 Chargement des documents depuis {knowledge_path}...")
        
        # Charger les fichiers markdown et texte
        loader = DirectoryLoader(
            str(knowledge_path),
            glob="*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            show_progress=True
        )
        
        documents = loader.load()
        logger.info(f"📄 {len(documents)} documents chargés")
        
        if not documents:
            logger.warning("⚠️ Aucun document trouvé")
            return
        
        # Afficher les fichiers chargés
        for doc in documents:
            filename = os.path.basename(doc.metadata.get('source', 'Unknown'))
            content_length = len(doc.page_content)
            logger.info(f"  📝 {filename}: {content_length} caractères")
        
        # Diviser les documents en chunks avec métadonnées enrichies
        logger.info("✂️ Division des documents en chunks...")
        texts = text_splitter.split_documents(documents)
        
        # Enrichir les métadonnées avec des tags
        for text in texts:
            source_file = os.path.basename(text.metadata.get('source', ''))
            content = text.page_content.lower()
            
            # Ajouter des tags basés sur le contenu et le fichier source
            tags = []
            
            # Tags basés sur le nom du fichier
            if 'product' in source_file or 'catalog' in source_file:
                tags.extend(['product', 'catalog'])
            if 'ecommerce' in source_file:
                tags.extend(['ecommerce', 'general'])
            if 'faq' in source_file:
                tags.extend(['faq', 'support'])
            if 'customer' in source_file:
                tags.extend(['customer_service', 'support'])
            
            # Tags basés sur le contenu
            if any(word in content for word in ['prix', 'price', '€', 'euro']):
                tags.append('pricing')
            if any(word in content for word in ['iphone', 'samsung', 'macbook', 'dell', 'airpods']):
                tags.extend(['product', 'electronics'])
            if any(word in content for word in ['livraison', 'delivery', 'shipping']):
                tags.append('shipping')
            if any(word in content for word in ['garantie', 'warranty', 'sav']):
                tags.append('warranty')
            if any(word in content for word in ['paiement', 'payment', 'carte']):
                tags.append('payment')
            
            # Ajouter les tags aux métadonnées (convertir en string pour ChromaDB)
            unique_tags = list(set(tags))  # Supprimer les doublons
            text.metadata['tags'] = ','.join(unique_tags) if unique_tags else 'general'
            text.metadata['content_type'] = 'product' if 'product' in tags else 'general'
        
        logger.info(f"📦 {len(texts)} chunks créés avec métadonnées enrichies")
        
        # Créer la base vectorielle
        logger.info("🔍 Création de la base vectorielle ChromaDB...")
        vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=embeddings,
            persist_directory=chroma_db_path
        )
        
        # Persister la base
        vectorstore.persist()
        logger.info(f"💾 Base vectorielle sauvegardée dans {chroma_db_path}")
        
        # Vérification
        collection = vectorstore._collection
        total_docs = collection.count()
        logger.info(f"✅ Vérification: {total_docs} documents dans la base")
        
        # Statistiques par fichier
        logger.info("\n📊 Statistiques par fichier:")
        file_stats = {}
        for text in texts:
            source = text.metadata.get('source', 'Unknown')
            filename = os.path.basename(source)
            if filename not in file_stats:
                file_stats[filename] = 0
            file_stats[filename] += 1
        
        for filename, count in file_stats.items():
            logger.info(f"  📄 {filename}: {count} chunks")
        
        # Test de recherche
        logger.info("\n🔍 Test de recherche...")
        test_query = "produits disponibles"
        results = vectorstore.similarity_search(test_query, k=3)
        
        logger.info(f"Requête test: '{test_query}'")
        logger.info(f"Résultats trouvés: {len(results)}")
        
        for i, result in enumerate(results, 1):
            source = os.path.basename(result.metadata.get('source', 'Unknown'))
            preview = result.page_content[:100].replace('\n', ' ')
            logger.info(f"  {i}. {source}: {preview}...")
        
        logger.info("\n🎉 Initialisation terminée avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {e}")
        raise

if __name__ == "__main__":
    main()