from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
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


system_prompt = """You are a friendly assistant for GreenTech.
For any question about GreenTech (products, warranty, returns, shipping, support),
call the search_knowledge tool first and answer ONLY from what it returns.
If the answer is not in the search results, say: "I don't know based on the provided information."
Remember what the user tells you in this conversation, such as their name.
Greetings and small talk do not need the tool."""


def make_agent(store):
    @tool
    def search_knowledge(query: str) -> str:
        """Search the GreenTech knowledge base. Use this for any question about
        GreenTech's products, warranty, returns, shipping, or support."""
        results = store.similarity_search(query, k=3)
        return "\n".join(r.page_content for r in results)


    return create_agent(
        model=model,
        tools=[search_knowledge],
        system_prompt=system_prompt,
        checkpointer=InMemorySaver()
    )


def ask_agent(agent, question, thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config=config
    )

    return result["messages"][-1].content

