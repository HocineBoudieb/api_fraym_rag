# Fraym RAG System avec LangChain

Système de Recherche et Génération Augmentée par Récupération (RAG) utilisant LangChain, ChromaDB et OpenAI.

## 🚀 Fonctionnalités

- **RAG avec LangChain** : Utilisation du framework LangChain pour une architecture modulaire
- **Embeddings OpenAI** : Modèle `text-embedding-3-small` pour des embeddings de haute qualité
- **LLM GPT-4o-mini** : Génération de réponses intelligentes et contextuelles
- **ChromaDB** : Base de données vectorielle performante
- **API FastAPI** : Interface REST moderne et documentée
- **Chunking intelligent** : Division automatique des documents avec RecursiveCharacterTextSplitter
- **Support multi-formats** : Markdown, texte et JSON

## 📋 Prérequis

- Python 3.9+
- Clé API OpenAI
- uv (gestionnaire de paquets Python)

## 🛠️ Installation

1. **Cloner le projet**
```bash
git clone <repository-url>
cd test_dev
```

2. **Installer les dépendances**
```bash
uv sync
```

3. **Configuration**
Créer un fichier `.env` avec votre clé API OpenAI :
```bash
cp .env.example .env
# Éditer .env et ajouter votre OPENAI_API_KEY
```

## 🚀 Démarrage rapide

### 1. Initialiser la base de connaissances

```bash
uv run python init_knowledge_base.py
```

Ce script va :
- Charger tous les documents du dossier `knowledges/`
- Les diviser en chunks intelligents
- Créer les embeddings avec OpenAI
- Sauvegarder dans ChromaDB

### 2. Démarrer l'API

```bash
uv run python main.py
```

L'API sera disponible sur `http://localhost:8000`

### 3. Tester le système

```bash
uv run python test_rag.py
```

## 📚 Structure du projet

```
.
├── main.py                 # API FastAPI principale
├── init_knowledge_base.py  # Script d'initialisation
├── test_rag.py            # Script de test
├── knowledges/            # Documents à indexer
│   ├── product_catalog.md
│   ├── faq.md
│   ├── customer_service.md
│   └── ...
├── chroma_langchain_db/   # Base ChromaDB (créée automatiquement)
├── .env                   # Variables d'environnement
└── pyproject.toml         # Dépendances
```

## 🔧 Configuration

### Variables d'environnement (.env)

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Paramètres du système

- **Modèle embedding** : `text-embedding-3-small`
- **Modèle LLM** : `gpt-4o-mini`
- **Taille des chunks** : 1000 caractères
- **Overlap** : 200 caractères
- **Résultats par défaut** : 5 documents

## 📖 Utilisation de l'API

### Endpoints principaux

#### GET `/`
Informations sur l'API

#### GET `/health`
Vérification de l'état du système

#### POST `/query`
Effectuer une requête sur la base de connaissances

```json
{
  "query": "Quels produits sont disponibles ?",
  "max_results": 5,
  "temperature": 0.7
}
```

Réponse :
```json
{
  "answer": "Voici les produits disponibles...",
  "sources": [
    {
      "content": "Extrait du document...",
      "metadata": {"source": "product_catalog.md"},
      "source": "product_catalog.md"
    }
  ],
  "metadata": {
    "total_sources": 3,
    "query": "Quels produits sont disponibles ?"
  }
}
```

#### POST `/reload`
Recharger la base de connaissances

#### GET `/info`
Informations détaillées sur le système

### Documentation interactive

Accédez à `http://localhost:8000/docs` pour la documentation Swagger interactive.

## 🧪 Tests

### Test automatique
```bash
uv run python test_rag.py
```

### Test manuel avec curl
```bash
# Test de santé
curl http://localhost:8000/health

# Requête simple
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Quels sont les produits disponibles ?"}'
```

## 🔍 Architecture LangChain

### Composants utilisés

1. **Document Loaders** : `DirectoryLoader` + `TextLoader`
2. **Text Splitter** : `RecursiveCharacterTextSplitter`
3. **Embeddings** : `OpenAIEmbeddings`
4. **Vector Store** : `Chroma`
5. **LLM** : `ChatOpenAI`
6. **Chain** : `RetrievalQA`

### Flux de traitement

1. **Chargement** : Les documents sont chargés depuis `knowledges/`
2. **Chunking** : Division en chunks avec overlap
3. **Embedding** : Conversion en vecteurs avec OpenAI
4. **Stockage** : Sauvegarde dans ChromaDB
5. **Requête** : Recherche par similarité + génération de réponse
6. **Réponse** : Réponse contextuelle avec sources

## 📊 Monitoring

### Logs
Les logs sont affichés dans la console avec différents niveaux :
- `INFO` : Opérations normales
- `WARNING` : Avertissements
- `ERROR` : Erreurs

### Métriques
- Nombre de documents indexés
- Temps de réponse des requêtes
- Sources utilisées par requête

## 🔧 Personnalisation

### Modifier le prompt
Éditez le `prompt_template` dans `main.py` :

```python
prompt_template = """
Votre prompt personnalisé ici...

Contexte:
{context}

Question: {question}

Réponse:"""
```

### Changer les paramètres de chunking
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,  # Taille des chunks
    chunk_overlap=300,  # Overlap
    separators=["\n\n", "\n", ". ", " ", ""]
)
```

### Modifier la recherche
```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 10}  # Nombre de documents
)
```

## 🐛 Dépannage

### Erreurs communes

1. **Clé API manquante**
   ```
   ValueError: OPENAI_API_KEY non trouvée
   ```
   → Vérifiez votre fichier `.env`

2. **Dossier knowledges vide**
   ```
   Aucun document trouvé
   ```
   → Ajoutez des fichiers `.md` ou `.txt` dans `knowledges/`

3. **Erreur ChromaDB**
   ```
   Erreur lors du chargement de la base vectorielle
   ```
   → Supprimez le dossier `chroma_langchain_db/` et réinitialisez

### Reset complet
```bash
# Supprimer la base
rm -rf chroma_langchain_db/

# Réinitialiser
uv run python init_knowledge_base.py
```

## 📈 Performance

### Optimisations
- Utilisation de `text-embedding-3-small` (plus rapide que `text-embedding-ada-002`)
- Chunking intelligent avec overlap
- Cache des embeddings dans ChromaDB
- Recherche vectorielle optimisée

### Limites
- Dépendant de l'API OpenAI (latence réseau)
- Coût des embeddings et du LLM
- Taille maximale des chunks (contexte LLM)

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature
3. Commit les changements
4. Push vers la branche
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.