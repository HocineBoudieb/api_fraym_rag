import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

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
    max_results: int = 5
    temperature: float = 0.7

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class DocumentInfo(BaseModel):
    filename: str
    content_preview: str
    chunk_count: int
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
        # Template de prompt personnalisé
        prompt_template = """
Tu es un assistant e-commerce spécialisé. Utilise le contexte suivant pour répondre à la question de manière précise et structurée.

INSTRUCTIONS SPÉCIALES :
- Pour les demandes de liste de produits : présente TOUS les produits disponibles avec leurs caractéristiques principales (nom, prix, spécifications clés)
- Pour les filtres (ex: "produits pas chers", "moins de X€") : analyse les prix et filtre automatiquement
- Pour les comparaisons : présente les différences clés entre les produits
- Utilise des listes à puces et une mise en forme claire
- Inclus toujours les prix quand disponibles
- Si des informations manquent, indique-le clairement

Contexte:
{context}

Question: {question}

Réponse structurée et détaillée:"""
        
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
    
    def query(self, question: str, max_results: int = 5) -> Dict[str, Any]:
        """Effectue une requête sur la base de connaissances avec logique améliorée"""
        try:
            if not self.qa_chain:
                raise ValueError("Système QA non initialisé")
            
            question_lower = question.lower()
            
            # Détecter si la question concerne les produits
            product_keywords = ['produit', 'product', 'liste', 'catalog', 'catalogue', 'disponible', 'prix', 'smartphone', 'ordinateur', 'iphone', 'samsung', 'macbook']
            is_product_query = any(keyword in question_lower for keyword in product_keywords)
            
            if is_product_query:
                # Pour les questions sur les produits, récupérer tous les chunks avec tag 'product'
                logger.info("🏷️ Requête produit détectée - récupération par tag")
                product_docs = self.get_chunks_by_tag('product', limit=15)
                
                if product_docs:
                    # Créer un contexte spécialisé pour les produits
                    context = "\n\n".join([doc.page_content for doc in product_docs])
                    
                    # Utiliser le prompt avec le contexte enrichi
                    prompt_template = self.qa_chain.combine_documents_chain.llm_chain.prompt
                    formatted_prompt = prompt_template.format(
                        context=context,
                        question=question
                    )
                    
                    # Générer la réponse
                    response = self.llm.invoke(formatted_prompt)
                    
                    # Formater les sources
                    sources = []
                    for doc in product_docs:
                        sources.append({
                            "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                            "metadata": doc.metadata,
                            "source": doc.metadata.get("source", "Unknown")
                        })
                    
                    return {
                        "answer": response.content if hasattr(response, 'content') else str(response),
                        "sources": sources,
                        "metadata": {
                            "total_sources": len(product_docs),
                            "query": question,
                            "search_method": "tag_based",
                            "tag_used": "product"
                        }
                    }
            
            # Pour les autres questions, utiliser la recherche par similarité normale
            logger.info("🔍 Requête générale - recherche par similarité")
            result = self.qa_chain({"query": question})
            
            # Formater les sources
            sources = []
            for doc in result.get("source_documents", []):
                sources.append({
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata,
                    "source": doc.metadata.get("source", "Unknown")
                })
            
            return {
                "answer": result["result"],
                "sources": sources[:max_results],
                "metadata": {
                    "total_sources": len(result.get("source_documents", [])),
                    "query": question,
                    "search_method": "similarity"
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
    """Effectue une requête sur la base de connaissances"""
    try:
        result = rag_system.query(
            question=request.query,
            max_results=request.max_results
        )
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            metadata=result["metadata"]
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)