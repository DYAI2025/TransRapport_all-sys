"""
Database Manager with SQLCipher Encryption
Manages encrypted database operations for TransRapport
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, offline only
"""

import logging
import os
import sqlite3
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import hashlib

try:
    import sqlcipher3
    SQLCIPHER_AVAILABLE = True
except ImportError:
    SQLCIPHER_AVAILABLE = False
    # No fallback - require SQLCipher for security
    raise RuntimeError("SQLCipher nicht installiert. Start abgebrochen: keine Verschlüsselung möglich. Installiere sqlcipher3-binary.")

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Configuration for encrypted database"""
    database_path: str = "data/transrapport.db"
    encryption_key: Optional[str] = None  # Will be derived from user input
    cipher_version: str = "4"
    kdf_iterations: int = 256000
    page_size: int = 4096
    enable_foreign_keys: bool = True
    constitutional_source: str = "LD-3.4-constitution"
    auto_vacuum: str = "INCREMENTAL"


class DatabaseManager:
    """
    Encrypted Database Manager for TransRapport
    Handles SQLCipher database operations with constitutional compliance
    """
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self.connection: Optional[Union[sqlite3.Connection, 'sqlcipher3.Connection']] = None
        self.database_path = Path(self.config.database_path)
        self.constitutional_source = self.config.constitutional_source
        self._encryption_key = None
        
        # Create data directory if needed
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        if SQLCIPHER_AVAILABLE:
            logger.info("SQLCipher available - using encrypted database")
        else:
            logger.warning("SQLCipher not available - using regular SQLite (development mode)")
    
    def initialize_database(self, passphrase: str) -> bool:
        """
        Initialize encrypted database with passphrase
        
        Args:
            passphrase: User passphrase for database encryption
            
        Returns:
            True if initialization successful
        """
        try:
            # Derive encryption key from passphrase
            self._encryption_key = self._derive_key(passphrase)
            
            # Connect to database
            if not self._connect():
                return False
            
            # Set SQLCipher pragmas
            if SQLCIPHER_AVAILABLE:
                self._configure_encryption()
            
            # Create schema
            if not self._create_schema():
                return False
            
            # Verify database integrity
            if not self._verify_database():
                return False
            
            logger.info(f"Database initialized: {self.database_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False
    
    def connect(self, passphrase: str) -> bool:
        """
        Connect to existing encrypted database
        
        Args:
            passphrase: User passphrase for database decryption
            
        Returns:
            True if connection successful
        """
        try:
            if not self.database_path.exists():
                logger.error(f"Database does not exist: {self.database_path}")
                return False
            
            # Derive encryption key
            self._encryption_key = self._derive_key(passphrase)
            
            # Connect
            if not self._connect():
                return False
            
            # Configure encryption
            if SQLCIPHER_AVAILABLE:
                self._configure_encryption()
            
            # Test access with a simple query
            if not self._test_database_access():
                logger.error("Database access test failed - invalid passphrase?")
                self.disconnect()
                return False
            
            logger.info("Database connection established")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                logger.info("Database disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting from database: {e}")
    
    def execute_query(self, query: str, parameters: Optional[tuple] = None) -> Optional[sqlite3.Cursor]:
        """
        Execute a database query
        
        Args:
            query: SQL query string
            parameters: Query parameters
            
        Returns:
            Cursor object or None if failed
        """
        if not self.connection:
            logger.error("No database connection")
            return None
        
        try:
            cursor = self.connection.cursor()
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            return cursor
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return None
    
    def execute_many(self, query: str, parameters_list: List[tuple]) -> bool:
        """
        Execute a query with multiple parameter sets
        
        Args:
            query: SQL query string
            parameters_list: List of parameter tuples
            
        Returns:
            True if successful
        """
        if not self.connection:
            logger.error("No database connection")
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, parameters_list)
            return True
            
        except Exception as e:
            logger.error(f"Batch query execution failed: {e}")
            return False
    
    def commit(self) -> bool:
        """Commit current transaction"""
        if not self.connection:
            return False
        
        try:
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Commit failed: {e}")
            return False
    
    def rollback(self) -> bool:
        """Rollback current transaction"""
        if not self.connection:
            return False
        
        try:
            self.connection.rollback()
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def backup_database(self, backup_path: str, passphrase: str) -> bool:
        """
        Create encrypted backup of database
        
        Args:
            backup_path: Path for backup file
            passphrase: Passphrase for backup encryption
            
        Returns:
            True if backup successful
        """
        if not self.connection:
            logger.error("No database connection for backup")
            return False
        
        try:
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup connection
            if SQLCIPHER_AVAILABLE:
                backup_conn = sqlcipher3.connect(str(backup_path))
                backup_key = self._derive_key(passphrase)
                backup_conn.execute(f"PRAGMA key = 'x\"{backup_key.hex()}\"'")
                self._configure_encryption_for_connection(backup_conn)
            else:
                backup_conn = sqlite3.connect(str(backup_path))
            
            # Perform backup
            self.connection.backup(backup_conn)
            backup_conn.close()
            
            logger.info(f"Database backup created: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False
    
    def vacuum_database(self) -> bool:
        """Vacuum database to reclaim space"""
        if not self.connection:
            return False
        
        try:
            self.connection.execute("VACUUM")
            self.connection.commit()
            logger.info("Database vacuum completed")
            return True
        except Exception as e:
            logger.error(f"Database vacuum failed: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics"""
        if not self.connection:
            return {}
        
        info = {
            'database_path': str(self.database_path),
            'encrypted': SQLCIPHER_AVAILABLE,
            'constitutional_source': self.constitutional_source
        }
        
        try:
            # Get database size
            info['size_bytes'] = self.database_path.stat().st_size
            
            # Get table information
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            info['tables'] = tables
            
            # Get record counts
            table_counts = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                table_counts[table] = cursor.fetchone()[0]
            info['table_counts'] = table_counts
            
            # Get schema version if exists
            cursor.execute("PRAGMA user_version")
            info['schema_version'] = cursor.fetchone()[0]
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return info
    
    def _derive_key(self, passphrase: str) -> bytes:
        """Derive encryption key from passphrase"""
        # Use PBKDF2 with SHA256
        salt = b'TransRapport-LD-3.4'  # Static salt for consistency
        return hashlib.pbkdf2_hmac('sha256', passphrase.encode('utf-8'), salt, self.config.kdf_iterations)
    
    def _connect(self) -> bool:
        """Establish database connection"""
        try:
            if SQLCIPHER_AVAILABLE:
                self.connection = sqlcipher3.connect(str(self.database_path))
            else:
                self.connection = sqlite3.connect(str(self.database_path))
            
            # Enable row factory for easier access
            self.connection.row_factory = sqlite3.Row
            
            return True
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def _configure_encryption(self):
        """Configure SQLCipher encryption parameters"""
        if not SQLCIPHER_AVAILABLE or not self.connection:
            return
        
        try:
            # Set encryption key
            self.connection.execute(f"PRAGMA key = 'x\"{self._encryption_key.hex()}\"'")
            
            self._configure_encryption_for_connection(self.connection)
            
        except Exception as e:
            logger.error(f"Failed to configure encryption: {e}")
            raise
    
    def _configure_encryption_for_connection(self, conn):
        """Configure encryption for a specific connection"""
        if not SQLCIPHER_AVAILABLE:
            return
        
        # Set cipher parameters
        conn.execute(f"PRAGMA cipher = 'aes-256-cbc'")
        conn.execute(f"PRAGMA kdf_iterations = {self.config.kdf_iterations}")
        conn.execute(f"PRAGMA cipher_page_size = {self.config.page_size}")
        conn.execute(f"PRAGMA cipher_version = {self.config.cipher_version}")
        
        # Enable foreign keys
        if self.config.enable_foreign_keys:
            conn.execute("PRAGMA foreign_keys = ON")
        
        # Set auto vacuum
        conn.execute(f"PRAGMA auto_vacuum = {self.config.auto_vacuum}")
    
    def _create_schema(self) -> bool:
        """Create database schema"""
        try:
            cursor = self.connection.cursor()
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    constitutional_source TEXT NOT NULL,
                    metadata TEXT,  -- JSON metadata
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # Transcript segments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transcript_segments (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    segment_index INTEGER NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL NOT NULL,
                    text TEXT NOT NULL,
                    speaker TEXT,
                    confidence REAL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """)
            
            # Constitutional markers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS constitutional_markers (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    marker_type TEXT NOT NULL,
                    marker_subtype TEXT,
                    start_time REAL NOT NULL,
                    end_time REAL NOT NULL,
                    confidence REAL NOT NULL,
                    evidence TEXT NOT NULL,
                    explanation TEXT,
                    speaker TEXT,
                    constitutional_source TEXT NOT NULL,
                    analysis_method TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """)
            
            # Rapport indicators table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rapport_indicators (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    value REAL NOT NULL,
                    trend TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    contributing_markers_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """)
            
            # Sessions table for analysis sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_sessions (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    session_name TEXT NOT NULL,
                    analysis_config TEXT,  -- JSON config
                    processing_time REAL,
                    marker_count INTEGER DEFAULT 0,
                    rapport_indicator_count INTEGER DEFAULT 0,
                    constitutional_source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    status TEXT DEFAULT 'pending',
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """)
            
            # Create indices for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_segments_conversation_time ON transcript_segments(conversation_id, start_time)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_markers_conversation_type ON constitutional_markers(conversation_id, marker_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_markers_time ON constitutional_markers(start_time)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rapport_conversation_time ON rapport_indicators(conversation_id, timestamp)")
            
            # Set schema version
            cursor.execute("PRAGMA user_version = 1")
            
            self.connection.commit()
            logger.info("Database schema created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database schema: {e}")
            return False
    
    def _verify_database(self) -> bool:
        """Verify database integrity"""
        try:
            cursor = self.connection.cursor()
            
            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}
            
            required_tables = {
                'conversations', 'transcript_segments', 'constitutional_markers',
                'rapport_indicators', 'analysis_sessions'
            }
            
            if not required_tables.issubset(tables):
                missing = required_tables - tables
                logger.error(f"Missing required tables: {missing}")
                return False
            
            # Test integrity check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            if result != "ok":
                logger.error(f"Database integrity check failed: {result}")
                return False
            
            logger.info("Database verification successful")
            return True
            
        except Exception as e:
            logger.error(f"Database verification failed: {e}")
            return False
    
    def _test_database_access(self) -> bool:
        """Test database access with simple query"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversations")
            cursor.fetchone()
            return True
        except Exception as e:
            logger.error(f"Database access test failed: {e}")
            return False