#!/usr/bin/env python3
"""
Script de test pour vérifier le fonctionnement du système de sessions
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"

def test_session_workflow():
    """Test complet du workflow de sessions"""
    print("🧪 Test du système de sessions")
    print("=" * 50)
    
    # 1. Créer une nouvelle session
    print("\n1. Création d'une nouvelle session...")
    session_data = {
        "title": "Test Session - Produits E-commerce"
    }
    
    response = requests.post(f"{BASE_URL}/sessions", json=session_data)
    if response.status_code == 200:
        session_info = response.json()
        session_id = session_info["session_id"]
        print(f"✅ Session créée: {session_id}")
        print(f"   Titre: {session_info['title']}")
        print(f"   Créée le: {session_info['created_at']}")
    else:
        print(f"❌ Erreur création session: {response.status_code}")
        return
    
    # 2. Poser une première question
    print("\n2. Première question dans la session...")
    query_data = {
        "query": "Quels sont les produits disponibles?",
        "session_id": session_id,
        "max_results": 5
    }
    
    response = requests.post(f"{BASE_URL}/query", json=query_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Réponse reçue (session: {result.get('session_id', 'N/A')})")
        print(f"   Réponse: {result['answer'][:100]}...")
        print(f"   Sources: {len(result['sources'])} documents")
    else:
        print(f"❌ Erreur requête: {response.status_code}")
        return
    
    # 3. Poser une question de suivi
    print("\n3. Question de suivi dans la même session...")
    query_data = {
        "query": "Peux-tu me donner plus de détails sur le premier produit?",
        "session_id": session_id,
        "max_results": 3
    }
    
    response = requests.post(f"{BASE_URL}/query", json=query_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Réponse de suivi reçue")
        print(f"   Réponse: {result['answer'][:100]}...")
    else:
        print(f"❌ Erreur requête de suivi: {response.status_code}")
    
    # 4. Récupérer l'historique de la session
    print("\n4. Récupération de l'historique...")
    response = requests.get(f"{BASE_URL}/sessions/{session_id}/history")
    if response.status_code == 200:
        history = response.json()
        print(f"✅ Historique récupéré: {len(history['messages'])} messages")
        for i, msg in enumerate(history['messages']):
            print(f"   {i+1}. [{msg['role']}] {msg['content'][:50]}...")
    else:
        print(f"❌ Erreur récupération historique: {response.status_code}")
    
    # 5. Lister toutes les sessions
    print("\n5. Liste de toutes les sessions...")
    response = requests.get(f"{BASE_URL}/sessions")
    if response.status_code == 200:
        sessions = response.json()
        print(f"✅ {len(sessions['sessions'])} session(s) trouvée(s)")
        for session in sessions['sessions']:
            print(f"   - {session['session_id']}: {session['title']} ({session['message_count']} messages)")
    else:
        print(f"❌ Erreur liste sessions: {response.status_code}")
    
    # 6. Mettre à jour le titre de la session
    print("\n6. Mise à jour du titre de session...")
    update_data = {
        "title": "Session Test - Produits E-commerce (Modifiée)"
    }
    
    response = requests.put(f"{BASE_URL}/sessions/{session_id}", json=update_data)
    if response.status_code == 200:
        print("✅ Titre de session mis à jour")
    else:
        print(f"❌ Erreur mise à jour: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 Test terminé!")
    print(f"Session de test créée: {session_id}")
    print("Vous pouvez maintenant tester manuellement avec cette session.")

def test_without_session():
    """Test d'une requête sans session_id (création automatique)"""
    print("\n🧪 Test sans session_id (création automatique)")
    print("=" * 50)
    
    query_data = {
        "query": "Comment puis-je contacter le support?",
        "max_results": 3
    }
    
    response = requests.post(f"{BASE_URL}/query", json=query_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Session créée automatiquement: {result.get('session_id', 'N/A')}")
        print(f"   Réponse: {result['answer'][:100]}...")
    else:
        print(f"❌ Erreur: {response.status_code}")

if __name__ == "__main__":
    try:
        # Vérifier que le serveur est accessible
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Serveur non accessible. Assurez-vous qu'il est démarré sur le port 8000.")
            exit(1)
        
        print("✅ Serveur accessible")
        
        # Exécuter les tests
        test_session_workflow()
        test_without_session()
        
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur.")
        print("   Assurez-vous que le serveur est démarré avec: python main.py")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")