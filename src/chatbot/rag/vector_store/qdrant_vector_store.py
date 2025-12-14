from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

class VectorStore():
    def __init__(self):
        self.client = QdrantClient(
            url=QDRANT_URL, 
            api_key=QDRANT_API_KEY
        )

        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

        if not self.client.collection_exists("ponderada-parte-1"):
            self.client.create_collection(
            collection_name="ponderada-parte-1",
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
        )
            
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name="ponderada-parte-1",
            embedding=self.embeddings,
        )

    def add_documents(self, chunks):
        return self.vector_store.add_documents(documents=chunks)
    
    def similarity_search(self, query, k):
        return self.vector_store.similarity_search(query, k=k)


