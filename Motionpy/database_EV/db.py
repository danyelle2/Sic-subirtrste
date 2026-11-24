# database_EV/db.py
from .database_manager import DatabaseManager

# Cria uma instância global do DatabaseManager
db = DatabaseManager()

def test_connection():
    """Testa a conexão com o banco"""
    return db.conn and db.conn.is_connected()