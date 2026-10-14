from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
load_dotenv()


model = init_chat_model("groq:openai/gpt-oss-120b")



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


def answer_question(store, question, k=3):
    results = store.similarity_search(question, k=k)
    context = "\n".join(r.page_content for r in results)

    prompt = f"""
        You are a helpful assistant for GreenTech.
        Answer the question using ONLY the context below.
        If the answer is not in the context, say: "I don't know based on the provided information."

        context: {context}
        question: {question}
        """

    reply = model.invoke(prompt)
    return reply.content, results



    