import pandas as pd
import os


import pandas as pd
import os

# --- LÓGICA DE CAMINHO ---
# Usamos o método mais robusto (que deve estar correto)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DO_PROJETO = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
CAMINHO_CSV = os.path.join(CAMINHO_DO_PROJETO, 'documents', 'transacoes_bancarias.csv')

def carregar_e_limpar_transacoes() -> pd.DataFrame:
    """
    Carrega o CSV, limpa nomes, padroniza 'data' e 'valor'.
    Retorna o DF ou None se falhar.
    """
    print(f"🔍 Tentando carregar CSV de: {CAMINHO_CSV}") 
    try:
        df = pd.read_csv(CAMINHO_CSV)
    except FileNotFoundError:
        print(f"ERRO FATAL: Arquivo CSV não encontrado. Caminho: {CAMINHO_CSV}")
        return None
    
    # 1. Padronização de Colunas, Data e Valor
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_', regex=False)
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    try:
        df['valor'] = pd.to_numeric(df['valor'].astype(str).str.replace(r'[$,()]', '', regex=True), errors='coerce')
    except:
        pass
        
    # 2. Garantia de ID de Transação
    if 'id_transacao' not in df.columns or df['id_transacao'].isnull().any():
        df['id_transacao'] = [f'ID_{i+1}' for i in range(len(df))]
        
    print(f"✅ Limpeza concluída. {len(df)} registros.")
    return df

if __name__ == "__main__":
    # Teste de execução do módulo
    df_teste = carregar_e_limpar_transacoes()
    if df_teste is not None:
        print("\n--- Amostra do DataFrame Limpo ---")
        print(df_teste.head().to_markdown(index=False))