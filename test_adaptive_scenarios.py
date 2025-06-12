#!/usr/bin/env python3
"""
Test du système de scénarios adaptatifs
Ce script teste la détection automatique de scénarios et l'adaptation des formats de réponse.
"""

import asyncio
import json
from main import RAGSystem

def test_scenario_detection():
    """
    Teste la détection de scénarios avec différents types de requêtes
    """
    print("🧪 Test de détection de scénarios")
    print("=" * 50)
    
    # Initialiser le système RAG
    rag = RAGSystem()
    rag.initialize()
    
    # Cas de test avec différents scénarios attendus
    test_cases = [
        {
            "query": "Je veux voir les détails de ce produit",
            "expected_scenario": "single_product",
            "description": "Requête produit unique"
        },
        {
            "query": "Montrez-moi les spécifications complètes",
            "expected_scenario": "single_product",
            "description": "Requête spécifications produit"
        },
        {
            "query": "Montrez-moi des produits électroniques",
            "expected_scenario": "ecommerce_products",
            "description": "Requête produits e-commerce"
        },
        {
            "query": "Quel est votre menu du jour ?",
            "expected_scenario": "restaurant_menu",
            "description": "Requête menu restaurant"
        },
        {
            "query": "J'ai un problème avec ma commande",
            "expected_scenario": "customer_support",
            "description": "Requête support client"
        },
        {
            "query": "Bonjour, pouvez-vous m'aider ?",
            "expected_scenario": "landing_page",
            "description": "Requête d'accueil"
        },
        {
            "query": "Comparez l'iPhone et le Samsung Galaxy",
            "expected_scenario": "product_comparison",
            "description": "Requête de comparaison"
        },
        {
            "query": "Quelles sont vos heures d'ouverture ?",
            "expected_scenario": "informative",
            "description": "Requête informative générale"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        
        try:
            # Simuler une recherche pour obtenir des documents
            if "produit" in test_case['query'].lower() or "électronique" in test_case['query'].lower():
                docs = rag.get_chunks_by_tag('product', limit=5)
            elif "menu" in test_case['query'].lower() or "restaurant" in test_case['query'].lower():
                docs = rag.get_chunks_by_tag('restaurant', limit=5)
            else:
                # Recherche générale
                result = rag.vectorstore.similarity_search(test_case['query'], k=3)
                docs = result if result else []
            
            # Détecter le scénario
            detected_scenario = rag.detect_scenario(test_case['query'], docs)
            
            print(f"Scénario attendu: {test_case['expected_scenario']}")
            print(f"Scénario détecté: {detected_scenario}")
            
            # Vérifier si la détection est correcte
            is_correct = detected_scenario == test_case['expected_scenario']
            status = "✅ CORRECT" if is_correct else "❌ INCORRECT"
            print(f"Résultat: {status}")
            
            results.append({
                "test": test_case['description'],
                "query": test_case['query'],
                "expected": test_case['expected_scenario'],
                "detected": detected_scenario,
                "correct": is_correct
            })
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            results.append({
                "test": test_case['description'],
                "query": test_case['query'],
                "expected": test_case['expected_scenario'],
                "detected": "ERROR",
                "correct": False,
                "error": str(e)
            })
    
    # Résumé des résultats
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    correct_count = sum(1 for r in results if r['correct'])
    total_count = len(results)
    accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"Tests réussis: {correct_count}/{total_count} ({accuracy:.1f}%)")
    
    # Détails des échecs
    failed_tests = [r for r in results if not r['correct']]
    if failed_tests:
        print("\n❌ Tests échoués:")
        for test in failed_tests:
            print(f"  - {test['test']}: attendu '{test['expected']}', obtenu '{test['detected']}'")
    
    return results

def test_scenario_prompts():
    """
    Teste la génération de prompts adaptés aux scénarios
    """
    print("\n🧪 Test de génération de prompts par scénario")
    print("=" * 50)
    
    rag = RAGSystem()
    rag.initialize()
    
    scenarios = ['ecommerce_products', 'restaurant_menu', 'customer_support', 'landing_page', 'informative']
    
    for scenario in scenarios:
        print(f"\n📋 Scénario: {scenario}")
        
        try:
            prompt = rag.get_scenario_prompt(
                scenario=scenario,
                session_context="Conversation précédente...",
                context="Contexte de test...",
                question="Question de test"
            )
            
            # Vérifier que le prompt contient les éléments attendus
            checks = {
                "Contient 'SCÉNARIO'": "SCÉNARIO" in prompt,
                "Contient 'JSON valide'": "JSON valide" in prompt,
                "Contient 'template'": "template" in prompt,
                "Contient 'components'": "components" in prompt
            }
            
            print("Vérifications:")
            for check, result in checks.items():
                status = "✅" if result else "❌"
                print(f"  {status} {check}")
            
            # Afficher un extrait du prompt
            lines = prompt.split('\n')
            preview = '\n'.join(lines[:5]) + "\n..."
            print(f"Aperçu du prompt:\n{preview}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération du prompt: {e}")

def test_full_query_with_scenarios():
    """
    Teste une requête complète avec le nouveau système de scénarios
    """
    print("\n🧪 Test de requête complète avec scénarios")
    print("=" * 50)
    
    rag = RAGSystem()
    rag.initialize()
    
    test_queries = [
        "Montrez-moi des smartphones disponibles",
        "Bonjour, comment ça marche ici ?",
        "J'ai besoin d'aide pour un retour"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Test de la requête: '{query}'")
        
        try:
            result = rag.query(query, max_results=3)
            
            print(f"Métadonnées: {result.get('metadata', {})}")
            
            # Vérifier si la réponse contient un JSON valide
            answer = result.get('answer', '')
            try:
                # Tenter de parser la réponse comme JSON
                json_response = json.loads(answer)
                print("✅ Réponse JSON valide")
                print(f"Template utilisé: {json_response.get('template', 'N/A')}")
                print(f"Nombre de composants: {len(json_response.get('components', []))}")
            except json.JSONDecodeError:
                print("❌ Réponse non-JSON ou JSON invalide")
                print(f"Début de la réponse: {answer[:100]}...")
            
        except Exception as e:
            print(f"❌ Erreur lors de la requête: {e}")

if __name__ == "__main__":
    print("🚀 Démarrage des tests du système de scénarios adaptatifs")
    print("=" * 60)
    
    try:
        # Test 1: Détection de scénarios
        results = test_scenario_detection()
        
        # Test 2: Génération de prompts
        test_scenario_prompts()
        
        # Test 3: Requête complète
        test_full_query_with_scenarios()
        
        print("\n🎉 Tests terminés avec succès !")
        
    except Exception as e:
        print(f"\n💥 Erreur critique lors des tests: {e}")
        import traceback
        traceback.print_exc()