#!/usr/bin/env python3
"""
Script de test pour le nouveau système RAG avec tags
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ajouter le répertoire courant au path pour importer main
sys.path.append(str(Path(__file__).parent))

from main import RAGSystem

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_tag_system():
    """Test du système de tags"""
    try:
        # Charger les variables d'environnement
        load_dotenv()
        
        logger.info("🚀 Test du système RAG avec tags")
        
        # Initialiser le système RAG
        rag = RAGSystem()
        
        # Test 1: Récupération de chunks par tag
        logger.info("\n📋 Test 1: Récupération de chunks avec tag 'product'")
        product_chunks = rag.get_chunks_by_tag('product')
        logger.info(f"Chunks trouvés avec tag 'product': {len(product_chunks)}")
        
        for i, chunk in enumerate(product_chunks[:3]):
            source = os.path.basename(chunk.metadata.get('source', 'Unknown'))
            tags = chunk.metadata.get('tags', [])
            preview = chunk.page_content[:100].replace('\n', ' ')
            logger.info(f"  {i+1}. {source} | Tags: {tags} | {preview}...")
        
        # Test 2: Requête produit
        logger.info("\n🛍️ Test 2: Requête liste de produits")
        result = rag.query("Liste moi tous les produits disponibles")
        
        logger.info(f"Méthode de recherche utilisée: {result['metadata'].get('search_method')}")
        logger.info(f"Tag utilisé: {result['metadata'].get('tag_used', 'N/A')}")
        logger.info(f"Sources trouvées: {result['metadata']['total_sources']}")
        
        logger.info("\n📝 Réponse:")
        print(result['answer'])
        
        # Test 3: Requête générale
        logger.info("\n❓ Test 3: Requête générale (non-produit)")
        result2 = rag.query("Comment contacter le service client?")
        
        logger.info(f"Méthode de recherche utilisée: {result2['metadata'].get('search_method')}")
        logger.info(f"Sources trouvées: {result2['metadata']['total_sources']}")
        
        logger.info("\n📝 Réponse:")
        print(result2['answer'])
        
        # Test 4: Requête avec filtre prix
        logger.info("\n💰 Test 4: Requête avec filtre prix")
        result3 = rag.query("Quels sont les produits moins chers, en dessous de 500€?")
        
        logger.info(f"Méthode de recherche utilisée: {result3['metadata'].get('search_method')}")
        logger.info(f"Tag utilisé: {result3['metadata'].get('tag_used', 'N/A')}")
        logger.info(f"Sources trouvées: {result3['metadata']['total_sources']}")
        
        logger.info("\n📝 Réponse:")
        print(result3['answer'])
        
        logger.info("\n✅ Tests terminés avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors des tests: {e}")
        raise

if __name__ == "__main__":
    test_tag_system()