from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore



def load_chunks(path="knowledge/greentech.txt"):
    text = Path(path).read_text(encoding="utf-8")
    doc = Document(page_content=text, metadata={"source" : "greentech.txt"})
    splitter = RecursiveCharacterTextSplitter(chunk_size=130, chunk_overlap=30)
    return splitter.split_documents([doc])


def build_vector_store(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    store = InMemoryVectorStore(embedding=embeddings)
    store.add_documents(chunks)
    return store


