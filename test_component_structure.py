#!/usr/bin/env python3
"""
Script de test pour vérifier la cohérence de la structure des composants générés par l'IA.
Vérifie que l'IA génère toujours exactement 6 composants dans l'ordre spécifié.
"""

import requests
import json
import time
from typing import List, Dict, Any

# Configuration
API_URL = "http://localhost:8000/query"
EXPECTED_COMPONENTS_ORDER = [
    "ZaraHeader",
    "Heading", 
    "ZaraCategoryButtons",
    "Text",
    ["Grid", "ZaraProductGrid"],  # L'un ou l'autre est acceptable
    "ZaraMessageInput"
]

# Questions de test variées
test_questions = [
    "Bonjour, je cherche une robe d'été",
    "Montrez-moi vos smartphones disponibles",
    "Quels sont vos produits populaires ?",
    "Je veux acheter un ordinateur portable",
    "Avez-vous des accessoires ?",
    "Bienvenue, que puis-je faire pour vous ?",
    "Recommandez-moi quelque chose",
    "Je cherche un cadeau"
]

def test_api_connection():
    """Teste la connexion à l'API"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Connexion API réussie")
            return True
        else:
            print(f"❌ Erreur de connexion API: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API. Assurez-vous que le serveur est démarré.")
        return False

def send_query(question: str) -> Dict[str, Any]:
    """Envoie une requête à l'API"""
    try:
        response = requests.post(API_URL, json={"question": question})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erreur API pour '{question}': {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de '{question}': {e}")
        return None

def parse_json_response(answer: str) -> Dict[str, Any]:
    """Parse la réponse JSON de l'IA"""
    try:
        # Nettoyer la réponse si nécessaire
        answer = answer.strip()
        if answer.startswith('```json'):
            answer = answer[7:]
        if answer.endswith('```'):
            answer = answer[:-3]
        
        return json.loads(answer)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        print(f"Réponse reçue: {answer[:200]}...")
        return None

def check_component_structure(components: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Vérifie la structure des composants"""
    result = {
        "valid": True,
        "errors": [],
        "component_count": len(components),
        "component_types": [comp.get("type", "Unknown") for comp in components]
    }
    
    # Vérifier le nombre de composants
    if len(components) != 6:
        result["valid"] = False
        result["errors"].append(f"Nombre de composants incorrect: {len(components)} au lieu de 6")
    
    # Vérifier l'ordre des composants
    for i, expected in enumerate(EXPECTED_COMPONENTS_ORDER):
        if i >= len(components):
            result["valid"] = False
            result["errors"].append(f"Composant manquant à la position {i+1}: {expected}")
            continue
            
        actual_type = components[i].get("type", "Unknown")
        
        # Gérer les cas où plusieurs types sont acceptables
        if isinstance(expected, list):
            if actual_type not in expected:
                result["valid"] = False
                result["errors"].append(f"Position {i+1}: attendu {expected}, reçu {actual_type}")
        else:
            if actual_type != expected:
                result["valid"] = False
                result["errors"].append(f"Position {i+1}: attendu {expected}, reçu {actual_type}")
    
    return result

def run_structure_tests():
    """Lance tous les tests de structure"""
    print("🧪 Test de la cohérence de structure des composants\n")
    
    if not test_api_connection():
        return
    
    results = []
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}/{len(test_questions)}: {question}")
        
        # Envoyer la requête
        response = send_query(question)
        if not response:
            continue
            
        # Parser la réponse JSON
        json_data = parse_json_response(response.get("answer", ""))
        if not json_data:
            continue
            
        # Vérifier la structure
        components = json_data.get("components", [])
        structure_check = check_component_structure(components)
        
        results.append({
            "question": question,
            "structure_check": structure_check,
            "json_data": json_data
        })
        
        # Afficher le résultat
        if structure_check["valid"]:
            print(f"✅ Structure valide: {structure_check['component_types']}")
        else:
            print(f"❌ Structure invalide:")
            for error in structure_check["errors"]:
                print(f"   - {error}")
            print(f"   Types reçus: {structure_check['component_types']}")
        
        # Pause entre les requêtes
        time.sleep(1)
    
    # Résumé final
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    valid_count = sum(1 for r in results if r["structure_check"]["valid"])
    total_count = len(results)
    
    print(f"Tests réussis: {valid_count}/{total_count}")
    print(f"Taux de réussite: {(valid_count/total_count)*100:.1f}%" if total_count > 0 else "Aucun test exécuté")
    
    if valid_count < total_count:
        print("\n❌ Erreurs détectées:")
        for result in results:
            if not result["structure_check"]["valid"]:
                print(f"\n• Question: {result['question']}")
                for error in result["structure_check"]["errors"]:
                    print(f"  - {error}")
    
    # Sauvegarder les résultats
    with open("test_structure_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Résultats sauvegardés dans test_structure_results.json")

if __name__ == "__main__":
    run_structure_tests()