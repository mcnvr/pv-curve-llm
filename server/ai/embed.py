'''
Goal Architecture:
Script to train model on the data.
embed.py
    - Currently this is handled in vector.py, need to separate.

Creation and interaction with vector database, calls embed.py if requested.
vector.py

Main script to run the trained model accessing the vector database.
main.py

PV-Curve calculation and graph generation prompted by model.

Returns in formatted response to the server
    - All handled in main.py?

Need to differentiate running locally and run by the server.
'''

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import glob
import shutil

def create_vector_database(db_location="./chroma_db", force_overwrite=False):
    """
    Create or update the vector database with documents from ./data/ directory.
    
    Args:
        db_location (str): Path where the database should be stored
        force_overwrite (bool): If True, overwrite existing database without asking
    
    Returns:
        bool: True if database was created/updated successfully
    """
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    
    add_documents = not os.path.exists(db_location)

    if os.path.exists(db_location):
        print(f"Database already exists at {db_location}")
        if force_overwrite:
            print("Force overwrite enabled. Deleting existing database...")
            shutil.rmtree(db_location)
            add_documents = True
            print("Existing database deleted")
        else:
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
        
        if not txt_files:
            print("❌ No .txt files found in ./data/ directory")
            return False
        
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
        
        if not documents:
            print("❌ No valid content found in text files")
            return False
        
    vector_store = Chroma(
        collection_name="pv_curve_notes",
        persist_directory=db_location,
        embedding_function=embeddings
    )

    if add_documents:
        vector_store.add_documents(documents=documents, ids=ids)
        print(f"✅ Added {len(documents)} documents to vector database")
    
    print("✅ Vector database ready")
    return True

if __name__ == "__main__":
    print("🔄 PV-Curve Database Training Script")
    print("=" * 40)
    
    success = create_vector_database()
    
    if success:
        print("\n🎉 Training completed successfully!")
        print("You can now run main.py or interactive_main.py")
    else:
        print("\n❌ Training failed. Please check your data files.")