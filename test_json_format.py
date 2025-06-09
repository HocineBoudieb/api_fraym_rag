#!/usr/bin/env python3
"""
Script de test pour vérifier que l'IA répond au format JSON spécifié
"""

import requests
import json
import sys

def test_json_response():
    """Teste si l'IA répond au format JSON correct"""
    
    # URL de l'API
    url = "http://localhost:8000/query"
    
    # Questions de test
    test_queries = [
        "Montre-moi la liste des produits disponibles",
        "Créer une page d'accueil pour notre boutique",
        "Affiche les smartphones disponibles",
        "Créer un tableau de bord pour les ventes"
    ]
    
    print("🧪 Test du format JSON de réponse...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"📝 Test {i}: {query}")
        
        try:
            # Faire la requête
            response = requests.post(url, json={
                "query": query,
                "max_results": 5,
                "temperature": 0.7
            })
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                
                print(f"📤 Réponse reçue: {len(answer)} caractères")
                
                # Essayer de parser la réponse comme JSON
                try:
                    json_response = json.loads(answer)
                    
                    # Vérifier la structure requise
                    required_fields = ['template', 'components']
                    missing_fields = [field for field in required_fields if field not in json_response]
                    
                    if missing_fields:
                        print(f"❌ Champs manquants: {missing_fields}")
                    else:
                        print("✅ Structure JSON valide!")
                        
                        # Afficher un aperçu de la structure
                        template = json_response.get('template')
                        components_count = len(json_response.get('components', []))
                        print(f"   📋 Template: {template}")
                        print(f"   🧩 Composants: {components_count}")
                        
                        # Vérifier les composants
                        components = json_response.get('components', [])
                        if components:
                            component_types = [comp.get('type') for comp in components if isinstance(comp, dict)]
                            print(f"   🏷️ Types: {', '.join(set(component_types))}")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Erreur de parsing JSON: {e}")
                    print(f"📄 Début de la réponse: {answer[:200]}...")
                
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Impossible de se connecter au serveur. Assurez-vous qu'il est démarré.")
            return False
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        print("-" * 50)
    
    return True

def test_specific_json_structure():
    """Teste une requête spécifique et affiche le JSON complet"""
    
    url = "http://localhost:8000/query"
    query = "Créer une page qui affiche tous nos produits en grille"
    
    print(f"🔍 Test détaillé avec: {query}\n")
    
    try:
        response = requests.post(url, json={
            "query": query,
            "max_results": 5,
            "temperature": 0.7
        })
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', '')
            
            try:
                json_response = json.loads(answer)
                print("📋 JSON généré:")
                print(json.dumps(json_response, indent=2, ensure_ascii=False))
                
                # Validation détaillée
                print("\n🔍 Validation:")
                
                # Vérifier template
                template = json_response.get('template')
                valid_templates = ['base', 'centered', 'grid', 'dashboard', 'landing']
                if template in valid_templates:
                    print(f"✅ Template valide: {template}")
                else:
                    print(f"❌ Template invalide: {template}")
                
                # Vérifier components
                components = json_response.get('components', [])
                if isinstance(components, list) and len(components) > 0:
                    print(f"✅ Composants présents: {len(components)}")
                    
                    for i, comp in enumerate(components):
                        if isinstance(comp, dict) and 'type' in comp:
                            comp_type = comp['type']
                            props = comp.get('props', {})
                            print(f"   {i+1}. {comp_type} (props: {len(props)})")
                        else:
                            print(f"   {i+1}. ❌ Composant mal formé")
                else:
                    print("❌ Aucun composant trouvé")
                
                # Vérifier templateProps
                template_props = json_response.get('templateProps')
                if template_props:
                    print(f"✅ TemplateProps présent: {list(template_props.keys())}")
                else:
                    print("ℹ️ TemplateProps optionnel absent")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Erreur JSON: {e}")
                print(f"📄 Réponse brute:\n{answer}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🚀 Test du format JSON pour le système de rendu de composants\n")
    
    # Test général
    test_json_response()
    
    print("\n" + "=" * 60 + "\n")
    
    # Test détaillé
    test_specific_json_structure()
    
    print("\n✨ Tests terminés!")