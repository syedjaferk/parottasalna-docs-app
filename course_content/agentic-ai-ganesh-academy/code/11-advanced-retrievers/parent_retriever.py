import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_groq import ChatGroq

from langchain_core.stores import InMemoryStore

load_dotenv()

PDF_PATH = "./python.pdf"
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
MODEL = "llama-3.3-70b-versatile"

PARENT_CHUNK_SIZE = 3000
PARENT_OVERLAP = 200

CHILD_CHUNK_SIZE = 300
CHILD_OVERLAP = 50

COLLECTION_NAME = "parent_document_demo"
CHROMA_DIR = "./vectorstore"


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR,
)

docstore = InMemoryStore()


parent_splitter = RecursiveCharacterTextSplitter(
    chunk_size=PARENT_CHUNK_SIZE,
    chunk_overlap=PARENT_OVERLAP,
)

child_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHILD_CHUNK_SIZE,
    chunk_overlap=CHILD_OVERLAP,
)


retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=docstore,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)


print("Loading PDF...")
loader = PyPDFLoader(PDF_PATH)
documents = loader.load()

print(f"Loaded {len(documents)} pages")

import re
def clean_text(text):
    text = text.encode("utf-8", "ignore").decode("utf-8")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Chunk Documents
clean_docs = []
for doc in documents:
    doc.page_content = clean_text(doc.page_content)
    clean_docs.append(doc)


print("Creating parent-child index...")
retriever.add_documents(clean_docs)

print("Indexing completed.")


llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=MODEL,
    temperature=0,
)


def ask(question: str):

    docs = retriever.invoke(question)

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
You are an expert assistant.

Use ONLY the supplied context and give examples.

Context:
{context}

Question:
{question}

Answer:
"""

    answer = llm.invoke(prompt)

    return answer.content, docs



print("=" * 60)
print("Parent Document Retriever Ready")
print("=" * 60)

while True:

    q = input("\nQuestion (type exit): ")

    if q.lower() == "exit":
        break

    response, docs = ask(q)

    print("\nRetrieved Parent Documents")
    print("-" * 60)

    for i, doc in enumerate(docs, start=1):
        print(f"\nParent Document {i}")
        print(doc.page_content[:600])
        print("...")

    print("\nAnswer")
    print("-" * 60)
    print(response)
