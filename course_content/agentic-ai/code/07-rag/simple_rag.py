import os
import re

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_groq import ChatGroq
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables (e.g., API keys) from a local .env file
load_dotenv()


def load_and_clean_pdf(pdf_path):
    """Loads a PDF file, cleans its contents, and splits it into smaller chunks."""
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    cleaned_docs = clean_docs(documents)
    split_docs = split_pdf(cleaned_docs)
    return split_docs


def clean_docs(documents):
    """Normalizes whitespace, removes null bytes, and sanitizes text encoding for each document."""
    cleaned_docs = []
    for doc in documents:
        # Handle objects with page_content attributes vs raw text strings
        if hasattr(doc, "page_content"):
            text = doc.page_content
        else:
            text = str(doc)

        # Replace multiple whitespace characters with a single space
        text = re.sub(r"\s+", " ", text)
        # Remove null control characters
        text = re.sub(r"\x00", "", text)
        # Drop invalid UTF-8 sequences and decode back to a clean string
        text = text.encode("utf-8", "ignore").decode("utf-8")
        text = text.strip()

        # Update the document object or append the cleaned text
        if hasattr(doc, "page_content"):
            doc.page_content = text
            cleaned_docs.append(doc)
        else:
            cleaned_docs.append(text)
    return cleaned_docs


def split_pdf(documents):
    """Splits documents into smaller overlapping chunks to optimize for embedding and retrieval."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    return splitter.split_documents(documents)


def build_vectorstore(chunks):
    """Initializes Ollama embeddings and loads or creates a persistent Chroma vector database."""
    # Setup local Ollama embeddings using the nomic-embed-text model
    embeddings = OllamaEmbeddings(model="nomic-embed-text", num_ctx=8192)
    print("started")

    # Connect to an existing Chroma collection if the directory exists; otherwise, create a new one from chunks
    if os.path.exists("./chromadb"):
        vectorstore = Chroma(
            collection_name="pdf_rag_collection",
            persist_directory="./chromadb",
            embedding_function=embeddings,
        )
    else:
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name="pdf_rag_collection",
            persist_directory="./chromadb",
        )
    print("completed")
    return vectorstore


def initial_setup(pdf_path):
    """Executes the end-to-end ingestion pipeline: loads, cleans, chunks, and vectorizes the PDF."""
    chunks = load_and_clean_pdf(pdf_path)
    vectorstore = build_vectorstore(chunks)
    return vectorstore


def retrieve(vectorstore, question):
    """Retrieves the top-k most relevant document chunks from the vector store based on the user question."""
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    # Prefix query to optimize retrieval performance for certain embedding models
    response = retriever.invoke(f"search_query: {question}")
    return response


def build_prompt(context: str, question: str):
    """Constructs a strict prompt instructing the LLM to answer using only the provided context."""
    return f"""
    Answer the question using ONLY the context below. If the answer is not in the
    context, say you don't know.
    Context: {context}
    Question: {question}
    Answer:
    """


def generate_answer(prompt):
    """Invokes the ChatGroq LLM to generate an answer based on the constructed prompt."""
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
    response = llm.invoke(prompt)
    return response.content


def rag_query(vectorstore, question):
    """Coordinates the full RAG pipeline: retrieves relevant chunks, builds a prompt, and generates the final answer."""
    response = retrieve(vectorstore, question)
    # Combine retrieved document contents into a single context string
    context = "\n\n".join(doc.page_content for doc in response)
    prompt = build_prompt(context, question)
    answer = generate_answer(prompt)
    return answer


if __name__ == "__main__":
    pdf_path = "./python.pdf"
    # Set up the vector store index from the target PDF
    vectorstore = initial_setup(pdf_path)

    # Prompt the user for a question, execute the RAG pipeline, and display the response
    q = input("Ask a question ")
    ans = rag_query(vectorstore, q)
    print(ans)
