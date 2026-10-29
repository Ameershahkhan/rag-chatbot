from rag_core import load_chunks, build_vector_store, make_agent, ask_agent

store = build_vector_store(load_chunks())
agent = make_agent(store)

print(ask_agent(agent, "Hi, my name is Ameer.", "user-1"))
print(ask_agent(agent, "How long is the battery guarantee?", "user-1"))
print(ask_agent(agent, "What is my name?", "user-1"))

print("--- different thread ---")
print(ask_agent(agent, "What is my name?", "user-2"))