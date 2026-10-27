from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from pypdf import PdfReader
from dotenv import load_dotenv
load_dotenv()


KNOWLEDGE_DIR = "knowledge"
INDEX_PATH = "index/store.json"
TOPIC = "the loaded documents"  # change this to describe your PDFs

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


SYSTEM_PROMPT = f"""You are a helpful assistant that answers questions about {TOPIC}.
For any question about {TOPIC}, call the search_knowledge tool first
and answer ONLY from what it returns.
Mention the source for facts you use, like (file.pdf, p. 3).
If the answer is not in the search results, say: "I don't know based on the provided documents."
Remember what the user tells you in this conversation, such as their name.
Greetings and small talk do not need the tool."""


def make_agent(store):
    @tool
    def search_knowledge(query: str) -> str:
        """Search the loaded documents for relevant passages. Use this for any
        question about the content of the documents."""
        results = store.similarity_search(query, k=4)
        return "\n\n".join(
            f"[{r.metadata.get('source')}, p. {r.metadata.get('page')}] {r.page_content}"
            for r in results
        )

    return create_agent(
        model=model,
        tools=[search_knowledge],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
    )



def ask_agent(agent, question, thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config=config
    )

    return result["messages"][-1].content

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def load_pdf_documents(folder=KNOWLEDGE_DIR):
    docs = []
    for pdf_path in sorted(Path(folder).glob("*.pdf")):
        reader = PdfReader(str(pdf_path))
        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                docs.append(
                    Document(
                        page_content=text,
                        metadata={"source": pdf_path.name, "page": page_number},
                    )
                )
    return docs


def build_index():
    docs = load_pdf_documents()
    if not docs:
        raise RuntimeError(
            "No text found. Put text-based PDFs in the knowledge/ folder."
        )
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    chunks = splitter.split_documents(docs)
    print(f"{len(docs)} pages -> {len(chunks)} chunks")

    store = InMemoryVectorStore(embedding=get_embeddings())
    store.add_documents(chunks)

    Path(INDEX_PATH).parent.mkdir(parents=True, exist_ok=True)
    store.dump(INDEX_PATH)
    return store


def get_vector_store():
    if Path(INDEX_PATH).exists():
        return InMemoryVectorStore.load(INDEX_PATH, get_embeddings())
    return build_index()