import re

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


def clean_text(text):
    text = text.encode("utf-8", "ignore").decode("utf-8")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


loader = PyPDFLoader("python.pdf")
docs = loader.load()

# 1. Clean every page first
for doc in docs:
    doc.page_content = clean_text(doc.page_content)

# 2. Then split the clean pages into small chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 3. Store the chunks (in class the whole pages were stored by mistake)
db = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")

print(f"Indexed {len(chunks)} chunks")
