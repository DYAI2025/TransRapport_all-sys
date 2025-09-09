"""
Conversation Storage Service
Manages conversation data in encrypted database
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, offline only
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import uuid4

from .database import DatabaseManager

logger = logging.getLogger(__name__)


class ConversationStore:
    """
    Conversation Storage Service for TransRapport
    Manages conversation metadata and transcript segments in encrypted storage
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.constitutional_source = db_manager.constitutional_source
        
        logger.info("Conversation store initialized")
    
    def create_conversation(self, name: str, description: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Create a new conversation record
        
        Args:
            name: Conversation name
            description: Optional description
            metadata: Additional metadata
            
        Returns:
            Conversation ID if successful, None otherwise
        """
        try:
            conversation_id = str(uuid4())
            now = datetime.now().isoformat()
            
            # Prepare metadata
            meta_json = json.dumps(metadata) if metadata else None
            
            query = """
                INSERT INTO conversations (id, name, description, created_at, updated_at, 
                                        constitutional_source, metadata, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor = self.db.execute_query(query, (
                conversation_id, name, description, now, now,
                self.constitutional_source, meta_json, 'active'
            ))
            
            if cursor and self.db.commit():
                logger.info(f"Conversation created: {conversation_id} - {name}")
                return conversation_id
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            self.db.rollback()
            return None
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation by ID
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation data or None if not found
        """
        try:
            query = """
                SELECT id, name, description, created_at, updated_at,
                       constitutional_source, metadata, status
                FROM conversations
                WHERE id = ?
            """
            
            cursor = self.db.execute_query(query, (conversation_id,))
            if not cursor:
                return None
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Parse metadata JSON
            metadata = None
            if row['metadata']:
                try:
                    metadata = json.loads(row['metadata'])
                except json.JSONDecodeError:
                    logger.warning(f"Invalid metadata JSON for conversation {conversation_id}")
                    metadata = {}
            
            return {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'constitutional_source': row['constitutional_source'],
                'metadata': metadata,
                'status': row['status']
            }
            
        except Exception as e:
            logger.error(f"Failed to get conversation {conversation_id}: {e}")
            return None
    
    def list_conversations(self, status: Optional[str] = None, 
                         limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List conversations with optional filtering
        
        Args:
            status: Filter by status (active, archived, etc.)
            limit: Maximum number of results
            
        Returns:
            List of conversation records
        """
        try:
            query = """
                SELECT id, name, description, created_at, updated_at,
                       constitutional_source, metadata, status
                FROM conversations
            """
            
            params = []
            if status:
                query += " WHERE status = ?"
                params.append(status)
            
            query += " ORDER BY updated_at DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor = self.db.execute_query(query, tuple(params) if params else None)
            if not cursor:
                return []
            
            conversations = []
            for row in cursor.fetchall():
                # Parse metadata
                metadata = None
                if row['metadata']:
                    try:
                        metadata = json.loads(row['metadata'])
                    except json.JSONDecodeError:
                        metadata = {}
                
                conversations.append({
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'constitutional_source': row['constitutional_source'],
                    'metadata': metadata,
                    'status': row['status']
                })
            
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")
            return []
    
    def update_conversation(self, conversation_id: str, 
                          name: Optional[str] = None,
                          description: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None,
                          status: Optional[str] = None) -> bool:
        """
        Update conversation record
        
        Args:
            conversation_id: Conversation ID
            name: New name (optional)
            description: New description (optional)
            metadata: New metadata (optional)
            status: New status (optional)
            
        Returns:
            True if update successful
        """
        try:
            # Build dynamic update query
            update_fields = []
            params = []
            
            if name is not None:
                update_fields.append("name = ?")
                params.append(name)
            
            if description is not None:
                update_fields.append("description = ?")
                params.append(description)
            
            if metadata is not None:
                update_fields.append("metadata = ?")
                params.append(json.dumps(metadata))
            
            if status is not None:
                update_fields.append("status = ?")
                params.append(status)
            
            if not update_fields:
                return True  # Nothing to update
            
            # Always update timestamp
            update_fields.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            
            # Add conversation ID for WHERE clause
            params.append(conversation_id)
            
            query = f"""
                UPDATE conversations 
                SET {', '.join(update_fields)}
                WHERE id = ?
            """
            
            cursor = self.db.execute_query(query, tuple(params))
            if cursor and self.db.commit():
                logger.info(f"Conversation updated: {conversation_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update conversation {conversation_id}: {e}")
            self.db.rollback()
            return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete conversation and all associated data
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if deletion successful
        """
        try:
            query = "DELETE FROM conversations WHERE id = ?"
            cursor = self.db.execute_query(query, (conversation_id,))
            
            if cursor and self.db.commit():
                logger.info(f"Conversation deleted: {conversation_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            self.db.rollback()
            return False
    
    def add_transcript_segments(self, conversation_id: str, 
                              segments: List[Dict[str, Any]]) -> bool:
        """
        Add transcript segments to conversation
        
        Args:
            conversation_id: Conversation ID
            segments: List of transcript segments
            
        Returns:
            True if segments added successfully
        """
        try:
            query = """
                INSERT INTO transcript_segments 
                (id, conversation_id, segment_index, start_time, end_time, 
                 text, speaker, confidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            now = datetime.now().isoformat()
            segment_data = []
            
            for i, segment in enumerate(segments):
                segment_id = str(uuid4())
                segment_data.append((
                    segment_id,
                    conversation_id,
                    i,
                    segment.get('start_time', 0.0),
                    segment.get('end_time', 0.0),
                    segment.get('text', ''),
                    segment.get('speaker'),
                    segment.get('confidence'),
                    now
                ))
            
            success = self.db.execute_many(query, segment_data)
            if success and self.db.commit():
                logger.info(f"Added {len(segments)} transcript segments to conversation {conversation_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to add transcript segments: {e}")
            self.db.rollback()
            return False
    
    def get_transcript_segments(self, conversation_id: str,
                              start_time: Optional[float] = None,
                              end_time: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Get transcript segments for conversation
        
        Args:
            conversation_id: Conversation ID
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            List of transcript segments
        """
        try:
            query = """
                SELECT id, segment_index, start_time, end_time, text, 
                       speaker, confidence, created_at
                FROM transcript_segments
                WHERE conversation_id = ?
            """
            
            params = [conversation_id]
            
            if start_time is not None:
                query += " AND start_time >= ?"
                params.append(start_time)
            
            if end_time is not None:
                query += " AND end_time <= ?"
                params.append(end_time)
            
            query += " ORDER BY segment_index"
            
            cursor = self.db.execute_query(query, tuple(params))
            if not cursor:
                return []
            
            segments = []
            for row in cursor.fetchall():
                segments.append({
                    'id': row['id'],
                    'segment_index': row['segment_index'],
                    'start_time': row['start_time'],
                    'end_time': row['end_time'],
                    'text': row['text'],
                    'speaker': row['speaker'],
                    'confidence': row['confidence'],
                    'created_at': row['created_at']
                })
            
            return segments
            
        except Exception as e:
            logger.error(f"Failed to get transcript segments: {e}")
            return []
    
    def get_conversation_statistics(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get statistics for conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dictionary with conversation statistics
        """
        try:
            stats = {'conversation_id': conversation_id}
            
            # Segment count and duration
            cursor = self.db.execute_query("""
                SELECT COUNT(*) as segment_count, 
                       MAX(end_time) as total_duration,
                       COUNT(DISTINCT speaker) as speaker_count
                FROM transcript_segments 
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            if cursor:
                row = cursor.fetchone()
                stats.update({
                    'segment_count': row['segment_count'],
                    'total_duration': row['total_duration'] or 0.0,
                    'speaker_count': row['speaker_count']
                })
            
            # Constitutional marker count
            cursor = self.db.execute_query("""
                SELECT COUNT(*) as marker_count,
                       COUNT(DISTINCT marker_type) as marker_types
                FROM constitutional_markers 
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            if cursor:
                row = cursor.fetchone()
                stats.update({
                    'marker_count': row['marker_count'],
                    'marker_types': row['marker_types']
                })
            
            # Rapport indicator count
            cursor = self.db.execute_query("""
                SELECT COUNT(*) as indicator_count,
                       AVG(value) as avg_rapport
                FROM rapport_indicators 
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            if cursor:
                row = cursor.fetchone()
                stats.update({
                    'indicator_count': row['indicator_count'],
                    'avg_rapport': row['avg_rapport'] or 0.0
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get conversation statistics: {e}")
            return {'conversation_id': conversation_id, 'error': str(e)}