# database_EV/teste_db.py
from . import db 
from .init_database import initialize_database, check_database_status 

print("--- 0. Verificando e Inicializando Banco de Dados ---")
if not check_database_status():
    initialize_database()
    print("Tentando inicializar o banco. Se houver erro, verifique as credenciais!")
else:
    print("Banco de dados já OK.")

# --- 1. Teste de Conexão ---
print("\n--- 1. Teste de Conexão ---")
conn = db.conn
if conn and conn.is_connected():
    print("✅ Sucesso: Conexão MySQL estabelecida!")
else:
    print("❌ Erro Crítico: Falha na conexão MySQL. Verifique config.py e servidor.")
    exit()

# --- 2. Teste de Criação de Usuário (C) ---
print("\n--- 2. Teste de Criação de Usuário ---")
email_teste = "teste.migracao@motion.com"
user_id = db.criar_usuario(
    email=email_teste,
    nome="Usuario Teste",
    senha_criptografada="hash_seguro_123",
    data_nascimento="1990-01-01"
)

if user_id:
    print(f"✅ Sucesso: Usuário criado com ID: {user_id}")
else:
    cursor = db.conn.cursor(dictionary=True)
    cursor.execute("SELECT idUsuarios FROM usuarios WHERE email = %s", (email_teste,))
    result = cursor.fetchone()
    if result:
        user_id = result['idUsuarios']
        print(f"✅ Usuário já existia. Usando ID: {user_id}")
    else:
        print("❌ Erro: Falha ao criar usuário")
        db.close()
        exit()

# --- 3. Teste de Login (R) ---
print("\n--- 3. Teste de Login ---")
usuario_logado = db.verificar_login(email_teste, "hash_seguro_123")
if usuario_logado:
    print(f"✅ Sucesso: Login verificado para {usuario_logado['nome']}")
else:
    print("❌ Erro: Login falhou com credenciais corretas.")

# --- 4. Teste de Registro de Histórico e Atualização (U) ---
print("\n--- 4. Teste de Registro e Progresso ---")
db.registrar_tentativa(user_id, letra_tentada='A', letra_reconhecida='B')
db.registrar_tentativa(user_id, letra_tentada='A', letra_reconhecida='A')

progresso = db.obter_progresso_usuario(user_id)
if progresso and progresso['total_tentativas'] == 2 and progresso['acertos'] == 1:
    print(f"✅ Sucesso: Progresso atualizado. Total: 2, Acertos: 1, Nível: {progresso['nivel']}")
else:
    print("❌ Erro: Progresso não foi atualizado corretamente.")

# --- 5. Teste de Estatísticas (R) ---
print("\n--- 5. Teste de Obter Estatísticas ---")
stats = db.obter_estatisticas_usuario(user_id)
if stats and stats['total_tentativas'] == 2 and stats['acertos_historico'] == 1:
    print("✅ Sucesso: Estatísticas completas obtidas corretamente.")
else:
    print("❌ Erro: Falha ao obter estatísticas ou dados incorretos.")

# --- Fim ---
db.close()
print("\n--- Testes concluídos ---")