from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import os

# Path to the vector database
DB_LOCATION = "./vector_db"
# Model used to embed the text into vectors
EMBEDDING_MODEL = "mxbai-embed-large"
# Number of vectors to return for each RAG query. Increasing this will increase the accuracy of the RAG query but will reduce speed.
NUM_VECTORS = 10

def retriever():
    """
    Returns a retriever object that can be used to query the vector database.
    """
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    
    if not os.path.exists(DB_LOCATION):
        raise FileNotFoundError(f"Chroma database not found at {DB_LOCATION}. Please run the training script /train.py first.")
    
    vector_store = Chroma(
        collection_name="pv-curves",
        persist_directory=DB_LOCATION,
        embedding_function=embeddings
    )

    return vector_store.as_retriever(search_kwargs={"k": NUM_VECTORS})