# database_EV/config.py
import mysql.connector
from mysql.connector import Error

class DatabaseConfig:
    """Configurações do banco de dados MySQL"""

    # --- Configurações de Conexão MySQL ---
    DB_HOST = "localhost"
    DB_USER = "root" 
    DB_PASSWORD = ""
    DB_NAME = "motion"
 
    
    @classmethod
    def get_connection(cls):
        """Retorna uma conexão com o banco MySQL"""
        conn = None
        try:
            conn = mysql.connector.connect(
                host=cls.DB_HOST,
                database=cls.DB_NAME,
                user=cls.DB_USER,
                password=cls.DB_PASSWORD,
            )
            return conn

        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")
            return None

    @classmethod
    def get_db_info(cls):
        """Retorna informações de conexão do banco de dados"""
        return f"MySQL Host: {cls.DB_HOST}, Database: {cls.DB_NAME}"