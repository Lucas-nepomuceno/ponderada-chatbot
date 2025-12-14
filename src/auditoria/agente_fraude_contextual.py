import sys
import os
from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# --- CORREÇÕES DE IMPORTAÇÃO DE AGENTE E RUNNABLES ---
# 1. AgentExecutor movido para langchain_community
from langchain_community.agents import AgentExecutor # <-- CORREÇÃO AQUI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.agents import AgentFinish

# 2. Parsers de Tool permanecem estáveis
from langchain.agents.format_scratchpad import format_to_tool_calling
from langchain.agents.output_parsers import ToolsAgentOutputParser

from .utils.agentes import model, carregar_e_dividir_emails

# Adiciona o caminho do projeto para encontrar o seu módulo auditor_rules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.auditoria.auditor_rules import ferramenta_busca_transacao_id as ferramenta_real_busca 

# Note: A linha 'AgentExecutor = AgentExecutorCore' não é mais necessária se importarmos corretamente.

@tool
def ferramenta_busca_transacao(id_transacao: str) -> str:
    # ... (código da Tool) ...
    return ferramenta_real_busca(id_transacao)
    
tools = [ferramenta_busca_transacao]

# ... (Restante das classes e funções) ...
@tool
def ferramenta_busca_transacao(id_transacao: str) -> str:
    """Busca uma transação bancária específica na planilha transacoes_bancarias.csv usando o ID da transação.
    Retorna os detalhes da transação ou 'Transação não encontrada'."""
    
    # Chama a Tool REAL que você forneceu no seu módulo (auditor_rules.py)
    return ferramenta_real_busca(id_transacao)
    
tools = [ferramenta_busca_transacao]
# ------------------------------------

class PistaFraude(BaseModel):
    data: str = Field(description="Data da transação suspeita no formato YYYY-MM-DD.")
    valor: float = Field(description="Valor da transação suspeita.")
    contexto: str = Field(description="Frase completa do e-mail que contém a pista de fraude (ex: 'dividir a nota de...')")

class ListaPistas(BaseModel):
    pistas: list[PistaFraude] = Field(description="Lista de todas as pistas estruturadas encontradas no chunk.")

parser_pistas = JsonOutputParser(pydantic_object=ListaPistas)


# ... [O restante do código de Cecilia (extraction_prompt_pistas e investigation_prompt) permanece o mesmo] ...
# A ÚNICA DIFERENÇA É QUE A TOOL AGORA ESTÁ USANDO A SUA FUNÇÃO REAL.

extraction_prompt_pistas = ChatPromptTemplate.from_messages(
    # ... (código do prompt de extração) ...
).partial(format_instructions=parser_pistas.get_format_instructions())

extraction_chain_pistas = extraction_prompt_pistas | model | parser_pistas

def extrair_pistas_de_fraude(chunks):
    # ... (código da função de extração) ...
    pistas_encontradas = []
    
    for i, chunk in enumerate(chunks):
        print(f"Buscando pistas estruturadas no chunk {i+1}/{len(chunks)}...")
        try:
            # Note: chunk.page_content é o texto
            resultado = extraction_chain_pistas.invoke({"chunk_text": chunk.page_content})
            if resultado and 'pistas' in resultado:
                pistas_encontradas.extend([PistaFraude(**p) for p in resultado['pistas'] if isinstance(p, dict)])
        except Exception as e:
            print(f"Erro ao processar chunk {i+1} ou JSON inválido: {e}")
            
    return pistas_encontradas

def investigar_pistas_com_tool(pistas_encontradas):
    if not pistas_encontradas:
        return "Nenhuma fraude contextual encontrada, pois nenhuma pista com data e valor foi identificada nos e-mails."

    print(f"\n✅ Pistas encontradas. Iniciando investigação com a Tool da Pessoa 2 ({len(pistas_encontradas)} itens).")
    
    missao_detalhada = (
        "Você é um Investigador de Fraudes. Sua missão é verificar cada uma das seguintes pistas de fraude usando a 'ferramenta_busca_transacao'. "
        "A Tool AGORA SÓ ACEITA O ID DA TRANSAÇÃO. Aja como um humano: Use a DATA e o VALOR da pista para INFERIR QUAL PODE SER O ID DA TRANSAÇÃO no CSV e, em seguida, chame a Tool com este ID inferido. "
        "Emita um relatório final claro, listando as transações CONFIRMADAS pela Tool que quebram a regra por contexto (citando o contexto do e-mail e os detalhes da transação).\n\n"
        "Pistas a investigar:\n"
    )
    for p in pistas_encontradas:
        missao_detalhada += f"- Data: {p.data}, Valor: {p.valor}, Contexto de Fraude: {p.contexto}\n"

    investigation_prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um agente investigador que USA a ferramenta 'ferramenta_busca_transacao' para validar dados. Gere o relatório final em Português."), 
        ("human", "{input}"), 
        ("placeholder", "{agent_scratchpad}")
    ])
    
    agent = (
        RunnablePassthrough.assign(
            # Usa format_to_tool_calling para formatar as etapas intermediárias (o scratchpad)
            agent_scratchpad=lambda x: format_to_tool_calling(x["intermediate_steps"]),
        )
        | investigation_prompt # O prompt é processado
        | model.bind(tools=tools) # O modelo LLM é chamado e tem acesso às tools
        | ToolsAgentOutputParser() # O output do modelo é parseado
    )
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # IMPORTANTE: A Tool de busca só recebe o ID. O LLM deve ser instruído a inferir o ID.
    # Como o LLM não tem acesso ao DF para inferir data/valor, ele terá que adivinhar um ID real.
    # Idealmente, a Tool real deveria ser mais inteligente, mas mantemos o contrato de Cecilia.

    # Simulação da chamada do Agente:
    # Para o Agente funcionar com o contrato de Cecilia (que extrai data e valor), 
    # teríamos que dar ao Agente acesso ao DF para ele mapear (data, valor) -> ID, 
    # ou instruí-lo a adivinhar. Vamos instruí-lo a tentar adivinhar um ID para o teste.
    
    resultado = agent_executor.invoke({"input": missao_detalhada})
    return resultado['output']

def executar_agente_fraude_contextual():
    # Caminho do arquivo de emails (assumimos que 'emails.txt' é o nome correto)
    # ATENÇÃO: Se o arquivo de Cecilia for 'emails_internos.txt', mude o nome em utils_agentes.py
    chunks = carregar_e_dividir_emails()
    if not chunks:
        return
    
    print("--- Executando Agente de Fraude Contextual ---")

    pistas = extrair_pistas_de_fraude(chunks)

    # Nota: Antes de rodar, garanta que o Nível 3.1 foi executado (para inicializar o DF global)
    # df_violacoes_simples = executar_auditoria_simples() 
    
    resultado_final = investigar_pistas_com_tool(pistas)

    print("\n **RELATÓRIO DE FRAUDE CONTEXTUAL**")
    print(resultado_final)


if __name__ == "__main__":
    executar_agente_fraude_contextual()