import json
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .utils.agentes import model, carregar_e_dividir_emails
# Nota: A importação do modelo já estava correta.


class Conspiracao(BaseModel):
    conspiracao_verificada: bool = Field(description="True se houver evidências claras de conspiração de Michael Scott contra Toby Flenderson.")
    evidencias: list[str] = Field(description="Uma lista de citações cruas dos e-mails que provam a conspiração (ex: 'De: Michael, Para: Dwight, Data: XX/XX. Conteúdo: Vamos humilhar Toby novamente').")
    justificativa_final: str = Field(description="Um resumo da conclusão do agente.")

parser_conclusao = JsonOutputParser(pydantic_object=Conspiracao)

extraction_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Você é um extrator de evidências de baixo nível. Analise o texto e extraia **TODAS** as frases ou blocos de e-mail que mostram Michael Scott conspirando, humilhando, ou planejando algo contra Toby Flenderson. Não adicione contexto, apenas extraia as frases de e-mail relevantes. Se não houver evidências, retorne EXATAMENTE o texto 'NENHUMA EVIDÊNCIA'."
        ),
        ("human", "Analise o seguinte bloco de e-mails: {chunk_text}")
    ]
)
extraction_chain = extraction_prompt | model


def extrair_evidencias_por_chunk(chunks):
    todas_as_evidencias = []
    
    for i, chunk in enumerate(chunks):
        print(f"Processando chunk {i+1}/{len(chunks)}...")
        resultado = extraction_chain.invoke({"chunk_text": chunk.page_content})
        
        if "NENHUMA EVIDÊNCIA" not in resultado.content:
            linhas_encontradas = [line.strip() for line in resultado.content.split('\n') if line.strip()]
            todas_as_evidencias.extend(linhas_encontradas)
            
    return todas_as_evidencias

consolidation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Você é o Agente de Auditoria de IA, responsável pela conclusão final. Você recebeu uma lista de possíveis evidências de conspiração. Analise a lista e preencha o JSON estritamente conforme o schema. RESPONDA SEMPRE EM PORTUGUÊS. Use as evidências fornecidas para a 'justificativa_final'.\n{format_instructions}"
        ),
        (
            "human",
            "Evidências encontradas:\n{evidencias_encontradas}"
        )
    ]
).partial(format_instructions=parser_conclusao.get_format_instructions())

consolidation_chain = consolidation_prompt | model | parser_conclusao

def executar_agente_conspiracao():
    chunks = carregar_e_dividir_emails()
    if not chunks:
        return

    print("--- Executando Agente de Verificação de Conspiração (Nível 2) ---")
    
    evidencias = extrair_evidencias_por_chunk(chunks)
    
    if not evidencias:
        evidencias_texto = "Nenhuma evidência de conspiração encontrada nos e-mails."
    else:
        evidencias_texto = "\n".join(evidencias)
        
    resultado_final = consolidation_chain.invoke({"evidencias_encontradas": evidencias_texto})

    print("\n**RELATÓRIO DE CONSPIRAÇÃO**")
    print(f"**Conspiração Verificada:** {'SIM' if resultado_final.get('conspiracao_verificada') else 'NÃO'}")
    print(f"**Justificativa:** {resultado_final.get('justificativa_final')}")
    if resultado_final.get('evidencias'):
        print("\n**Evidências:**")
        for ev in resultado_final['evidencias']:
            print(f"- {ev}")

if __name__ == "__main__":
    executar_agente_conspiracao()