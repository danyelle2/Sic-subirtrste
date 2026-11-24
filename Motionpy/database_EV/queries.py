# database_EV/queries.py
"""
Módulo com consultas SQL reutilizáveis para MySQL
"""

class Queries:
    """Classe com todas as consultas SQL do sistema"""
    
    # 1. BUSCAR USUÁRIO POR EMAIL
    BUSCAR_USUARIO_POR_EMAIL = """
        SELECT * FROM usuarios WHERE email = %s
    """
    
    # 2. HISTÓRICO COMPLETO DO USUÁRIO
    HISTORICO_USUARIO = """
        SELECT 
            u.nome,
            h.letra_tentada,
            h.letra_reconhecida,
            CASE WHEN h.acertou = 1 THEN 'Sim' ELSE 'Não' END as acertou,
            h.data_tentativa
        FROM historico_aprendizado h
        JOIN usuarios u ON h.idUsuarios = u.idUsuarios
        WHERE u.idUsuarios = %s
        ORDER BY h.data_tentativa DESC
    """
    
    # 3. ESTATÍSTICAS DE PROGRESSO
    ESTATISTICAS_USUARIO = """
        SELECT 
            p.nivel,
            p.total_tentativas,
            p.acertos,
            ROUND((p.acertos * 100.0 / p.total_tentativas), 2) as taxa_acerto, 
            p.aula_atual
        FROM progresso_usuario p
        WHERE p.idUsuarios = %s
    """
    
    # 4. TOP LETRAS MAIS PRATICADAS
    TOP_LETRAS_USUARIO = """
        SELECT 
            letra_tentada,
            COUNT(*) as total_tentativas,
            SUM(acertou) as acertos
        FROM historico_aprendizado
        WHERE idUsuarios = %s
        GROUP BY letra_tentada
        ORDER BY total_tentativas DESC
        LIMIT 5
    """
    
    # 5. PROGRESSO GERAL DA TURMA
    PROGRESSO_TURMA = """
        SELECT 
            u.nome,
            p.total_tentativas,
            p.acertos,
            p.aula_atual,
            p.nivel
        FROM progresso_usuario p
        JOIN usuarios u ON p.idUsuarios = u.idUsuarios
        ORDER BY p.acertos DESC
    """