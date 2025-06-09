import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class SessionManager:
    """Gestionnaire de sessions et d'historique des conversations"""
    
    def __init__(self, db_path: str = "sessions.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialise la base de données SQLite avec les tables nécessaires"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Table des sessions
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        title TEXT,
                        metadata TEXT
                    )
                """)
                
                # Table de l'historique des messages
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        metadata TEXT,
                        FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                    )
                """)
                
                # Index pour améliorer les performances
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_messages_session_id 
                    ON messages (session_id)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
                    ON messages (timestamp)
                """)
                
                conn.commit()
                logger.info(f"✅ Base de données des sessions initialisée: {self.db_path}")
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
            raise
    
    def create_session(self, title: str = None, metadata: Dict[str, Any] = None) -> str:
        """Crée une nouvelle session et retourne son ID"""
        try:
            session_id = str(uuid.uuid4())
            
            # Générer un titre automatique si non fourni
            if not title:
                title = f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            metadata_json = json.dumps(metadata or {})
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sessions (id, title, metadata)
                    VALUES (?, ?, ?)
                """, (session_id, title, metadata_json))
                conn.commit()
            
            logger.info(f"📝 Nouvelle session créée: {session_id} - {title}")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création de session: {e}")
            raise
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> int:
        """Ajoute un message à l'historique d'une session"""
        try:
            # Vérifier que la session existe
            if not self.session_exists(session_id):
                raise ValueError(f"Session {session_id} n'existe pas")
            
            metadata_json = json.dumps(metadata or {})
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO messages (session_id, role, content, metadata)
                    VALUES (?, ?, ?, ?)
                """, (session_id, role, content, metadata_json))
                
                # Mettre à jour le timestamp de la session
                cursor.execute("""
                    UPDATE sessions 
                    SET updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (session_id,))
                
                message_id = cursor.lastrowid
                conn.commit()
            
            logger.debug(f"💬 Message ajouté à la session {session_id}: {role}")
            return message_id
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'ajout du message: {e}")
            raise
    
    def get_session_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère l'historique des messages d'une session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, timestamp, role, content, metadata
                    FROM messages
                    WHERE session_id = ?
                    ORDER BY timestamp ASC
                    LIMIT ?
                """, (session_id, limit))
                
                messages = []
                for row in cursor.fetchall():
                    message_id, timestamp, role, content, metadata_json = row
                    metadata = json.loads(metadata_json) if metadata_json else {}
                    
                    messages.append({
                        "id": message_id,
                        "timestamp": timestamp,
                        "role": role,
                        "content": content,
                        "metadata": metadata
                    })
                
                return messages
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération de l'historique: {e}")
            raise
    
    def get_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Récupère la liste des sessions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT s.id, s.created_at, s.updated_at, s.title, s.metadata,
                           COUNT(m.id) as message_count
                    FROM sessions s
                    LEFT JOIN messages m ON s.id = m.session_id
                    GROUP BY s.id, s.created_at, s.updated_at, s.title, s.metadata
                    ORDER BY s.updated_at DESC
                    LIMIT ?
                """, (limit,))
                
                sessions = []
                for row in cursor.fetchall():
                    session_id, created_at, updated_at, title, metadata_json, message_count = row
                    metadata = json.loads(metadata_json) if metadata_json else {}
                    
                    sessions.append({
                        "id": session_id,
                        "created_at": created_at,
                        "updated_at": updated_at,
                        "title": title,
                        "metadata": metadata,
                        "message_count": message_count
                    })
                
                return sessions
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des sessions: {e}")
            raise
    
    def session_exists(self, session_id: str) -> bool:
        """Vérifie si une session existe"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM sessions WHERE id = ?
                """, (session_id,))
                
                count = cursor.fetchone()[0]
                return count > 0
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la vérification de session: {e}")
            return False
    
    def get_session_info(self, session_id: str) -> dict:
        """Récupère les informations d'une session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, title, created_at FROM sessions WHERE id = ?",
                    (session_id,)
                )
                result = cursor.fetchone()
                if result:
                    return {
                        "session_id": result[0],
                        "title": result[1],
                        "created_at": result[2]
                    }
                return None
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des informations de session: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Supprime une session et tous ses messages"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Supprimer les messages (CASCADE devrait le faire automatiquement)
                cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
                
                # Supprimer la session
                cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"🗑️ Session supprimée: {session_id}")
                    return True
                else:
                    logger.warning(f"⚠️ Session non trouvée: {session_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erreur lors de la suppression de session: {e}")
            raise
    
    def update_session_title(self, session_id: str, title: str) -> bool:
        """Met à jour le titre d'une session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sessions 
                    SET title = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (title, session_id))
                
                updated_count = cursor.rowcount
                conn.commit()
                
                if updated_count > 0:
                    logger.info(f"✏️ Titre de session mis à jour: {session_id} -> {title}")
                    return True
                else:
                    logger.warning(f"⚠️ Session non trouvée pour mise à jour: {session_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erreur lors de la mise à jour du titre: {e}")
            raise
    
    def get_session_context(self, session_id: str, max_messages: int = 10) -> str:
        """Récupère le contexte récent d'une session pour l'IA"""
        try:
            messages = self.get_session_history(session_id, limit=max_messages)
            
            if not messages:
                return ""
            
            # Construire le contexte
            context_parts = []
            for msg in messages[-max_messages:]:  # Prendre les derniers messages
                role = msg['role']
                content = msg['content']
                
                if role == 'user':
                    context_parts.append(f"Utilisateur: {content}")
                elif role == 'assistant':
                    # Pour l'assistant, on peut raccourcir le JSON si c'est trop long
                    if len(content) > 500:
                        context_parts.append(f"Assistant: [Réponse JSON générée]")
                    else:
                        context_parts.append(f"Assistant: {content}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération du contexte: {e}")
            return ""
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Supprime les sessions anciennes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Supprimer les sessions non mises à jour depuis X jours
                cursor.execute("""
                    DELETE FROM sessions 
                    WHERE updated_at < datetime('now', '-{} days')
                """.format(days_old))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"🧹 {deleted_count} sessions anciennes supprimées")
                
                return deleted_count
                
        except Exception as e:
            logger.error(f"❌ Erreur lors du nettoyage: {e}")
            raise