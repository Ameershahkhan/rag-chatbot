from rag_core import load_chunks, build_vector_store

chunks = load_chunks()
store = build_vector_store(chunks)

question = "What is the name of the CEO?"
results = store.similarity_search(question, k=2)

for r in results:
    print("-", r.page_content)