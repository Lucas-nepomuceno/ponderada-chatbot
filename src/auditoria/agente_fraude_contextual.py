from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.agentes import model, carregar_e_dividir_emails
from auditor_rules import ferramenta_busca_transacao_id as ferramenta_real_busca 
from langchain.agents import create_agent
    
tools = [ferramenta_real_busca]

class PistaFraude(BaseModel):
    data: str = Field(description="Data da transação suspeita no formato YYYY-MM-DD.")
    valor: float = Field(description="Valor da transação suspeita.")
    contexto: str = Field(description="Frase completa do e-mail que contém a pista de fraude (ex: 'dividir a nota de...')")

class ListaPistas(BaseModel):
    pistas: list[PistaFraude] = Field(description="Lista de todas as pistas estruturadas encontradas no chunk.")

parser_pistas = JsonOutputParser(
    pydantic_object=ListaPistas
)

extraction_prompt_pistas = ChatPromptTemplate.from_messages([
    (
        "system",
        "Você é um extrator de informações.\n"
        "Extraia as pistas do texto fornecido.\n"
        "Responda EXCLUSIVAMENTE com JSON VÁLIDO.\n"
        "Escape corretamente TODAS as aspas internas em strings usando \\\".\n"
        "Nunca inclua texto fora do JSON.\n"
        "{format_instructions}"
    ),
    (
        "human",
        "{chunk_text}"
    )
]).partial(
    format_instructions=parser_pistas.get_format_instructions()
)

extraction_chain_pistas = (
    extraction_prompt_pistas
    | model
    | parser_pistas
)

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
    )

    input_agent = "Pistas a investigar:\n"

    for p in pistas_encontradas:
        input_agent += f"- Data: {p.data}, Valor: {p.valor}, Contexto de Fraude: {p.contexto}\n"

    agent = create_agent(model, tools, system_prompt=missao_detalhada)

    resultado = agent.invoke({"input": input_agent})
    return resultado

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
    mensagem_final = resultado_final["input"][-1]

    print("\n **RELATÓRIO DE FRAUDE CONTEXTUAL**")
    print(mensagem_final.content)


if __name__ == "__main__":
    executar_agente_fraude_contextual()