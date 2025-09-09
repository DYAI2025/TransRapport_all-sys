"""
Constitutional Marker Storage Service
Manages constitutional markers and rapport indicators in encrypted database
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, offline only
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import uuid4

from src.models.marker_event import MarkerEvent, MarkerType
from src.models.rapport_indicator import RapportIndicator, RapportTrend
from .database import DatabaseManager

logger = logging.getLogger(__name__)


class MarkerStore:
    """
    Constitutional Marker Storage Service for TransRapport
    Manages LD-3.4 constitutional markers and rapport indicators
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.constitutional_source = db_manager.constitutional_source
        
        logger.info("Constitutional marker store initialized")
    
    def store_markers(self, conversation_id: str, markers: List[MarkerEvent]) -> bool:
        """
        Store constitutional markers for a conversation
        
        Args:
            conversation_id: Conversation ID
            markers: List of constitutional marker events
            
        Returns:
            True if storage successful
        """
        try:
            if not markers:
                return True
            
            query = """
                INSERT INTO constitutional_markers 
                (id, conversation_id, marker_type, marker_subtype, start_time, end_time,
                 confidence, evidence, explanation, speaker, constitutional_source, 
                 analysis_method, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            now = datetime.now().isoformat()
            marker_data = []
            
            for marker in markers:
                # Use existing marker ID or generate new one
                marker_id = marker.id or str(uuid4())
                
                marker_data.append((
                    marker_id,
                    conversation_id,
                    marker.marker_type.value if hasattr(marker.marker_type, 'value') else str(marker.marker_type),
                    marker.marker_subtype,
                    marker.start_time,
                    marker.end_time,
                    marker.confidence,
                    marker.evidence,
                    marker.explanation,
                    marker.speaker,
                    marker.constitutional_source or self.constitutional_source,
                    marker.analysis_method,
                    now
                ))
            
            success = self.db.execute_many(query, marker_data)
            if success and self.db.commit():
                logger.info(f"Stored {len(markers)} constitutional markers for conversation {conversation_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to store constitutional markers: {e}")
            self.db.rollback()
            return False
    
    def get_markers(self, conversation_id: str,
                   marker_type: Optional[str] = None,
                   start_time: Optional[float] = None,
                   end_time: Optional[float] = None,
                   min_confidence: Optional[float] = None) -> List[MarkerEvent]:
        """
        Get constitutional markers for conversation with filtering
        
        Args:
            conversation_id: Conversation ID
            marker_type: Filter by marker type (ATO, SEM, CLU, MEMA)
            start_time: Filter by start time
            end_time: Filter by end time  
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of constitutional marker events
        """
        try:
            query = """
                SELECT id, marker_type, marker_subtype, start_time, end_time,
                       confidence, evidence, explanation, speaker, 
                       constitutional_source, analysis_method, created_at
                FROM constitutional_markers
                WHERE conversation_id = ?
            """
            
            params = [conversation_id]
            
            if marker_type:
                query += " AND marker_type = ?"
                params.append(marker_type)
            
            if start_time is not None:
                query += " AND start_time >= ?"
                params.append(start_time)
            
            if end_time is not None:
                query += " AND end_time <= ?"
                params.append(end_time)
            
            if min_confidence is not None:
                query += " AND confidence >= ?"
                params.append(min_confidence)
            
            query += " ORDER BY start_time"
            
            cursor = self.db.execute_query(query, tuple(params))
            if not cursor:
                return []
            
            markers = []
            for row in cursor.fetchall():
                # Convert marker type string back to enum
                try:
                    marker_type_enum = MarkerType(row['marker_type'])
                except ValueError:
                    # Fallback for unknown marker types
                    marker_type_enum = row['marker_type']
                
                marker = MarkerEvent(
                    id=row['id'],
                    marker_type=marker_type_enum,
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    confidence=row['confidence'],
                    evidence=row['evidence'],
                    explanation=row['explanation'],
                    marker_subtype=row['marker_subtype'],
                    speaker=row['speaker'],
                    constitutional_source=row['constitutional_source'],
                    analysis_method=row['analysis_method']
                )
                markers.append(marker)
            
            return markers
            
        except Exception as e:
            logger.error(f"Failed to get constitutional markers: {e}")
            return []
    
    def store_rapport_indicators(self, conversation_id: str, 
                               indicators: List[RapportIndicator]) -> bool:
        """
        Store rapport indicators for a conversation
        
        Args:
            conversation_id: Conversation ID
            indicators: List of rapport indicators
            
        Returns:
            True if storage successful
        """
        try:
            if not indicators:
                return True
            
            query = """
                INSERT INTO rapport_indicators 
                (id, conversation_id, timestamp, value, trend, confidence,
                 contributing_markers_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            now = datetime.now().isoformat()
            indicator_data = []
            
            for indicator in indicators:
                indicator_id = str(uuid4())
                trend_value = indicator.trend.value if hasattr(indicator.trend, 'value') else str(indicator.trend)
                
                indicator_data.append((
                    indicator_id,
                    conversation_id,
                    indicator.timestamp,
                    indicator.value,
                    trend_value,
                    indicator.confidence,
                    len(indicator.contributing_markers) if hasattr(indicator, 'contributing_markers') else 0,
                    now
                ))
            
            success = self.db.execute_many(query, indicator_data)
            if success and self.db.commit():
                logger.info(f"Stored {len(indicators)} rapport indicators for conversation {conversation_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to store rapport indicators: {e}")
            self.db.rollback()
            return False
    
    def get_rapport_indicators(self, conversation_id: str,
                             start_time: Optional[float] = None,
                             end_time: Optional[float] = None) -> List[RapportIndicator]:
        """
        Get rapport indicators for conversation
        
        Args:
            conversation_id: Conversation ID
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            List of rapport indicators
        """
        try:
            query = """
                SELECT id, timestamp, value, trend, confidence, 
                       contributing_markers_count, created_at
                FROM rapport_indicators
                WHERE conversation_id = ?
            """
            
            params = [conversation_id]
            
            if start_time is not None:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time is not None:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp"
            
            cursor = self.db.execute_query(query, tuple(params))
            if not cursor:
                return []
            
            indicators = []
            for row in cursor.fetchall():
                # Convert trend string back to enum
                try:
                    trend_enum = RapportTrend(row['trend'])
                except ValueError:
                    trend_enum = RapportTrend.STABLE  # Default fallback
                
                # Create indicator without contributing_markers (would require separate query)
                indicator = RapportIndicator(
                    timestamp=row['timestamp'],
                    value=row['value'],
                    trend=trend_enum,
                    confidence=row['confidence'],
                    contributing_markers=[]  # Empty list - can be populated if needed
                )
                indicators.append(indicator)
            
            return indicators
            
        except Exception as e:
            logger.error(f"Failed to get rapport indicators: {e}")
            return []
    
    def get_marker_statistics(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get constitutional marker statistics for conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dictionary with marker statistics
        """
        try:
            stats = {
                'conversation_id': conversation_id,
                'constitutional_source': self.constitutional_source
            }
            
            # Overall marker statistics
            cursor = self.db.execute_query("""
                SELECT COUNT(*) as total_markers,
                       AVG(confidence) as avg_confidence,
                       MIN(confidence) as min_confidence,
                       MAX(confidence) as max_confidence,
                       COUNT(DISTINCT marker_type) as unique_types,
                       COUNT(DISTINCT marker_subtype) as unique_subtypes
                FROM constitutional_markers 
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            if cursor:
                row = cursor.fetchone()
                stats.update({
                    'total_markers': row['total_markers'],
                    'avg_confidence': row['avg_confidence'] or 0.0,
                    'min_confidence': row['min_confidence'] or 0.0,
                    'max_confidence': row['max_confidence'] or 0.0,
                    'unique_types': row['unique_types'],
                    'unique_subtypes': row['unique_subtypes']
                })
            
            # Marker type distribution
            cursor = self.db.execute_query("""
                SELECT marker_type, COUNT(*) as count,
                       AVG(confidence) as avg_confidence
                FROM constitutional_markers 
                WHERE conversation_id = ?
                GROUP BY marker_type
                ORDER BY count DESC
            """, (conversation_id,))
            
            if cursor:
                type_distribution = {}
                for row in cursor.fetchall():
                    type_distribution[row['marker_type']] = {
                        'count': row['count'],
                        'avg_confidence': row['avg_confidence']
                    }
                stats['type_distribution'] = type_distribution
            
            # Marker subtype distribution
            cursor = self.db.execute_query("""
                SELECT marker_subtype, COUNT(*) as count,
                       AVG(confidence) as avg_confidence
                FROM constitutional_markers 
                WHERE conversation_id = ? AND marker_subtype IS NOT NULL
                GROUP BY marker_subtype
                ORDER BY count DESC
                LIMIT 10
            """, (conversation_id,))
            
            if cursor:
                subtype_distribution = {}
                for row in cursor.fetchall():
                    subtype_distribution[row['marker_subtype']] = {
                        'count': row['count'],
                        'avg_confidence': row['avg_confidence']
                    }
                stats['top_subtypes'] = subtype_distribution
            
            # Temporal analysis
            cursor = self.db.execute_query("""
                SELECT MIN(start_time) as first_marker_time,
                       MAX(end_time) as last_marker_time,
                       MAX(end_time) - MIN(start_time) as marker_timespan
                FROM constitutional_markers 
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            if cursor:
                row = cursor.fetchone()
                if row['first_marker_time'] is not None:
                    stats.update({
                        'first_marker_time': row['first_marker_time'],
                        'last_marker_time': row['last_marker_time'],
                        'marker_timespan': row['marker_timespan']
                    })
            
            # Rapport indicator statistics
            cursor = self.db.execute_query("""
                SELECT COUNT(*) as indicator_count,
                       AVG(value) as avg_rapport,
                       MIN(value) as min_rapport,
                       MAX(value) as max_rapport,
                       AVG(confidence) as avg_indicator_confidence
                FROM rapport_indicators 
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            if cursor:
                row = cursor.fetchone()
                stats.update({
                    'indicator_count': row['indicator_count'],
                    'avg_rapport': row['avg_rapport'] or 0.0,
                    'min_rapport': row['min_rapport'] or 0.0,
                    'max_rapport': row['max_rapport'] or 0.0,
                    'avg_indicator_confidence': row['avg_indicator_confidence'] or 0.0
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get marker statistics: {e}")
            return {'conversation_id': conversation_id, 'error': str(e)}
    
    def delete_markers(self, conversation_id: str, marker_type: Optional[str] = None) -> bool:
        """
        Delete markers for conversation
        
        Args:
            conversation_id: Conversation ID
            marker_type: Optional marker type filter
            
        Returns:
            True if deletion successful
        """
        try:
            if marker_type:
                query = "DELETE FROM constitutional_markers WHERE conversation_id = ? AND marker_type = ?"
                params = (conversation_id, marker_type)
            else:
                query = "DELETE FROM constitutional_markers WHERE conversation_id = ?"
                params = (conversation_id,)
            
            cursor = self.db.execute_query(query, params)
            if cursor and self.db.commit():
                logger.info(f"Deleted markers for conversation {conversation_id}" +
                           (f" (type: {marker_type})" if marker_type else ""))
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete markers: {e}")
            self.db.rollback()
            return False
    
    def update_marker_confidence(self, marker_id: str, new_confidence: float) -> bool:
        """
        Update confidence score for a specific marker
        
        Args:
            marker_id: Marker ID
            new_confidence: New confidence value (0.0 to 1.0)
            
        Returns:
            True if update successful
        """
        try:
            query = "UPDATE constitutional_markers SET confidence = ? WHERE id = ?"
            cursor = self.db.execute_query(query, (new_confidence, marker_id))
            
            if cursor and self.db.commit():
                logger.info(f"Updated marker confidence: {marker_id} -> {new_confidence}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update marker confidence: {e}")
            self.db.rollback()
            return False