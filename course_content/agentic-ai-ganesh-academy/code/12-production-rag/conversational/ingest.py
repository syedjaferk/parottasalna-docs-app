# ingest.py

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

loader = PyPDFLoader("./python.pdf")

docs = loader.load()

import re
def clean_text(text):
    text = text.encode("utf-8", "ignore").decode("utf-8")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Chunk Documents
clean_docs = []
for doc in docs:
    doc.page_content = clean_text(doc.page_content)
    clean_docs.append(doc)


splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = splitter.split_documents(clean_docs)

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma.from_documents(
    chunks,
    embedding,
    persist_directory="chroma_db"
)

# (langchain_chroma saves to persist_directory automatically)
print("Done")
