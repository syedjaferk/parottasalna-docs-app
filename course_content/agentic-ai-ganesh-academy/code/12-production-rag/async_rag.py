import os
import asyncio

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.retrievers import BM25Retriever
from langchain_groq import ChatGroq



loader = PyPDFLoader("python.pdf")

documents = loader.load()


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


splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)

chunks = splitter.split_documents(clean_docs)



embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding,
    persist_directory="./db"
)

vector_retriever = db.as_retriever(
    search_kwargs={"k":5}
)



bm25 = BM25Retriever.from_documents(chunks)

bm25.k = 5



llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.environ["GROQ_API_KEY"]
)


async def vector_search(query):

    return await vector_retriever.ainvoke(query)


async def keyword_search(query):

    return await bm25.ainvoke(query)


async def metadata_search(query):

    return db.similarity_search(
        query,
        k=3,
        filter={"source":"python.pdf"}
    )



async def retrieve(query):

    vector_docs, keyword_docs, metadata_docs = await asyncio.gather(

        vector_search(query),

        keyword_search(query),

        metadata_search(query)

    )

    return vector_docs + keyword_docs + metadata_docs



def remove_duplicates(docs):

    unique = {}

    for doc in docs:

        unique[doc.page_content] = doc

    return list(unique.values())



async def ask_llm(query, docs):

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    prompt = f"""

Answer only from the given context.

Context:

{context}

Question:

{query}

"""

    response = await llm.ainvoke(prompt)

    return response.content


async def rag(query):

    docs = await retrieve(query)

    docs = remove_duplicates(docs)

    answer = await ask_llm(query, docs)

    return answer



if __name__ == "__main__":

    question = input("Question: ")

    answer = asyncio.run(rag(question))

    print("\nAnswer:\n")

    print(answer)
