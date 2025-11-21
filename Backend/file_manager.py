# backend/file_manager.py
import os
from PyPDF2 import PdfReader
from docx import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI

# Initialize OpenAI and Chroma
embeddings = OpenAIEmbeddings()
db = Chroma(collection_name="my_files", embedding_function=embeddings, persist_directory="vector_db")
llm = OpenAI(model_name="gpt-4")

# Set the root directory for file search (you can change this to a specific folder if you prefer)
ROOT_DIR = "C:\\"  # For Windows (change to "/" for Linux/Mac)

# File extensions to consider
ALLOWED_EXTENSIONS = (".pdf", ".docx", ".txt")

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def find_file_path(filename_query):
    # Search the whole system for the file (be careful, this can take time!)
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        for file in filenames:
            if filename_query.lower() in file.lower() and file.lower().endswith(ALLOWED_EXTENSIONS):
                return os.path.join(dirpath, file)
    return None

def load_and_index_file(filename_query):
    file_path = find_file_path(filename_query)
    if not file_path:
        print(f"File '{filename_query}' not found.")
        return False

    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    elif file_path.endswith(".txt"):
        text = extract_text_from_txt(file_path)
    else:
        print("Unsupported file type.")
        return False

    db.add_texts([text], metadatas=[{"file": os.path.basename(file_path), "path": file_path}])
    db.persist()
    print(f"Indexed: {file_path}")
    return True

def search_files(query):
    results = db.similarity_search(query)
    for doc in results:
        print(f"From {doc.metadata['file']} ({doc.metadata.get('path', 'unknown')}):")
        print(doc.page_content[:500])
        print("...")

def summarize_query(query):
    results = db.similarity_search(query)
    if not results:
        return "No relevant files found."
    combined_text = "\n\n".join([doc.page_content for doc in results])
    prompt = f"Summarize this:\n{combined_text}"
    summary = llm.predict(prompt)
    return summary
