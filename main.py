import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import du gestionnaire de sessions
from session_manager import SessionManager

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.prompts import PromptTemplate

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

app = FastAPI(
    title="Fraym RAG API avec LangChain",
    description="API de recherche et génération augmentée par récupération utilisant LangChain et ChromaDB",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles Pydantic
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    max_results: int = 5
    temperature: float = 0.7

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    session_id: Optional[str] = None

class DocumentInfo(BaseModel):
    filename: str
    content_preview: str
    chunk_count: int
    metadata: Dict[str, Any]

# Modèles pour les sessions
class SessionCreate(BaseModel):
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int
    metadata: Dict[str, Any]

class SessionUpdate(BaseModel):
    title: str

class MessageResponse(BaseModel):
    id: int
    timestamp: str
    role: str
    content: str
    metadata: Dict[str, Any]

# Configuration globale
class RAGSystem:
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self.qa_chain = None
        self.text_splitter = None
        self.knowledge_base_path = Path("knowledges")
        self.chroma_db_path = "./chroma_langchain_db"
        
        # Initialiser le gestionnaire de sessions
        self.session_manager = SessionManager("sessions.db")
        
        # Initialiser les composants
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialise les composants LangChain"""
        try:
            # Vérifier la clé API OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY non trouvée dans les variables d'environnement")
            
            # Initialiser les embeddings
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=api_key,
                model="text-embedding-3-small"
            )
            
            # Initialiser le LLM
            self.llm = ChatOpenAI(
                openai_api_key=api_key,
                model="gpt-4o-mini",
                temperature=0.7
            )
            
            # Initialiser le text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            # Charger ou créer la base vectorielle
            self._load_or_create_vectorstore()
            
            # Créer la chaîne QA
            self._create_qa_chain()
            
            logger.info("✅ Système RAG initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation: {e}")
            raise
    
    def _load_or_create_vectorstore(self):
        """Charge ou crée la base vectorielle ChromaDB"""
        try:
            # Essayer de charger une base existante
            if os.path.exists(self.chroma_db_path):
                self.vectorstore = Chroma(
                    persist_directory=self.chroma_db_path,
                    embedding_function=self.embeddings
                )
                logger.info(f"📚 Base vectorielle chargée depuis {self.chroma_db_path}")
            else:
                # Créer une nouvelle base
                self.vectorstore = Chroma(
                    persist_directory=self.chroma_db_path,
                    embedding_function=self.embeddings
                )
                logger.info(f"🆕 Nouvelle base vectorielle créée dans {self.chroma_db_path}")
                
                # Charger les documents si le dossier knowledges existe
                if self.knowledge_base_path.exists():
                    self.load_knowledge_base()
                    
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement de la base vectorielle: {e}")
            raise
    
    def _create_qa_chain(self):
        """Crée la chaîne de question-réponse"""
        # Template de prompt personnalisé pour générer du JSON selon le guide
        prompt_template = """
Tu es un assistant e-commerce spécialisé qui génère des interfaces utilisateur dynamiques. Tu dois TOUJOURS répondre avec un JSON valide selon la structure définie dans le Guide de Structure JSON pour le Système de Rendu de Composants.

INSTRUCTIONS OBLIGATOIRES :
- Ta réponse DOIT être un JSON valide avec la structure : {{"template": "...", "components": [...], "templateProps": {{...}}}}
- Utilise les templates disponibles : "base", "centered", "grid", "dashboard", "landing"
- Utilise les composants appropriés : "Heading", "Text", "Button", "Card", "Grid", "ProductCard", "Container", "Navigation", etc.
- Pour les listes de produits : utilise "Grid" avec des "ProductCard"
- Pour les pages simples : utilise "centered" avec "Heading" et "Text"
- Pour les tableaux de bord : utilise "dashboard"
- Applique les classes Tailwind CSS appropriées
- Assure-toi que le JSON est syntaxiquement correct

STRUCTURE COHÉRENTE DES COMPOSANTS :
- TOUJOURS générer EXACTEMENT 6 composants dans cet ordre :
  1. Heading (titre principal ou message de bienvenue)
  2. ZaraCategoryButtons (boutons de catégories)
  3. Text (texte descriptif ou question)
  4. Grid avec ProductCard OU ZaraProductGrid (produits)
- Maintenir cette structure pour TOUTES les réponses
- Adapter uniquement le contenu, pas la structure

RÈGLES STRICTES POUR LES PRODUITS :
- Tu NE DOIS JAMAIS inventer ou créer de nouveaux produits
- Tu DOIS UNIQUEMENT utiliser les produits, prix et informations présents dans le contexte fourni
- Si un produit n'existe pas dans le contexte, tu DOIS dire qu'il n'est pas disponible
- Tu NE DOIS PAS inventer de prix, de caractéristiques ou de descriptions
- Reste fidèle aux informations exactes du catalogue fourni

Contexte:
{context}

Question: {question}

Réponds UNIQUEMENT avec un JSON valide selon le guide de structure, en utilisant SEULEMENT les produits du contexte :"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Créer la chaîne QA avec retriever amélioré
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": 10  # Récupérer plus de documents pour avoir plus d'informations
                }
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
    
    def load_knowledge_base(self):
        """Charge tous les documents du dossier knowledges"""
        try:
            if not self.knowledge_base_path.exists():
                logger.warning(f"📁 Dossier {self.knowledge_base_path} non trouvé")
                return
            
            # Charger tous les fichiers markdown, texte et JSON
            loader = DirectoryLoader(
                str(self.knowledge_base_path),
                glob="**/*.{md,txt,json}",
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8"}
            )
            
            documents = loader.load()
            logger.info(f"📄 {len(documents)} documents chargés")
            
            if documents:
                # Diviser les documents en chunks
                texts = self.text_splitter.split_documents(documents)
                
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
                
                logger.info(f"✂️ {len(texts)} chunks créés avec métadonnées enrichies")
                
                # Ajouter à la base vectorielle
                self.vectorstore.add_documents(texts)
                self.vectorstore.persist()
                
                logger.info(f"✅ Base de connaissances chargée: {len(texts)} chunks indexés")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement de la base de connaissances: {e}")
            raise
    
    def detect_scenario(self, query: str, found_docs: List[Document]) -> str:
        """
        Détecte le scénario approprié basé sur la requête et les documents trouvés
        """
        query_lower = query.lower()
        
        # Mots-clés par scénario
        ecommerce_keywords = ['produit', 'acheter', 'prix', 'catalogue', 'recommandation', 'commander', 'panier']
        single_product_keywords = ['détails', 'spécifications', 'caractéristiques', 'fiche produit', 'plus d\'infos', 'description complète']
        restaurant_keywords = ['menu', 'plat', 'restaurant', 'réserver', 'carte', 'table', 'cuisine']
        support_keywords = ['aide', 'problème', 'retour', 'livraison', 'garantie', 'support', 'contact']
        comparison_keywords = ['comparer', 'différence', 'vs', 'versus', 'mieux', 'choisir']
        landing_keywords = ['bonjour', 'salut', 'hello', 'bienvenue', 'aide-moi', 'que faire']
        
        # Vérifier les tags dans les documents
        doc_tags = set()
        for doc in found_docs:
            if 'tags' in doc.metadata:
                if isinstance(doc.metadata['tags'], list):
                    doc_tags.update(doc.metadata['tags'])
                else:
                    doc_tags.add(doc.metadata['tags'])
        
        # Logique de détection par priorité
        
        # 1. Produit unique avec détails
        if ('product' in doc_tags or 'ecommerce' in doc_tags) and \
           (any(keyword in query_lower for keyword in single_product_keywords) or \
            len(found_docs) == 1):
            return 'single_product'
        
        # 2. Produits E-commerce (liste)
        if ('product' in doc_tags or 'ecommerce' in doc_tags) and \
           any(keyword in query_lower for keyword in ecommerce_keywords):
            return 'ecommerce_products'
        
        # 3. Restaurant
        if ('restaurant' in doc_tags or 'menu' in doc_tags) or \
           any(keyword in query_lower for keyword in restaurant_keywords):
            return 'restaurant_menu'
        
        # 4. Support/FAQ
        if ('support' in doc_tags or 'faq' in doc_tags) or \
           any(keyword in query_lower for keyword in support_keywords):
            return 'customer_support'
        
        # 5. Comparaison (si plusieurs produits et mots-clés de comparaison)
        if any(keyword in query_lower for keyword in comparison_keywords) and \
           len(found_docs) > 1 and 'product' in doc_tags:
            return 'product_comparison'
        
        # 6. Landing/Accueil
        if any(keyword in query_lower for keyword in landing_keywords) or \
           len(query.strip()) < 20:  # Requêtes courtes = orientation
            return 'landing_page'
        
        # 7. Par défaut : informatif
        return 'informative'
    
    def get_scenario_prompt(self, scenario: str, session_context: str, context: str, question: str) -> str:
        """
        Retourne le prompt adapté au scénario détecté
        """
        base_instructions = """
Tu es un assistant e-commerce spécialisé qui génère des interfaces utilisateur dynamiques. Tu dois TOUJOURS répondre avec un JSON valide selon la structure définie dans le Guide de Structure JSON pour le Système de Rendu de Composants.

INSTRUCTIONS OBLIGATOIRES :
- Ta réponse DOIT être un JSON valide avec la structure : {{"template": "...", "components": [...], "templateProps": {{...}}}}
- Utilise les templates disponibles : "base", "centered", "grid", "dashboard", "landing"
- Utilise les composants appropriés selon le scénario
- Applique les classes Tailwind CSS appropriées
- Assure-toi que le JSON est syntaxiquement correct
- Prends en compte l'historique de la conversation pour maintenir la cohérence
"""
        
        scenario_prompts = {
            'single_product': f"""{base_instructions}

SCÉNARIO : PRODUIT UNIQUE - FICHE DÉTAILLÉE
- Utilise le template "centered" pour une présentation focalisée
- Structure recommandée : Heading → ProductCard détaillée → Text complémentaires → Button d'action
- Mets en avant TOUS les détails du produit unique :
  * Nom, prix, description complète
  * Spécifications techniques détaillées
  * Caractéristiques importantes
  * Informations de disponibilité
- Ajoute des informations sur la livraison, garantie, service après-vente
- Inclus un appel à l'action clair ("Ajouter au panier", "Commander")
- Optimise pour la conversion sur ce produit spécifique

RÈGLES STRICTES POUR LES PRODUITS :
- Tu NE DOIS JAMAIS inventer ou créer de nouveaux produits
- Tu DOIS UNIQUEMENT utiliser les produits, prix et informations présents dans le contexte fourni
- Si un produit n'existe pas dans le contexte, tu DOIS dire qu'il n'est pas disponible

Historique de la conversation:
{session_context}

Contexte du produit:
{context}

Question actuelle: {question}

Réponds UNIQUEMENT avec un JSON valide selon le guide de structure :""",
            
            'ecommerce_products': f"""{base_instructions}

SCÉNARIO : AFFICHAGE DE PRODUITS E-COMMERCE
- Utilise le template "grid" pour une présentation optimale des produits
- Structure recommandée : Heading → Text descriptif → Grid avec ProductCard → Text de suivi/CTA
- Mets en avant les produits avec leurs caractéristiques et prix
- Inclus des appels à l'action pour l'achat
- Optimise pour la conversion

RÈGLES STRICTES POUR LES PRODUITS :
- Tu NE DOIS JAMAIS inventer ou créer de nouveaux produits
- Tu DOIS UNIQUEMENT utiliser les produits, prix et informations présents dans le contexte fourni
- Si un produit n'existe pas dans le contexte, tu DOIS dire qu'il n'est pas disponible

Historique de la conversation:
{session_context}

Contexte des produits:
{context}

Question actuelle: {question}

Réponds UNIQUEMENT avec un JSON valide selon le guide de structure :""",
            
            'restaurant_menu': f"""{base_instructions}

SCÉNARIO : MENU RESTAURANT
- Utilise le template "centered" ou "grid" selon le contenu
- Structure recommandée : Heading → Grid avec Cards pour les plats → Button de réservation
- Mets en avant les spécialités et informations pratiques
- Inclus les informations de contact et réservation

Historique de la conversation:
{session_context}

Contexte restaurant:
{context}

Question actuelle: {question}

Réponds UNIQUEMENT avec un JSON valide selon le guide de structure :""",
            
            'customer_support': f"""{base_instructions}

SCÉNARIO : SERVICE CLIENT / SUPPORT
- Utilise le template "centered" pour une lecture facile
- Structure recommandée : Heading → Card avec réponse détaillée → Text + Button de contact
- Priorise la clarté et l'aide pratique
- Inclus les informations de contact si pertinent

Historique de la conversation:
{session_context}

Contexte support:
{context}

Question actuelle: {question}

Réponds UNIQUEMENT avec un JSON valide selon le guide de structure :""",
            
            'product_comparison': f"""{base_instructions}

SCÉNARIO : COMPARAISON DE PRODUITS
- Utilise le template "grid" pour comparer côte à côte
- Structure recommandée : Heading → Grid avec Cards de comparaison → Text de recommandation
- Mets en évidence les différences clés
- Conclus avec une recommandation basée sur les besoins

Historique de la conversation:
{session_context}

Contexte des produits à comparer:
{context}

Question actuelle: {question}

Réponds UNIQUEMENT avec un JSON valide selon le guide de structure :""",
            
            'landing_page': f"""{base_instructions}

SCÉNARIO : PAGE D'ACCUEIL / ORIENTATION
- Utilise le template "landing" pour un accueil chaleureux
- Structure recommandée : Heading de bienvenue → Text d'orientation → Grid avec options d'action
- Propose des directions claires vers les principales fonctionnalités
- Crée une expérience d'onboarding fluide

Historique de la conversation:
{session_context}

Contexte général:
{context}

Question actuelle: {question}

Réponds UNIQUEMENT avec un JSON valide selon le guide de structure :""",
            
            'informative': f"""{base_instructions}

SCÉNARIO : RÉPONSE INFORMATIVE
- Utilise le template "centered" pour une présentation claire
- Structure recommandée : Heading → Text/Card avec information → Text de suivi si nécessaire
- Priorise la clarté et la pertinence de l'information
- Garde une structure simple et lisible

Historique de la conversation:
{session_context}

Contexte:
{context}

Question actuelle: {question}

Réponds UNIQUEMENT avec un JSON valide selon le guide de structure :"""
        }
        
        return scenario_prompts.get(scenario, scenario_prompts['informative'])
    
    def get_chunks_by_tag(self, tag: str, limit: int = 10) -> List[Document]:
        """Récupère les chunks ayant un tag spécifique"""
        try:
            collection = self.vectorstore._collection
            # Récupérer tous les documents et filtrer manuellement
            results = collection.get(
                include=["documents", "metadatas"]
            )
            
            filtered_docs = []
            for i, metadata in enumerate(results.get('metadatas', [])):
                if metadata and 'tags' in metadata:
                    tags_str = metadata['tags']
                    if tag in tags_str.split(','):
                        doc = Document(
                            page_content=results['documents'][i],
                            metadata=metadata
                        )
                        filtered_docs.append(doc)
                        if len(filtered_docs) >= limit:
                            break
            
            return filtered_docs
        except Exception as e:
            logger.error(f"Erreur lors de la récupération par tag: {e}")
            return []
    
    def query(self, question: str, session_id: str = None, max_results: int = 5) -> Dict[str, Any]:
        """Effectue une requête sur la base de connaissances avec logique améliorée et gestion de session"""
        try:
            if not self.qa_chain:
                raise ValueError("Système QA non initialisé")
            
            # Créer une session si nécessaire
            if not session_id:
                session_id = self.session_manager.create_session()
                logger.info(f"🆕 Nouvelle session créée: {session_id}")
            
            # Enregistrer la question de l'utilisateur
            self.session_manager.add_message(session_id, "user", question)
            
            # Récupérer le contexte de la session
            session_context = self.session_manager.get_session_context(session_id, max_messages=5)
            
            question_lower = question.lower()
            
            # Détecter si la question concerne les produits (logique élargie)
            product_keywords = [
                # Mots directs
                'produit', 'product', 'liste', 'catalog', 'catalogue', 'disponible', 'prix',
                # Produits spécifiques
                'smartphone', 'ordinateur', 'iphone', 'samsung', 'macbook', 'airpods', 'dell',
                # Actions d'achat/recommandation
                'acheter', 'achat', 'buy', 'purchase', 'commander', 'order',
                'cadeau', 'cadeaux', 'gift', 'offrir', 'offer',
                'proposer', 'propose', 'recommander', 'recommend', 'suggérer', 'suggest',
                'cherche', 'search', 'trouve', 'find', 'besoin', 'need', 'veux', 'want',
                # Contextes commerciaux
                'boutique', 'magasin', 'shop', 'store', 'vendre', 'sell', 'vente', 'sale',
                'choisir', 'choose', 'sélectionner', 'select', 'comparer', 'compare',
                # Termes généraux qui impliquent souvent des produits
                'que me', 'qu\'avez', 'avez-vous', 'do you have', 'what do you',
                'me conseillez', 'me proposez', 'me recommandez'
            ]
            is_product_query = any(keyword in question_lower for keyword in product_keywords)
            
            if is_product_query:
                # Pour les questions sur les produits, récupérer tous les chunks avec tag 'product'
                logger.info("🏷️ Requête produit détectée - récupération par tag")
                product_docs = self.get_chunks_by_tag('product', limit=15)
                
                if product_docs:
                    # Détecter le scénario approprié
                    scenario = self.detect_scenario(question, product_docs)
                    logger.info(f"📋 Scénario détecté: {scenario}")
                    
                    # Créer un contexte spécialisé pour les produits
                    context = "\n\n".join([doc.page_content for doc in product_docs])
                    
                    # Obtenir le prompt adapté au scénario
                    formatted_prompt = self.get_scenario_prompt(scenario, session_context, context, question)
                    
                    # Générer la réponse
                    response = self.llm.invoke(formatted_prompt)
                    answer = response.content if hasattr(response, 'content') else str(response)
                    
                    # Enregistrer la réponse de l'assistant
                    self.session_manager.add_message(session_id, "assistant", answer, {
                        "search_method": "tag_based",
                        "tag_used": "product",
                        "scenario": scenario,
                        "sources_count": len(product_docs)
                    })
                    
                    # Formater les sources
                    sources = []
                    for doc in product_docs:
                        sources.append({
                            "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                            "metadata": doc.metadata,
                            "source": doc.metadata.get("source", "Unknown")
                        })
                    
                    return {
                        "answer": answer,
                        "sources": sources,
                        "session_id": session_id,
                        "metadata": {
                            "total_sources": len(product_docs),
                            "query": question,
                            "search_method": "tag_based",
                            "scenario": scenario,
                            "tag_used": "product"
                        }
                    }
            
            # Pour les autres questions, utiliser la recherche par similarité normale
            logger.info("🔍 Requête générale - recherche par similarité")
            
            # Modifier le prompt pour inclure l'historique de session
            if session_context:
                # Créer un prompt enrichi avec l'historique
                enriched_query = f"Historique de la conversation:\n{session_context}\n\nQuestion actuelle: {question}"
                result = self.qa_chain({"query": enriched_query})
            else:
                result = self.qa_chain({"query": question})
            
            answer = result["result"]
            sources_found = result.get("source_documents", [])
            
            # Détecter le scénario pour les réponses générales
            scenario = self.detect_scenario(question, sources_found)
            logger.info(f"📋 Scénario général détecté: {scenario}")
            
            # Si le scénario détecté nécessite un format JSON spécifique, régénérer la réponse
            if scenario in ['restaurant_menu', 'customer_support', 'landing_page', 'product_comparison']:
                context = "\n\n".join([doc.page_content for doc in sources_found]) if sources_found else "Aucun contexte spécifique trouvé."
                formatted_prompt = self.get_scenario_prompt(scenario, session_context, context, question)
                
                # Régénérer avec le format adapté
                response = self.llm.invoke(formatted_prompt)
                answer = response.content if hasattr(response, 'content') else str(response)
            
            # Logique de fallback : si peu de sources trouvées et que la question pourrait concerner des recommandations
            fallback_keywords = ['recommand', 'conseil', 'suggest', 'propose', 'que faire', 'quoi', 'help', 'aide']
            should_try_products = (
                len(sources_found) < 3 and 
                any(keyword in question_lower for keyword in fallback_keywords)
            )
            
            if should_try_products:
                logger.info("🔄 Fallback - tentative de recherche dans les produits")
                product_docs = self.get_chunks_by_tag('product', limit=10)
                
                if product_docs and len(product_docs) > len(sources_found):
                    # Détecter le scénario approprié pour le fallback
                    scenario = self.detect_scenario(question, product_docs)
                    logger.info(f"📋 Scénario fallback détecté: {scenario}")
                    
                    # Utiliser les produits comme sources supplémentaires
                    context = "\n\n".join([doc.page_content for doc in product_docs])
                    
                    # Obtenir le prompt adapté au scénario
                    formatted_prompt = self.get_scenario_prompt(scenario, session_context, context, question)
                    
                    # Générer la réponse avec les produits
                    response = self.llm.invoke(formatted_prompt)
                    answer = response.content if hasattr(response, 'content') else str(response)
                    
                    # Enregistrer la réponse de l'assistant
                    self.session_manager.add_message(session_id, "assistant", answer, {
                        "search_method": "fallback_products",
                        "scenario": scenario,
                        "sources_count": len(product_docs)
                    })
                    
                    # Formater les sources avec les produits
                    sources = []
                    for doc in product_docs:
                        sources.append({
                            "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                            "metadata": doc.metadata,
                            "source": doc.metadata.get("source", "Unknown")
                        })
                    
                    return {
                        "answer": answer,
                        "sources": sources,
                        "session_id": session_id,
                        "metadata": {
                            "total_sources": len(product_docs),
                            "query": question,
                            "search_method": "fallback_products",
                            "scenario": scenario
                        }
                    }
            
            # Enregistrer la réponse de l'assistant (recherche normale)
            self.session_manager.add_message(session_id, "assistant", answer, {
                "search_method": "similarity",
                "scenario": scenario,
                "sources_count": len(sources_found)
            })
            
            # Formater les sources
            sources = []
            for doc in sources_found:
                sources.append({
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata,
                    "source": doc.metadata.get("source", "Unknown")
                })
            
            return {
                "answer": answer,
                "sources": sources[:max_results],
                "session_id": session_id,
                "metadata": {
                    "total_sources": len(sources_found),
                    "query": question,
                    "search_method": "similarity",
                    "scenario": scenario
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la requête: {e}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Retourne des informations sur la collection"""
        try:
            if not self.vectorstore:
                return {"status": "not_initialized", "count": 0}
            
            # Obtenir le nombre de documents
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                "status": "ready",
                "count": count,
                "embedding_model": "text-embedding-3-small",
                "llm_model": "gpt-4o-mini"
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des infos: {e}")
            return {"status": "error", "error": str(e)}

# Instance globale du système RAG
rag_system = RAGSystem()

# Routes API
@app.get("/")
async def root():
    return {
        "message": "Fraym RAG API avec LangChain",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    info = rag_system.get_collection_info()
    return {
        "status": "healthy",
        "vectorstore": info
    }

@app.post("/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """Effectue une requête sur la base de connaissances avec gestion de session"""
    try:
        result = rag_system.query(
            question=request.query,
            session_id=request.session_id,
            max_results=request.max_results
        )
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            metadata=result["metadata"],
            session_id=result["session_id"]
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la requête: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reload")
async def reload_knowledge_base():
    """Recharge la base de connaissances"""
    try:
        rag_system.load_knowledge_base()
        info = rag_system.get_collection_info()
        
        return {
            "status": "success",
            "message": "Base de connaissances rechargée",
            "info": info
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du rechargement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/info")
async def get_system_info():
    """Retourne des informations sur le système"""
    info = rag_system.get_collection_info()
    
    return {
        "system": "Fraym RAG avec LangChain",
        "vectorstore": info,
        "knowledge_path": str(rag_system.knowledge_base_path),
        "chroma_path": rag_system.chroma_db_path
    }

# Routes pour la gestion des sessions
@app.post("/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreate):
    """Crée une nouvelle session de conversation"""
    try:
        session_id = rag_system.session_manager.create_session(request.title)
        return SessionResponse(
            session_id=session_id,
            title=request.title,
            created_at=rag_system.session_manager.get_session_info(session_id)["created_at"],
            message_count=0
        )
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
async def list_sessions():
    """Liste toutes les sessions"""
    try:
        sessions = rag_system.session_manager.get_sessions()
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Récupère l'historique d'une session"""
    try:
        if not rag_system.session_manager.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        history = rag_system.session_manager.get_session_history(session_id)
        messages = []
        for msg in history:
            messages.append(MessageResponse(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["timestamp"],
                metadata=msg["metadata"]
            ))
        
        return {"session_id": session_id, "messages": messages}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération de l'historique: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/sessions/{session_id}")
async def update_session(session_id: str, request: SessionUpdate):
    """Met à jour le titre d'une session"""
    try:
        if not rag_system.session_manager.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        rag_system.session_manager.update_session_title(session_id, request.title)
        return {"message": "Session mise à jour avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la mise à jour de session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Supprime une session"""
    try:
        if not rag_system.session_manager.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        rag_system.session_manager.delete_session(session_id)
        return {"message": "Session supprimée avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression de session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)