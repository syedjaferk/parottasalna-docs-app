
import os
import uuid
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.stores import InMemoryByteStore
from langchain_classic.retrievers.multi_vector import MultiVectorRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

GROQ_API_KEY=os.environ["GROQ_API_KEY"]
PDF_PATH="./python.pdf"
DOC_ID_KEY="doc_id"

embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorstore=Chroma(
    collection_name="multi_vector_demo",
    embedding_function=embeddings,
    persist_directory="./vectorstore"
)

store=InMemoryByteStore()

retriever=MultiVectorRetriever(
    vectorstore=vectorstore,
    byte_store=store,
    id_key=DOC_ID_KEY,
)

llm=ChatGroq(
    api_key=GROQ_API_KEY,
    model="openai/gpt-oss-120b",
    temperature=0,
)

def summarize(txt):
    val = llm.invoke(f"Summarize:\n\n{txt}").content
    print(val)
    return val

def keywords(txt):
    val = llm.invoke(f"Extract comma separated keywords:\n\n{txt}").content
    print(val)
    return val

def questions(txt):
    val = llm.invoke(f"Generate five questions answered by this document:\n\n{txt}").content
    print(val)
    return val
docs=PyPDFLoader(PDF_PATH).load()


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


summary_docs=[]
keyword_docs=[]
question_docs=[]
parents=[]

for d in clean_docs[:10]:
    did=str(uuid.uuid4())
    parents.append((did,d))
    summary_docs.append(Document(page_content=summarize(d.page_content),metadata={DOC_ID_KEY:did,"type":"summary"}))
    keyword_docs.append(Document(page_content=keywords(d.page_content),metadata={DOC_ID_KEY:did,"type":"keywords"}))
    question_docs.append(Document(page_content=questions(d.page_content),metadata={DOC_ID_KEY:did,"type":"questions"}))

vectorstore.add_documents(summary_docs)
vectorstore.add_documents(keyword_docs)
vectorstore.add_documents(question_docs)

store.mset(parents)

while True:
    q=input("Question (exit): ")
    if q.lower()=="exit":
        break
    results=retriever.invoke(q)
    context="\n\n".join(r.page_content for r in results)
    ans=llm.invoke(f"Answer from only this context:\n{context}\nQuestion:{q}")
    print(ans.content)
