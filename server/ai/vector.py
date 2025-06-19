from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import glob
import shutil

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

# Only run database creation logic when this script is run directly
if __name__ == "__main__":
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    db_location = "./chroma_db"
    add_documents = not os.path.exists(db_location)

    if os.path.exists(db_location):
        print(f"Database already exists at {db_location}")
        overwrite = input("Do you want to overwrite the existing database? (y/n): ").lower().strip()
        if overwrite in ['y', 'yes']:
            print("Deleting existing database...")
            shutil.rmtree(db_location)
            add_documents = True
            print("Existing database deleted")
        else:
            print("Using existing database")
            add_documents = False

    if add_documents:
        documents = []
        ids = []

        print("Processing text files from ./data/ directory...")
        txt_files = glob.glob("./data/*.txt")
        print(f"Found {len(txt_files)} text files")
        
        for file_path in txt_files:
            filename = os.path.basename(file_path)
            print(f"Processing {filename}...")
            
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            chunks = text.split('\n\n')
            
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    documents.append(Document(page_content=chunk.strip()))
                    ids.append(f"{filename}_{i}")
            
            print(f"✓ Added {len([c for c in chunks if c.strip()])} chunks from {filename}")
        
        print(f"Total documents created: {len(documents)}")
        
    vector_store = Chroma(
        collection_name="pv_curve_notes",
        persist_directory=db_location,
        embedding_function=embeddings
    )

    if add_documents:
        vector_store.add_documents(documents=documents, ids=ids)
        print(f"Added {len(documents)} documents to vector database")

    # k: number of documents to retrieve from the vector database
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 10}
    )