"""
CLI Database Manager
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, no modifications
"""

import logging
from typing import Optional
from pathlib import Path

from src.lib.storage import DatabaseManager, ConversationStore, MarkerStore, SessionStore
from src.lib.storage.database import DatabaseConfig
from .config import CLIConfig

logger = logging.getLogger(__name__)

# Global database manager instance
_db_manager: Optional[DatabaseManager] = None
_conversation_store: Optional[ConversationStore] = None
_marker_store: Optional[MarkerStore] = None
_session_store: Optional[SessionStore] = None


def get_database_manager(cli_config: CLIConfig) -> DatabaseManager:
    """Get or create database manager instance"""
    global _db_manager
    
    if _db_manager is None:
        db_config = DatabaseConfig(
            database_path=cli_config.database_path,
            constitutional_source=cli_config.constitutional_source
        )
        _db_manager = DatabaseManager(db_config)
    
    return _db_manager


def get_conversation_store(cli_config: CLIConfig) -> ConversationStore:
    """Get or create conversation store instance"""
    global _conversation_store
    
    if _conversation_store is None:
        db_manager = get_database_manager(cli_config)
        _conversation_store = ConversationStore(db_manager)
    
    return _conversation_store


def get_marker_store(cli_config: CLIConfig) -> MarkerStore:
    """Get or create marker store instance"""
    global _marker_store
    
    if _marker_store is None:
        db_manager = get_database_manager(cli_config)
        _marker_store = MarkerStore(db_manager)
    
    return _marker_store


def get_session_store(cli_config: CLIConfig) -> SessionStore:
    """Get or create session store instance"""
    global _session_store
    
    if _session_store is None:
        db_manager = get_database_manager(cli_config)
        _session_store = SessionStore(db_manager)
    
    return _session_store


def ensure_database_connection(cli_config: CLIConfig, passphrase: str) -> bool:
    """Ensure database is connected with passphrase"""
    db_manager = get_database_manager(cli_config)
    
    if Path(cli_config.database_path).exists():
        return db_manager.connect(passphrase)
    else:
        return db_manager.initialize_database(passphrase)


def disconnect_all():
    """Disconnect all database connections"""
    global _db_manager
    
    if _db_manager:
        _db_manager.disconnect()
        _db_manager = None
    
    # Reset store instances
    global _conversation_store, _marker_store, _session_store
    _conversation_store = None
    _marker_store = None
    _session_store = None