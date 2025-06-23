from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import os

def get_retriever_for_api():
    """
    Create a retriever for the existing Chroma database without interactive prompts.
    This function is intended for API usage where the database already exists.
    """
    embeddings_api = OllamaEmbeddings(model="mxbai-embed-large")
    
    db_location_api = "./ai/chroma_db"
    
    if not os.path.exists(db_location_api):
        raise FileNotFoundError(f"Chroma database not found at {db_location_api}. Please run the training script first.")
    
    vector_store_api = Chroma(
        collection_name="pv_curve_notes",
        persist_directory=db_location_api,
        embedding_function=embeddings_api
    )
    
    return vector_store_api.as_retriever(search_kwargs={"k": 10})

def get_retriever_for_local():
    embeddings_local = OllamaEmbeddings(model="mxbai-embed-large")
    
    db_location_local = "./chroma_db"
    
    if not os.path.exists(db_location_local):
        raise FileNotFoundError(f"Chroma database not found at {db_location_local}. Please run 'python embed.py' first to create the database.")
    
    vector_store_local = Chroma(
        collection_name="pv_curve_notes",
        persist_directory=db_location_local,
        embedding_function=embeddings_local
    )
    
    return vector_store_local.as_retriever(search_kwargs={"k": 10})

try:
    retriever = get_retriever_for_local()
except FileNotFoundError:
    retriever = None

if __name__ == "__main__":
    from embed import create_vector_database
    
    print("🔄 Vector Database Management")
    print("=" * 30)
    print("This will create/update the vector database using embed.py")
    print()
    
    success = create_vector_database()
    
    if success:
        try:
            retriever = get_retriever_for_local()
            print("✅ Retriever updated successfully")
        except Exception as e:
            print(f"❌ Error creating retriever: {e}")
    else:
        print("❌ Database creation failed")