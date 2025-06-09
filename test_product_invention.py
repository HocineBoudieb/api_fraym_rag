#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier que l'IA ne génère pas de produits inventés
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"

def test_product_invention():
    """Teste si l'IA invente des produits ou reste fidèle au catalogue"""
    
    # Questions qui pourraient pousser l'IA à inventer des produits
    test_questions = [
        # Questions sans le mot 'produit' (test principal)
        "J'ai envie de faire des cadeaux à ma mère, que me proposez-vous ?",
        "Que me conseillez-vous pour un anniversaire ?",
        "J'ai besoin d'aide pour choisir quelque chose",
        "Que puis-je offrir à mon ami ?",
        "Je cherche des idées de cadeaux",
        "Pouvez-vous me recommander quelque chose ?",
        "Qu'avez-vous à me proposer ?",
        "Je ne sais pas quoi acheter",
        
        # Questions spécifiques pour des produits inexistants
        "Avez-vous des coffrets spa ?",
        "Je cherche un parfum pour femme",
        "Proposez-vous des bijoux ?",
        "J'aimerais acheter des vêtements",
        "Avez-vous des produits de beauté ?",
        "Je cherche des livres",
        "Proposez-vous des jouets pour enfants ?",
        "J'aimerais un cadeau romantique",
        "Avez-vous des produits pour la maison ?"
    ]
    
    print("🧪 Test de prévention d'invention de produits")
    print("=" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        
        try:
            # Envoyer la requête
            response = requests.post(
                f"{BASE_URL}/query",
                json={"query": question},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")
                sources = data.get("sources", [])
                
                print(f"✅ Réponse reçue")
                print(f"📊 Sources utilisées: {len(sources)}")
                
                # Analyser la réponse pour détecter des produits inventés
                try:
                    # Essayer de parser le JSON de la réponse
                    if answer.strip().startswith('{'):
                        json_response = json.loads(answer)
                        
                        # Extraire les produits mentionnés
                        products_mentioned = extract_products_from_json(json_response)
                        
                        if products_mentioned:
                            print(f"🛍️ Produits mentionnés: {products_mentioned}")
                            
                            # Vérifier si les produits sont dans le catalogue réel
                            real_products = [
                                "iPhone 15 Pro", "Samsung Galaxy S24 Ultra", 
                                "MacBook Air M3", "Dell XPS 13", 
                                "AirPods Pro", "Magic Keyboard"
                            ]
                            
                            invented_products = []
                            for product in products_mentioned:
                                if not any(real_product.lower() in product.lower() for real_product in real_products):
                                    invented_products.append(product)
                            
                            if invented_products:
                                print(f"⚠️ PRODUITS POTENTIELLEMENT INVENTÉS: {invented_products}")
                            else:
                                print("✅ Tous les produits semblent être du catalogue réel")
                        else:
                            print("ℹ️ Aucun produit spécifique mentionné (réponse générale)")
                    else:
                        print("ℹ️ Réponse non-JSON reçue")
                        
                except json.JSONDecodeError:
                    print("⚠️ Impossible de parser la réponse JSON")
                    
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion: {e}")
            
        # Pause entre les tests
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("🏁 Tests terminés")

def extract_products_from_json(json_data):
    """Extrait les noms de produits d'une réponse JSON"""
    products = []
    
    def search_in_dict(obj, key_patterns=["title", "name", "product", "text"]):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if any(pattern in key.lower() for pattern in key_patterns):
                    if isinstance(value, str) and len(value) > 3:
                        products.append(value)
                elif isinstance(value, (dict, list)):
                    search_in_dict(value, key_patterns)
        elif isinstance(obj, list):
            for item in obj:
                search_in_dict(item, key_patterns)
    
    search_in_dict(json_data)
    return products

def test_specific_product_request():
    """Teste une demande de produit spécifique qui n'existe pas"""
    print("\n🎯 Test de demande de produit spécifique inexistant")
    print("=" * 50)
    
    question = "Avez-vous un coffret spa à 60€ ?"
    print(f"📝 Question: {question}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={"query": question},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "")
            
            print("✅ Réponse reçue:")
            print(f"📄 {answer[:200]}..." if len(answer) > 200 else answer)
            
            # Vérifier si la réponse mentionne que le produit n'existe pas
            negative_indicators = [
                "pas disponible", "n'existe pas", "non disponible", 
                "pas en stock", "introuvable", "pas dans", "absent"
            ]
            
            answer_lower = answer.lower()
            if any(indicator in answer_lower for indicator in negative_indicators):
                print("✅ L'IA indique correctement que le produit n'est pas disponible")
            else:
                print("⚠️ L'IA pourrait avoir inventé le produit ou donné une réponse ambiguë")
                
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    print("🚀 Démarrage des tests de prévention d'invention de produits")
    print("Assurez-vous que le serveur RAG est démarré sur http://localhost:8000")
    print()
    
    # Vérifier que le serveur est accessible
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Serveur RAG accessible")
            print()
            
            # Lancer les tests
            test_product_invention()
            test_specific_product_request()
            
        else:
            print(f"❌ Serveur RAG non accessible (status: {response.status_code})")
            
    except requests.exceptions.RequestException:
        print("❌ Impossible de se connecter au serveur RAG")
        print("Assurez-vous qu'il est démarré avec: python main.py")