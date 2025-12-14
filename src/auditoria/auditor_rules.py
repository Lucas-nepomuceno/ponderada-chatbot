import pandas as pd
import numpy as np
import json
# Importa a função de carregamento/limpeza do módulo irmão (data_preparation)
from data_preparation import carregar_e_limpar_transacoes 

# ==============================================================================
# 0. INICIALIZAÇÃO DE VARIÁVEL GLOBAL E REGRAS
# ==============================================================================

# Variável global para o DataFrame LIMPO (acesso para as Tools)
df_transacoes_global = None

# Estruturação das regras de validação (Nível 3.1)
REGRAS_AUDITORIA_SIMPLES = [
    {
        "id": "R001_LIMITE_ALTO",
        "tipo": "Limite de Gasto",
        "campo": "valor",
        "operador": ">",
        "limite": 500.00,
        "justificativa": "Violação: Transação acima de $500,00 (Categoria A), requer PO formal e aprovação do CFO."
    },
    {
        "id": "R003_RESTRITO_LOCAL",
        "tipo": "Gasto Proibido (Local)",
        "campo": "descricao",
        "operador": "contem",
        "valor_proibido": "Hooters",
        "justificativa": "Violação: O restaurante 'Hooters' é banido da lista de reembolso corporativo."
    },
    {
        "id": "R004_PROIBIDO_ITENS",
        "tipo": "Gasto Proibido (Itens)",
        "campo": "descricao",
        "operador": "contem",
        "valor_proibido": ["kits de mágica", "algemas", "strippers", "espada", "katana", "whupf.com", "beterraba", "vela artesanal", "chrysler sebring", "frigobar", "pay-per-view", "spa"],
        "justificativa": "Violação: Compra/uso de item estritamente proibido."
    }
]

# ==============================================================================
# 1. FUNÇÃO PRINCIPAL DE EXECUÇÃO E VALIDAÇÃO (NÍVEL 3.1)
# ==============================================================================

def executar_auditoria_simples() -> pd.DataFrame:
    """
    Função principal. Garante o carregamento do DF e executa a validação Nível 3.1.
    """
    global df_transacoes_global

    # 1. Carregamento (Chamamos a função do data_preparation.py)
    if df_transacoes_global is None:
        df_transacoes_global = carregar_e_limpar_transacoes()
    
    # 2. Verifica se o carregamento foi bem-sucedido (resolve o NoneType)
    if df_transacoes_global is None or df_transacoes_global.empty:
        print("🔴 Erro: Não foi possível carregar o DataFrame para auditoria.")
        return pd.DataFrame()

    df = df_transacoes_global.copy()
    df['violacoes'] = [[] for _ in range(len(df))]
    
    # 3. Execução da Validação de Regras
    for regra in REGRAS_AUDITORIA_SIMPLES:
        filtro = pd.Series([False] * len(df))
        campo = regra["campo"]

        # Filtro A: Limite de Valor
        if regra["tipo"] == "Limite de Gasto" and regra["operador"] == ">":
            filtro = (df[campo] > regra["limite"])

        # Filtro B: Conteúdo Proibido
        elif regra["operador"] == "contem":
            termos = regra["valor_proibido"]
            if not isinstance(termos, list):
                termos = [termos]
            
            for termo in termos:
                filtro |= df[campo].str.contains(termo, case=False, na=False) 

        # Adiciona o ID da regra à lista 'violacoes' (CORREÇÃO DE TypeError)
        df.loc[filtro, 'violacoes'] = df.loc[filtro, 'violacoes'].apply(lambda x: x + [regra["id"]])

    # 4. Formatação do Resultado
    df_violacoes = df[df['violacoes'].str.len() > 0].copy()
    
    # Mapeia IDs para justificativas
    regra_map = {r['id']: r['justificativa'] for r in REGRAS_AUDITORIA_SIMPLES}
    df_violacoes['justificativa_detalhada'] = df_violacoes['violacoes'].apply(
        lambda ids: "\n".join([f"({id}) {regra_map.get(id, 'Regra Desconhecida')}" for id in ids])
    )

    return df_violacoes[['id_transacao', 'data', 'funcionario', 'descricao', 'valor', 'justificativa_detalhada']]

# ==============================================================================
# 2. FERRAMENTA (TOOL) PARA O AGENTE 3.2 (Pessoa 3)
# ==============================================================================

def ferramenta_busca_transacao_id(id_transacao: str) -> str:
    """
    TOOL: Busca e retorna os detalhes de uma transação específica usando seu ID.
    """
    global df_transacoes_global
    
    # Garante que o DataFrame foi inicializado
    if df_transacoes_global is None:
        # Se for chamado diretamente (pelo Agente), executa a auditoria para inicializar o DF
        executar_auditoria_simples() 
    
    if df_transacoes_global is None:
        return "ERRO: O DataFrame de transações não pôde ser carregado. Execute a auditoria primeiro."

    df = df_transacoes_global
    id_transacao = str(id_transacao).strip()

    resultado = df[df['id_transacao'].astype(str).str.strip() == id_transacao]

    if resultado.empty:
        return f"Nenhuma transação encontrada com o ID: {id_transacao}"
    else:
        transacao_encontrada = resultado.iloc[0].to_dict()
        return json.dumps(transacao_encontrada, indent=2, default=str)

if __name__ == "__main__":
    # Teste de execução do módulo
    df_violacoes = executar_auditoria_simples()
    if not df_violacoes.empty:
        print("\n--- Violações Nível 3.1 ---")
        print(df_violacoes.head().to_markdown(index=False))
        # Teste da Tool
        primeiro_id = df_violacoes['id_transacao'].iloc[0]
        print(f"\n--- Teste da Tool com ID {primeiro_id} ---")
        print(ferramenta_busca_transacao_id(primeiro_id))