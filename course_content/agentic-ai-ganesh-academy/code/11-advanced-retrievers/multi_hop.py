from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

loader = TextLoader("./data.txt")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20
)

docs = splitter.split_documents(documents)

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectordb = Chroma.from_documents(
    docs,
    embedding
)

retriever = vectordb.as_retriever(search_kwargs={"k":2})

question = "How does S3 reduce storage cost?"

first_docs = retriever.invoke(question)

print("FIRST HOP")
print("-"*40)

for doc in first_docs:
    print(doc.page_content)
