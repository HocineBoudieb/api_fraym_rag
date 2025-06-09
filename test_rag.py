#!/usr/bin/env python3
"""
Script de test pour le système RAG avec LangChain
"""

import asyncio
import json
from pathlib import Path
from main import rag_system

def test_queries():
    """Test différentes requêtes sur le système RAG"""
    
    # Liste de requêtes de test
    test_queries = [
        "Liste moi tous les produits disponibles",
        "Quels smartphones sont disponibles ?",
        "Comment contacter le service client ?",
        "Quelles sont les heures d'ouverture ?",
        "Quelle est la politique de retour ?",
        "Comment préparer une pizza margherita ?",
        "Quels sont les composants disponibles ?"
    ]
    
    print("🧪 Test du système RAG avec LangChain\n")
    
    # Informations sur le système
    info = rag_system.get_collection_info()
    print(f"📊 Informations système:")
    print(f"   Status: {info.get('status')}")
    print(f"   Documents: {info.get('count')}")
    print(f"   Modèle embedding: {info.get('embedding_model')}")
    print(f"   Modèle LLM: {info.get('llm_model')}")
    print("\n" + "="*80 + "\n")
    
    # Tester chaque requête
    for i, query in enumerate(test_queries, 1):
        print(f"🔍 Test {i}: {query}")
        print("-" * 60)
        
        try:
            result = rag_system.query(query, max_results=3)
            
            print(f"📝 Réponse:")
            print(f"   {result['answer']}")
            print(f"\n📚 Sources ({len(result['sources'])}):") 
            
            for j, source in enumerate(result['sources'], 1):
                source_file = source['metadata'].get('source', 'Unknown')
                filename = Path(source_file).name if source_file != 'Unknown' else 'Unknown'
                content_preview = source['content'][:100].replace('\n', ' ')
                print(f"   {j}. {filename}: {content_preview}...")
            
            print(f"\n📈 Métadonnées:")
            print(f"   Total sources: {result['metadata']['total_sources']}")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        print("\n" + "="*80 + "\n")

def test_similarity_search():
    """Test de recherche par similarité directe"""
    print("🔍 Test de recherche par similarité\n")
    
    queries = [
        "smartphone",
        "pizza",
        "service client",
        "composants"
    ]
    
    for query in queries:
        print(f"Recherche: '{query}'")
        try:
            # Recherche directe dans le vectorstore
            results = rag_system.vectorstore.similarity_search(query, k=3)
            
            print(f"Résultats trouvés: {len(results)}")
            for i, result in enumerate(results, 1):
                source = Path(result.metadata.get('source', 'Unknown')).name
                preview = result.page_content[:80].replace('\n', ' ')
                print(f"  {i}. {source}: {preview}...")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        print("-" * 40)

def save_test_results():
    """Sauvegarde les résultats de test dans un fichier JSON"""
    print("💾 Sauvegarde des résultats de test...")
    
    test_data = {
        "system_info": rag_system.get_collection_info(),
        "test_results": []
    }
    
    queries = [
        "Liste moi tous les produits disponibles",
        "Quels smartphones sont disponibles ?",
        "Comment contacter le service client ?"
    ]
    
    for query in queries:
        try:
            result = rag_system.query(query, max_results=2)
            test_data["test_results"].append({
                "query": query,
                "answer": result["answer"],
                "sources_count": len(result["sources"]),
                "total_sources": result["metadata"]["total_sources"]
            })
        except Exception as e:
            test_data["test_results"].append({
                "query": query,
                "error": str(e)
            })
    
    # Sauvegarder dans un fichier
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Résultats sauvegardés dans test_results.json")

def main():
    """Fonction principale de test"""
    try:
        print("🚀 Démarrage des tests du système RAG\n")
        
        # Test des requêtes
        test_queries()
        
        # Test de recherche par similarité
        test_similarity_search()
        
        # Sauvegarder les résultats
        save_test_results()
        
        print("\n🎉 Tests terminés avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        raise

if __name__ == "__main__":
    main()