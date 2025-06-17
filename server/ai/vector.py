from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from pypdf import PdfReader
import os
import pandas as pd
import shutil

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
        print("✓ Existing database deleted")
    else:
        print("Using existing database")
        add_documents = False

if add_documents:
    documents = []
    ids = []

    print("Processing PDF...")
    reader = PdfReader("pv_curve_notes.pdf")
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    lines = text.split("\n")
    for i in range(0, len(lines), 8):
        section = "\n".join(lines[i:i+8])
        if section.strip():
            documents.append(Document(page_content=section.strip()))
            ids.append(f"{i//8}")
    
vector_store = Chroma(
    collection_name="pv_curve_notes",
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_documents:
    vector_store.add_documents(documents=documents, ids=ids)
    print(f"Added {len(documents)} documents to vector database")

retriever = vector_store.as_retriever(
    search_kwargs={"k": 10}
)