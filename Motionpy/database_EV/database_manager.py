# database_EV/database_manager.py
import mysql.connector
from mysql.connector import Error
from .config import DatabaseConfig

class DatabaseManager:
    """Classe principal para gerenciar todas as operações do banco"""
    
    def __init__(self):
        self.conn = DatabaseConfig.get_connection()
        # Consome resultados pendentes para evitar "Unread result found"
        if self.conn and self.conn.is_connected():
            try:
                while self.conn.next_result():
                    pass
            except:
                pass
    
    # ========== MÉTODOS PARA USUÁRIOS ==========
    
    def criar_usuario(self, email, nome, senha_criptografada, data_nascimento=None, cpf=None, telefone=None):
        """Cria um novo usuário no sistema"""
        cursor = self.conn.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                INSERT INTO usuarios 
                (email, nome, data_nascimento, cpf, telefone, senha_criptografada) 
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (email, nome, data_nascimento, cpf, telefone, senha_criptografada))
            
            user_id = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO progresso_usuario (idUsuarios) 
                VALUES (%s)
            ''', (user_id,))
            
            self.conn.commit()
            print(f"Usuário {nome} criado com ID: {user_id}")
            return user_id
            
        except Error as e:
            self.conn.rollback()
            if e.errno == 1062:
                print(f"Erro: Email {email} já existe")
            else:
                print(f"Erro ao criar usuário (MySQL Error Code {e.errno}): {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado: {e}")
            self.conn.rollback()
            return None
    
    def verificar_login(self, email, senha):
        """Verifica se email e senha estão corretos"""
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute('''
                SELECT idUsuarios, nome, email FROM usuarios 
                WHERE email = %s AND senha_criptografada = %s
            ''', (email, senha))
            
            usuario = cursor.fetchone()
            
            if usuario:
                print(f"Login bem-sucedido para: {usuario['nome']}")
            else:
                print("Login falhou - credenciais inválidas")
                
            return usuario
            
        except Error as e:
            print(f"Erro no login (MySQL Error): {e}")
            return None
    
    def buscar_usuario_por_id(self, user_id):
        """Busca usuário pelo ID"""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuarios WHERE idUsuarios = %s', (user_id,))
        return cursor.fetchone()
    
    def listar_usuarios(self):
        """Lista todos os usuários"""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute('SELECT idUsuarios, nome, email, data_cadastro FROM usuarios')
        return cursor.fetchall()
    
    # ========== MÉTODOS PARA HISTÓRICO ==========
    
    def registrar_tentativa(self, user_id, letra_tentada, letra_reconhecida):
        """Registra uma tentativa de gesto do usuário"""
        cursor = self.conn.cursor(dictionary=True)
        
        try:
            acertou = 1 if letra_tentada.upper() == letra_reconhecida.upper() else 0
            
            cursor.execute('''
                INSERT INTO historico_aprendizado 
                (letra_tentada, letra_reconhecida, acertou, idUsuarios) 
                VALUES (%s, %s, %s, %s)
            ''', (letra_tentada.upper(), letra_reconhecida.upper(), acertou, user_id))
            
            cursor.execute('''
                UPDATE progresso_usuario 
                SET total_tentativas = total_tentativas + 1,
                    acertos = acertos + %s
                WHERE idUsuarios = %s
            ''', (acertou, user_id))
            
            self._atualizar_nivel_usuario(user_id)
            
            self.conn.commit()
            
            status = "ACERTOU" if acertou else "ERROU"
            print(f"{status} - Usuário {user_id}: tentou '{letra_tentada}', reconhecido '{letra_reconhecida}'")
            
            return {
                'acertou': bool(acertou),
                'letra_tentada': letra_tentada,
                'letra_reconhecida': letra_reconhecida
            }
            
        except Error as e:
            print(f"Erro ao registrar tentativa (MySQL Error): {e}")
            self.conn.rollback()
            return None
    
    def _atualizar_nivel_usuario(self, user_id):
        """Atualiza o nível do usuário baseado na performance"""
        cursor = self.conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT acertos, total_tentativas 
            FROM progresso_usuario 
            WHERE idUsuarios = %s
        ''', (user_id,))
        
        progresso = cursor.fetchone()
        
        if progresso and progresso['total_tentativas'] is not None and progresso['total_tentativas'] > 0:
            acertos = progresso['acertos'] if progresso['acertos'] is not None else 0
            total_tentativas = progresso['total_tentativas']
            
            taxa_acerto = (acertos / total_tentativas) * 100
            
            if taxa_acerto >= 80:
                novo_nivel = 'Avançado'
            elif taxa_acerto >= 60:
                novo_nivel = 'Intermediário'
            else:
                novo_nivel = 'Iniciante'
            
            cursor.execute('''
                UPDATE progresso_usuario 
                SET nivel = %s 
                WHERE idUsuarios = %s
            ''', (novo_nivel, user_id))
    
    def obter_historico_usuario(self, user_id, limite=20):
        """Obtém o histórico de tentativas do usuário"""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT * FROM historico_aprendizado 
            WHERE idUsuarios = %s 
            ORDER BY data_tentativa DESC 
            LIMIT %s
        ''', (user_id, limite))
        return cursor.fetchall()
    
    # ========== MÉTODOS PARA PROGRESSO ==========
    
    def obter_progresso_usuario(self, user_id):
        """Obtém o progresso atual do usuário"""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT * FROM progresso_usuario 
            WHERE idUsuarios = %s
        ''', (user_id,))
        return cursor.fetchone()
    
    def atualizar_aula_atual(self, user_id, nova_aula):
        """Atualiza a aula atual do usuário"""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute('''
            UPDATE progresso_usuario 
            SET aula_atual = %s 
            WHERE idUsuarios = %s
        ''', (nova_aula, user_id))
        self.conn.commit()
        print(f"Usuário {user_id} avançou para aula {nova_aula}")
    
    def obter_estatisticas_usuario(self, user_id):
        """Obtém estatísticas completas do usuário"""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT 
                COALESCE(p.total_tentativas, 0) as total_tentativas,
                COALESCE(p.acertos, 0) as acertos,
                COALESCE(p.aula_atual, 1) as aula_atual,
                COALESCE(p.nivel, 'Iniciante') as nivel,
                COUNT(h.idHistorico) as total_tentativas_historico,
                COALESCE(SUM(CASE WHEN h.acertou = 1 THEN 1 ELSE 0 END), 0) as acertos_historico
            FROM progresso_usuario p
            LEFT JOIN historico_aprendizado h ON p.idUsuarios = h.idUsuarios
            WHERE p.idUsuarios = %s
            GROUP BY p.idUsuarios, p.total_tentativas, p.acertos, p.aula_atual, p.nivel
        ''', (user_id,))
        
        stats = cursor.fetchone()
        
        if not stats:
            return {
                'total_tentativas': 0,
                'acertos': 0,
                'aula_atual': 1,
                'nivel': 'Iniciante',
                'total_tentativas_historico': 0,
                'acertos_historico': 0
            }
        
        return stats
    
    def close(self):
        """Fecha a conexão com o banco"""
        if self.conn and self.conn.is_connected():
            self.conn.close()