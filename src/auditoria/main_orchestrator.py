
from auditor_rules import executar_auditoria_simples, ferramenta_busca_transacao_id
from agentes_conspiracao import executar_agente_conspiracao
from agente_fraude_contextual import executar_agente_fraude_contextual


def main():
    print("="*60)
    print("INÍCIO DA AUDITORIA AUTOMÁTICA (Pessoa 2: Data e Regras)")
    print("="*60)

    # 1. EXECUÇÃO NÍVEL 3.1: Detecção por Regras Simples
    # (ESSENCIAL: Isso carrega e inicializa o DataFrame global para as Tools)
    df_violacoes_simples = executar_auditoria_simples()

    print("\n" + "="*60)
    print("RESULTADO DO NÍVEL 3.1: DETECÇÃO POR REGRAS")
    print("="*60)
    
    if not df_violacoes_simples.empty:
        print(f"TOTAL DE VIOLAÇÕES ENCONTRADAS: {len(df_violacoes_simples)}")
        print("\n--- Amostra de Violações ---")
        print(df_violacoes_simples.head(10).to_markdown(index=False))
    else:
        print("Nenhuma violação direta de compliance encontrada no Nível 3.1.")

    # 2. TESTE DA FERRAMENTA (TOOL)
    print("\n" + "="*60)
    print("TESTE DA FERRAMENTA DE BUSCA PARA O AGENTE (Pessoa 3)")
    print("="*60)
    
    # Testamos um ID real encontrado nas violações, se houver
    teste_id = df_violacoes_simples['id_transacao'].iloc[0] if not df_violacoes_simples.empty else 'ID_1'
    detalhes_tool = ferramenta_busca_transacao_id(teste_id)
    print(f" Busca de detalhes para o ID: {teste_id}")
    print(detalhes_tool)


    # 3. EXECUÇÃO DOS AGENTES DE IA (NÍVEL 2 e NÍVEL 3.2)
    print("\n" + "="*60)
    print("--- INÍCIO DA ANÁLISE DE CONTEXTO (PESSOA 3 - AGENTES) ---")
    print("="*60)
    
    # Nível 2: Análise de Conspiração
    print("\n[NÍVEL 2: AGENTE DE CONSPIRAÇÃO]")
    executar_agente_conspiracao()

    # Nível 3.2: Fraude Contextual (Usará a Tool que acabamos de testar)
    print("\n[NÍVEL 3.2: AGENTE DE FRAUDE CONTEXTUAL]")
    executar_agente_fraude_contextual()


if __name__ == "__main__":
    main()