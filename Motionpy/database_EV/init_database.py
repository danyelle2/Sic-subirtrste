# database_EV/init_database.py
import sys
from .models import TableCreator
from .config import DatabaseConfig

def initialize_database():
    """
    Inicializa o banco de dados criando todas as tabelas.
    Deve ser executado UMA vez no início da aplicação.
    """
    print("Inicializando banco de dados MotionPy (MySQL)...")
    print("Criando estrutura de tabelas...")
    
    try:
        TableCreator.create_tables()
        print("Banco de dados inicializado com sucesso!")
        print("Tabelas criadas ou verificadas:")
        print("   ├── usuarios")
        print("   ├── historico_aprendizado") 
        print("   └── progresso_usuario")
        print("Dica: Execute este script apenas uma vez para criar a estrutura.")
    except Exception as e:
        print(f"ERRO: Falha ao inicializar o banco de dados. Verifique a conexão e as permissões. Erro: {e}")

def reset_database():
    """
    PERIGO: Apaga e recria todas as tabelas.
    Use apenas em desenvolvimento para limpar dados de teste.
    """
    print("ALERTA: Esta operação apagará TODOS os dados!")
    confirm = input("Tem certeza que deseja resetar o banco? (digite 'SIM' para confirmar): ")
    
    if confirm.upper() == 'SIM':
        try:
            print("Removendo tabelas...")
            TableCreator.drop_tables()
            
            print("Recriando tabelas...")
            TableCreator.create_tables()
            
            print("Banco de dados resetado com sucesso!")
        except Exception as e:
            print(f"ERRO ao resetar o banco: {e}")
    else:
        print("Reset cancelado.")

def check_database_status():
    """
    Verifica se o banco está corretamente inicializado
    """
    print("Verificando status do banco de dados MySQL...")
    conn = None
    try:
        conn = DatabaseConfig.get_connection()
        if not conn:
             print("ERRO: Não foi possível conectar ao MySQL. Verifique as configurações em config.py.")
             return False

        cursor = conn.cursor()
        
        required_tables = {'usuarios', 'historico_aprendizado', 'progresso_usuario'}
        existing_tables = set()

        db_name = DatabaseConfig.DB_NAME
        
        cursor.execute(f"SHOW TABLES FROM `{db_name}`")
        
        for (table_name,) in cursor.fetchall():
            existing_tables.add(table_name)

        missing_tables = required_tables - existing_tables
        
        if not missing_tables:
            print("Banco de dados OK - Todas as tabelas existem.")
            return True
        else:
            print(f"Banco incompleto. Tabelas faltando: {', '.join(missing_tables)}. Execute initialize_database().")
            return False
            
    except Exception as e:
        print(f"Erro ao verificar banco: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

# Execução direta via linha de comando
if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "reset":
            reset_database()
        elif command == "status":
            check_database_status()
        elif command == "help":
            print("Uso: python init_database.py [comando]")
            print("Comandos:")
            print("   reset   - Apaga e recria todas as tabelas (PERIGO)")
            print("   status  - Verifica se o banco está OK")
            print("   help    - Mostra esta ajuda")
            print("Sem comando - Inicializa o banco normalmente")
        else:
            print(f"Comando '{command}' não reconhecido. Use 'help'.")
    else:
        initialize_database()