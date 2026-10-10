import re
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("python.pdf")
documents = loader.load()

def clean_text(text):
    text = text.encode("utf-8", "ignore").decode("utf-8")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

clean_docs = []
for doc in documents:
    doc.page_content = clean_text(doc.page_content)
    clean_docs.append(doc)

print(clean_docs[11].page_content[:500])
