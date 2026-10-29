from rag_core import load_chunks, build_vector_store, answer_question

store = build_vector_store(load_chunks())

questions = [
    "How long is the battery guarantee?",
    "How many days do I have to return a product?",
    "What is the name of the CEO?",
]

for q in questions:
    answer, sources = answer_question(store, q)
    print("Q:", q)
    print("A:", answer)
    print()