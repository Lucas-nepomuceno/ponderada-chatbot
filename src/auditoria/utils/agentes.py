import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

model = init_chat_model(
    "openai:nvidia/nvidia-nemotron-nano-9b-v2",
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY,
)

def carregar_e_dividir_emails(caminho="documents/emails.txt"):
    try:
        with open(caminho, "r", encoding="utf8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo {caminho} não encontrado.")
        return []
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000,     
        chunk_overlap=200,      
        separators=["\n\n\n", "\n\n", "\n", " ", ""]
    )
    document_chunks = splitter.create_documents([content])
    print(f"Documento de E-mails dividido em {len(document_chunks)} partes (chunks).")
    return document_chunks