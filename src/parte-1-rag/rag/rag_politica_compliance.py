from langchain_text_splitters import RecursiveCharacterTextSplitter
from vector_store import qdrant_vector_store

## Função utilitária que muda o header para ter apenas uma sequencia de igual
def create_chunks(text):
    chunks = text.split("==============================================================================") # Cleaning
    chunks = include_header(chunks)
    return chunks

## Função utilitária para incluir o header no chunk
def include_header(text):
    i = 0
    chunks_com_header = [text[0]]
    for i in range(1, len(text) - 1, 2):
        chunk_com_header = text[i] + text[i+1]
        chunks_com_header.append(chunk_com_header)
    return chunks_com_header

if __name__ == "__main__":

    file = open("documents/politica_compliance.txt", "r", encoding="utf8")
    try:
        content = file.read() # Load
        chunks = create_chunks(content)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        documents = splitter.create_documents(texts=chunks) # Chunking

        vector_store = qdrant_vector_store.VectorStore() # loading on the Vector Store

        document_ids = vector_store.add_documents(documents)

    finally:
        file.close()  # Ensures the file is closed