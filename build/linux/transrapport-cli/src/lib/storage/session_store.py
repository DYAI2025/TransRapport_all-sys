"""
Analysis Session Storage Service
Manages analysis sessions and their metadata in encrypted database  
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, offline only
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import uuid4

from .database import DatabaseManager

logger = logging.getLogger(__name__)


class SessionStore:
    """
    Analysis Session Storage Service for TransRapport
    Manages LD-3.4 analysis sessions with constitutional compliance
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.constitutional_source = db_manager.constitutional_source
        
        logger.info("Analysis session store initialized")
    
    def create_session(self, conversation_id: str, session_name: str,
                      analysis_config: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Create new analysis session
        
        Args:
            conversation_id: Conversation ID
            session_name: Name for the analysis session
            analysis_config: Analysis configuration parameters
            
        Returns:
            Session ID if successful, None otherwise
        """
        try:
            session_id = str(uuid4())
            now = datetime.now().isoformat()
            
            # Serialize analysis config
            config_json = json.dumps(analysis_config) if analysis_config else None
            
            query = """
                INSERT INTO analysis_sessions 
                (id, conversation_id, session_name, analysis_config, 
                 constitutional_source, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor = self.db.execute_query(query, (
                session_id, conversation_id, session_name, config_json,
                self.constitutional_source, now, 'pending'
            ))
            
            if cursor and self.db.commit():
                logger.info(f"Analysis session created: {session_id} - {session_name}")
                return session_id
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to create analysis session: {e}")
            self.db.rollback()
            return None
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get analysis session by ID
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None if not found
        """
        try:
            query = """
                SELECT id, conversation_id, session_name, analysis_config,
                       processing_time, marker_count, rapport_indicator_count,
                       constitutional_source, created_at, completed_at, status
                FROM analysis_sessions
                WHERE id = ?
            """
            
            cursor = self.db.execute_query(query, (session_id,))
            if not cursor:
                return None
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Parse analysis config JSON
            analysis_config = None
            if row['analysis_config']:
                try:
                    analysis_config = json.loads(row['analysis_config'])
                except json.JSONDecodeError:
                    logger.warning(f"Invalid analysis config JSON for session {session_id}")
                    analysis_config = {}
            
            return {
                'id': row['id'],
                'conversation_id': row['conversation_id'],
                'session_name': row['session_name'],
                'analysis_config': analysis_config,
                'processing_time': row['processing_time'],
                'marker_count': row['marker_count'],
                'rapport_indicator_count': row['rapport_indicator_count'],
                'constitutional_source': row['constitutional_source'],
                'created_at': row['created_at'],
                'completed_at': row['completed_at'],
                'status': row['status']
            }
            
        except Exception as e:
            logger.error(f"Failed to get analysis session {session_id}: {e}")
            return None
    
    def list_sessions(self, conversation_id: Optional[str] = None,
                     status: Optional[str] = None,
                     limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List analysis sessions with optional filtering
        
        Args:
            conversation_id: Filter by conversation ID
            status: Filter by status
            limit: Maximum number of results
            
        Returns:
            List of session records
        """
        try:
            query = """
                SELECT id, conversation_id, session_name, analysis_config,
                       processing_time, marker_count, rapport_indicator_count,
                       constitutional_source, created_at, completed_at, status
                FROM analysis_sessions
            """
            
            conditions = []
            params = []
            
            if conversation_id:
                conditions.append("conversation_id = ?")
                params.append(conversation_id)
            
            if status:
                conditions.append("status = ?")
                params.append(status)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor = self.db.execute_query(query, tuple(params) if params else None)
            if not cursor:
                return []
            
            sessions = []
            for row in cursor.fetchall():
                # Parse analysis config
                analysis_config = None
                if row['analysis_config']:
                    try:
                        analysis_config = json.loads(row['analysis_config'])
                    except json.JSONDecodeError:
                        analysis_config = {}
                
                sessions.append({
                    'id': row['id'],
                    'conversation_id': row['conversation_id'],
                    'session_name': row['session_name'],
                    'analysis_config': analysis_config,
                    'processing_time': row['processing_time'],
                    'marker_count': row['marker_count'],
                    'rapport_indicator_count': row['rapport_indicator_count'],
                    'constitutional_source': row['constitutional_source'],
                    'created_at': row['created_at'],
                    'completed_at': row['completed_at'],
                    'status': row['status']
                })
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to list analysis sessions: {e}")
            return []
    
    def update_session_progress(self, session_id: str,
                              processing_time: Optional[float] = None,
                              marker_count: Optional[int] = None,
                              rapport_indicator_count: Optional[int] = None,
                              status: Optional[str] = None) -> bool:
        """
        Update session progress and metrics
        
        Args:
            session_id: Session ID
            processing_time: Processing time in seconds
            marker_count: Number of markers detected
            rapport_indicator_count: Number of rapport indicators generated
            status: Session status
            
        Returns:
            True if update successful
        """
        try:
            update_fields = []
            params = []
            
            if processing_time is not None:
                update_fields.append("processing_time = ?")
                params.append(processing_time)
            
            if marker_count is not None:
                update_fields.append("marker_count = ?")
                params.append(marker_count)
            
            if rapport_indicator_count is not None:
                update_fields.append("rapport_indicator_count = ?")
                params.append(rapport_indicator_count)
            
            if status is not None:
                update_fields.append("status = ?")
                params.append(status)
                
                # Set completion time if status is completed
                if status == 'completed':
                    update_fields.append("completed_at = ?")
                    params.append(datetime.now().isoformat())
            
            if not update_fields:
                return True  # Nothing to update
            
            params.append(session_id)  # For WHERE clause
            
            query = f"""
                UPDATE analysis_sessions 
                SET {', '.join(update_fields)}
                WHERE id = ?
            """
            
            cursor = self.db.execute_query(query, tuple(params))
            if cursor and self.db.commit():
                logger.info(f"Analysis session updated: {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update analysis session {session_id}: {e}")
            self.db.rollback()
            return False
    
    def complete_session(self, session_id: str, 
                        processing_time: float,
                        marker_count: int,
                        rapport_indicator_count: int) -> bool:
        """
        Mark session as completed with final metrics
        
        Args:
            session_id: Session ID
            processing_time: Total processing time
            marker_count: Final marker count
            rapport_indicator_count: Final rapport indicator count
            
        Returns:
            True if completion successful
        """
        return self.update_session_progress(
            session_id=session_id,
            processing_time=processing_time,
            marker_count=marker_count,
            rapport_indicator_count=rapport_indicator_count,
            status='completed'
        )
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete analysis session
        
        Args:
            session_id: Session ID
            
        Returns:
            True if deletion successful
        """
        try:
            query = "DELETE FROM analysis_sessions WHERE id = ?"
            cursor = self.db.execute_query(query, (session_id,))
            
            if cursor and self.db.commit():
                logger.info(f"Analysis session deleted: {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete analysis session {session_id}: {e}")
            self.db.rollback()
            return False
    
    def get_session_summary(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get summary of all sessions for a conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dictionary with session summary statistics
        """
        try:
            summary = {
                'conversation_id': conversation_id,
                'constitutional_source': self.constitutional_source
            }
            
            # Overall session statistics
            cursor = self.db.execute_query("""
                SELECT COUNT(*) as total_sessions,
                       COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
                       COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_sessions,
                       COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_sessions,
                       AVG(CASE WHEN processing_time IS NOT NULL THEN processing_time END) as avg_processing_time,
                       SUM(CASE WHEN marker_count IS NOT NULL THEN marker_count ELSE 0 END) as total_markers,
                       SUM(CASE WHEN rapport_indicator_count IS NOT NULL THEN rapport_indicator_count ELSE 0 END) as total_indicators
                FROM analysis_sessions
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            if cursor:
                row = cursor.fetchone()
                summary.update({
                    'total_sessions': row['total_sessions'],
                    'completed_sessions': row['completed_sessions'],
                    'pending_sessions': row['pending_sessions'],
                    'failed_sessions': row['failed_sessions'],
                    'avg_processing_time': row['avg_processing_time'] or 0.0,
                    'total_markers': row['total_markers'],
                    'total_indicators': row['total_indicators']
                })
            
            # Recent sessions
            cursor = self.db.execute_query("""
                SELECT id, session_name, status, created_at, completed_at,
                       marker_count, rapport_indicator_count
                FROM analysis_sessions
                WHERE conversation_id = ?
                ORDER BY created_at DESC
                LIMIT 5
            """, (conversation_id,))
            
            if cursor:
                recent_sessions = []
                for row in cursor.fetchall():
                    recent_sessions.append({
                        'id': row['id'],
                        'session_name': row['session_name'],
                        'status': row['status'],
                        'created_at': row['created_at'],
                        'completed_at': row['completed_at'],
                        'marker_count': row['marker_count'],
                        'rapport_indicator_count': row['rapport_indicator_count']
                    })
                summary['recent_sessions'] = recent_sessions
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get session summary: {e}")
            return {'conversation_id': conversation_id, 'error': str(e)}
    
    def get_constitutional_compliance_report(self) -> Dict[str, Any]:
        """
        Generate constitutional compliance report for all sessions
        
        Returns:
            Dictionary with constitutional compliance metrics
        """
        try:
            report = {
                'constitutional_source': self.constitutional_source,
                'report_timestamp': datetime.now().isoformat()
            }
            
            # Overall compliance metrics
            cursor = self.db.execute_query("""
                SELECT COUNT(*) as total_sessions,
                       COUNT(CASE WHEN constitutional_source = ? THEN 1 END) as compliant_sessions,
                       COUNT(DISTINCT conversation_id) as conversations_analyzed,
                       SUM(CASE WHEN marker_count IS NOT NULL THEN marker_count ELSE 0 END) as total_constitutional_markers
                FROM analysis_sessions
            """, (self.constitutional_source,))
            
            if cursor:
                row = cursor.fetchone()
                compliance_rate = (row['compliant_sessions'] / row['total_sessions'] * 100) if row['total_sessions'] > 0 else 0
                
                report.update({
                    'total_sessions': row['total_sessions'],
                    'compliant_sessions': row['compliant_sessions'],
                    'compliance_rate_percent': compliance_rate,
                    'conversations_analyzed': row['conversations_analyzed'],
                    'total_constitutional_markers': row['total_constitutional_markers']
                })
            
            # Session status distribution
            cursor = self.db.execute_query("""
                SELECT status, COUNT(*) as count
                FROM analysis_sessions
                GROUP BY status
                ORDER BY count DESC
            """)
            
            if cursor:
                status_distribution = {}
                for row in cursor.fetchall():
                    status_distribution[row['status']] = row['count']
                report['status_distribution'] = status_distribution
            
            # Processing performance metrics
            cursor = self.db.execute_query("""
                SELECT AVG(processing_time) as avg_processing_time,
                       MIN(processing_time) as min_processing_time,
                       MAX(processing_time) as max_processing_time,
                       COUNT(CASE WHEN processing_time IS NOT NULL THEN 1 END) as sessions_with_timing
                FROM analysis_sessions
                WHERE status = 'completed'
            """)
            
            if cursor:
                row = cursor.fetchone()
                report['performance_metrics'] = {
                    'avg_processing_time': row['avg_processing_time'] or 0.0,
                    'min_processing_time': row['min_processing_time'] or 0.0,
                    'max_processing_time': row['max_processing_time'] or 0.0,
                    'sessions_with_timing': row['sessions_with_timing']
                }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate constitutional compliance report: {e}")
            return {'error': str(e), 'constitutional_source': self.constitutional_source}
    
    def archive_old_sessions(self, days_old: int = 30) -> int:
        """
        Archive old completed sessions
        
        Args:
            days_old: Archive sessions older than this many days
            
        Returns:
            Number of sessions archived
        """
        try:
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)
            cutoff_iso = cutoff_date.isoformat()
            
            # Update status to archived for old completed sessions
            query = """
                UPDATE analysis_sessions 
                SET status = 'archived'
                WHERE status = 'completed' 
                AND completed_at < ?
                AND status != 'archived'
            """
            
            cursor = self.db.execute_query(query, (cutoff_iso,))
            if cursor and self.db.commit():
                archived_count = cursor.rowcount
                logger.info(f"Archived {archived_count} old analysis sessions")
                return archived_count
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to archive old sessions: {e}")
            self.db.rollback()
            return 0