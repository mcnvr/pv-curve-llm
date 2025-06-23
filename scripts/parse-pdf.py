"""
**This script is AI generated**

This script designed to parse a PDF file and extract the text into chunks for embedding into a vector database.
It should automatically detect the paragraphs and split them in that method, not including titles, citations, etc.

**AI generated documentation**

Usage:
1. Place this script in a directory containing a PDF file
2. Run: python parse-pdf.py
3. The script will automatically find the first PDF file in the directory
4. Creates chunks.txt with each paragraph on a separate line
5. Filters out citations, headers, footers, page numbers, and image references
6. Preserves meaningful text content suitable for embedding

Requirements:
- PyPDF2 or pdfplumber (install with: pip install PyPDF2 pdfplumber)
- PDF file in the same directory as the script

Output:
- chunks.txt: Contains clean text chunks, one paragraph per line
"""

import os
import re
import glob
try:
    import pdfplumber
    PDF_LIBRARY = 'pdfplumber'
except ImportError:
    try:
        import PyPDF2
        PDF_LIBRARY = 'PyPDF2'
    except ImportError:
        print("Error: Please install pdfplumber or PyPDF2: pip install pdfplumber")
        exit(1)

def find_pdf_file():
    pdf_files = glob.glob("*.pdf")
    if not pdf_files:
        print("No PDF files found in current directory")
        return None
    return pdf_files[0]

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^Page \d+.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*Figure \d+.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*Table \d+.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\[?\d+\]?\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'^\s*References?\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*Bibliography\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*Abstract\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*Keywords?:.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*DOI:.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*©.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[A-Z\s]{10,}\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\.{3,}\s*\d*\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*_{3,}\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*-{3,}\s*$', '', text, flags=re.MULTILINE)
    return text.strip()

def is_valid_paragraph(text):
    if len(text.strip()) < 50:
        return False
    if re.match(r'^\s*\d+\.?\s*$', text):
        return False
    if re.match(r'^\s*[A-Z\s]{5,}\s*$', text):
        return False
    if re.search(r'^\s*(Figure|Table|Chart|Graph|Image)\s+\d+', text, re.IGNORECASE):
        return False
    if re.search(r'^\s*(References?|Bibliography|Appendix|Index)\s*$', text, re.IGNORECASE):
        return False
    if text.count('.') < 1 and len(text) > 100:
        return False
    return True

def split_into_chunks(text):
    chunks = []
    
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    
    current_chunk = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        test_chunk = current_chunk + " " + sentence if current_chunk else sentence
        
        if len(test_chunk) > 3000:
            if current_chunk and is_valid_paragraph(current_chunk):
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk = test_chunk
    
    if current_chunk and is_valid_paragraph(current_chunk):
        chunks.append(current_chunk.strip())
    
    return chunks

def extract_with_pdfplumber(pdf_path):
    chunks = []
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + " "
        
        full_text = clean_text(full_text)
        chunks = split_into_chunks(full_text)
    
    return chunks

def extract_with_pypdf2(pdf_path):
    chunks = []
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        full_text = ""
        
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + " "
        
        full_text = clean_text(full_text)
        chunks = split_into_chunks(full_text)
    
    return chunks

def extract_pdf_chunks(pdf_path):
    if PDF_LIBRARY == 'pdfplumber':
        return extract_with_pdfplumber(pdf_path)
    else:
        return extract_with_pypdf2(pdf_path)

def save_chunks(chunks, output_file='chunks.txt'):
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            f.write(chunk + '\n\n')

def main():
    pdf_file = find_pdf_file()
    if not pdf_file:
        return
    
    print(f"Processing PDF: {pdf_file}")
    print(f"Using library: {PDF_LIBRARY}")
    
    chunks = extract_pdf_chunks(pdf_file)
    
    if chunks:
        save_chunks(chunks)
        print(f"Successfully extracted {len(chunks)} chunks to chunks.txt")
        print(f"Average chunk length: {sum(len(c) for c in chunks) // len(chunks)} characters")
    else:
        print("No valid text chunks found in PDF")

if __name__ == "__main__":
    main()