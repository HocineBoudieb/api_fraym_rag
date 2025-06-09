# Documentation du Système de Sessions

## Vue d'ensemble

Le système RAG a été enrichi avec un système de gestion de sessions et d'historique de conversations utilisant SQLite. Chaque conversation peut maintenant être organisée en sessions persistantes, permettant de maintenir le contexte entre les questions.

## Fonctionnalités

### 1. Gestion des Sessions
- **Création automatique** : Si aucun `session_id` n'est fourni, une nouvelle session est créée automatiquement
- **Création manuelle** : Possibilité de créer des sessions avec un titre personnalisé
- **Persistance** : Les sessions sont stockées dans une base de données SQLite (`sessions.db`)
- **Métadonnées** : Chaque session contient un titre, une date de création et un compteur de messages

### 2. Historique des Conversations
- **Stockage complet** : Tous les messages (utilisateur et assistant) sont sauvegardés
- **Métadonnées enrichies** : Chaque message contient des informations sur la méthode de recherche utilisée
- **Contexte intelligent** : Les 5 derniers messages sont automatiquement inclus dans le prompt pour maintenir le contexte
- **Horodatage** : Chaque message est horodaté pour un suivi précis

### 3. Intégration avec le RAG
- **Prompt enrichi** : L'historique de conversation est automatiquement intégré dans les prompts
- **Cohérence** : Le format JSON est maintenu même avec l'historique
- **Performance** : Optimisation pour éviter les prompts trop longs (limite à 5 messages récents)

## API Endpoints

### Sessions

#### `POST /sessions`
Crée une nouvelle session de conversation.

**Body:**
```json
{
  "title": "Ma session de test"
}
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "title": "Ma session de test",
  "created_at": "2024-01-01T12:00:00",
  "message_count": 0
}
```

#### `GET /sessions`
Liste toutes les sessions existantes.

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "uuid-string",
      "title": "Ma session",
      "created_at": "2024-01-01T12:00:00",
      "message_count": 5
    }
  ]
}
```

#### `GET /sessions/{session_id}/history`
Récupère l'historique complet d'une session.

**Response:**
```json
{
  "session_id": "uuid-string",
  "messages": [
    {
      "role": "user",
      "content": "Quels sont vos produits?",
      "timestamp": "2024-01-01T12:00:00",
      "metadata": {}
    },
    {
      "role": "assistant",
      "content": "{\"template\": \"ProductList\", ...}",
      "timestamp": "2024-01-01T12:00:01",
      "metadata": {
        "search_method": "tag_based",
        "sources_count": 3
      }
    }
  ]
}
```

#### `PUT /sessions/{session_id}`
Met à jour le titre d'une session.

**Body:**
```json
{
  "title": "Nouveau titre"
}
```

#### `DELETE /sessions/{session_id}`
Supprime une session et tout son historique.

### Requêtes avec Sessions

#### `POST /query`
Effectue une requête avec support de session (modifié).

**Body:**
```json
{
  "query": "Votre question",
  "session_id": "uuid-string",  // Optionnel
  "max_results": 5
}
```

**Response:**
```json
{
  "answer": "{\"template\": \"Response\", ...}",
  "sources": [...],
  "metadata": {...},
  "session_id": "uuid-string"  // Nouveau champ
}
```

## Structure de la Base de Données

### Table `sessions`
```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Table `messages`
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
);
```

## Utilisation

### Exemple 1: Conversation Simple
```python
import requests

# 1. Créer une session
response = requests.post("http://localhost:8000/sessions", json={
    "title": "Questions sur les produits"
})
session_id = response.json()["session_id"]

# 2. Poser des questions
response = requests.post("http://localhost:8000/query", json={
    "query": "Quels sont vos produits disponibles?",
    "session_id": session_id
})

# 3. Question de suivi (avec contexte automatique)
response = requests.post("http://localhost:8000/query", json={
    "query": "Quel est le prix du premier produit?",
    "session_id": session_id
})
```

### Exemple 2: Sans Session (Création Automatique)
```python
# La session sera créée automatiquement
response = requests.post("http://localhost:8000/query", json={
    "query": "Comment vous contacter?"
})
session_id = response.json()["session_id"]
```

## Avantages

1. **Contexte Persistant** : Les conversations maintiennent leur contexte entre les questions
2. **Organisation** : Les conversations peuvent être organisées et retrouvées facilement
3. **Historique Complet** : Toutes les interactions sont sauvegardées
4. **Performance** : Optimisation intelligente du contexte pour éviter les prompts trop longs
5. **Flexibilité** : Fonctionne avec ou sans session explicite
6. **Métadonnées Riches** : Informations détaillées sur chaque interaction

## Configuration

Le système utilise les paramètres suivants (configurables dans `session_manager.py`):

- **Base de données** : `sessions.db` (SQLite)
- **Contexte maximum** : 5 derniers messages
- **Nettoyage automatique** : Sessions de plus de 30 jours (optionnel)
- **Titre par défaut** : "Nouvelle conversation"

## Test

Utilisez le script de test fourni :

```bash
python test_sessions.py
```

Ce script teste :
- Création de session
- Requêtes avec contexte
- Récupération d'historique
- Gestion des sessions
- Création automatique de session