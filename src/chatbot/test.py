import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langchain.tools import tool
from chatbot.rag.vector_store.qdrant_vector_store import VectorStore
from langchain.agents import create_agent

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
vector_store = VectorStore()

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

model = init_chat_model(
    "openai:nvidia/nvidia-nemotron-nano-9b-v2",
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY,
)

tools = [retrieve_context]


prompt = (
    "Você tem acesso a uma tool que contém trechos da política de compliance da Dunder Mufflin. Responda as perguntas do usuário em um tom respeitoso, de preferência citando integralmente o artigo usado por você."
    "Use a tool para responder as perguntas a seguir. RESPONDA SEMPRE EM PORTUGUÊS"
)
    
agent = create_agent(model, tools, system_prompt=prompt)

def start_chat():
    print("\nVocê está no chat de dúvidas sobre a política de compliance da Dunder Mufflin. Caso queira sair, mande 'sair'.\n")

    history = [
        {
            "role": "system",
            "content": prompt
        }
    ]

    while True:
        query = input("Usuário: ")

        if query.lower() == "sair":
            break

        # Adiciona a nova mensagem do usuário no histórico
        history.append({"role": "user", "content": query})

        # Invoca o agente com TODO o histórico
        result = agent.invoke({
            "messages": history
        })

        # Pega a última resposta do modelo
        resposta = result["messages"][-1].content
        print("\nChat: " + resposta + "\n")

        # Salva a resposta do modelo no histfórico
        history.append({"role": "assistant", "content": resposta})



if __name__ == "__main__":

    start_chat()

