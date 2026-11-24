# database_EV/models.py
from .config import DatabaseConfig
import mysql.connector
from mysql.connector import Error

class TableCreator:
    
    @staticmethod
    def create_tables():
        conn = DatabaseConfig.get_connection()
        cursor = conn.cursor()
        
        sql_commands = [
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                idUsuarios BIGINT PRIMARY KEY AUTO_INCREMENT,
                email VARCHAR(255) NOT NULL UNIQUE,
                nome VARCHAR(255) NOT NULL,
                data_nascimento DATE,
                cpf VARCHAR(14),
                telefone VARCHAR(20),
                senha_criptografada VARCHAR(255) NOT NULL,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            
            """
            CREATE TABLE IF NOT EXISTS historico_aprendizado (
                idHistorico BIGINT PRIMARY KEY AUTO_INCREMENT,
                letra_tentada CHAR(1) NOT NULL,
                letra_reconhecida CHAR(1) NOT NULL,
                acertou TINYINT NOT NULL COMMENT '0=Errou, 1=Acertou',
                data_tentativa DATETIME DEFAULT CURRENT_TIMESTAMP,
                idUsuarios BIGINT NOT NULL,
                FOREIGN KEY (idUsuarios) REFERENCES usuarios(idUsuarios) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            
            """
            CREATE TABLE IF NOT EXISTS progresso_usuario (
                idProgresso BIGINT PRIMARY KEY AUTO_INCREMENT,
                nivel VARCHAR(20) DEFAULT 'Iniciante' COMMENT 'Iniciante, Intermediário, Avançado',
                total_tentativas INT DEFAULT 0,
                acertos INT DEFAULT 0,
                aula_atual INT DEFAULT 1,
                idUsuarios BIGINT NOT NULL UNIQUE,
                FOREIGN KEY (idUsuarios) REFERENCES usuarios(idUsuarios) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        ]
        
        try:
            for command in sql_commands:
                cursor.execute(command)
                
            conn.commit()
            print("Todas as tabelas foram criadas/verificadas com sucesso no MySQL!")
            
        except Error as e:
            print(f"Erro MySQL ao criar tabelas: {e}")
            conn.rollback()
        except Exception as e:
             print(f"Erro inesperado ao criar tabelas: {e}")
             conn.rollback()
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    
    @staticmethod
    def drop_tables():
        """Remove todas as tabelas (apenas para desenvolvimento)"""
        conn = DatabaseConfig.get_connection()
        cursor = conn.cursor()
        
        tables_to_drop = [
            "progresso_usuario",
            "historico_aprendizado",
            "usuarios"
        ]
        
        try:
            for table in tables_to_drop:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
            
            conn.commit()
            print("Todas as tabelas foram removidas do MySQL!")
            
        except Error as e:
            print(f"Erro MySQL ao remover tabelas: {e}")
            conn.rollback()
        except Exception as e:
            print(f"Erro inesperado ao remover tabelas: {e}")
            conn.rollback()
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()