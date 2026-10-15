from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_core import load_chunks, build_vector_store, answer_question


app = Flask(__name__)
CORS(app)


# Built ONCE when the server starts, not on every request
chunks = load_chunks()
store = build_vector_store(chunks=chunks)


@app.get("/health")
def health():
    return jsonify({"status" : "ok"})


@app.post("/chat")
def chat_rag():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error" : "Please send a non-empty 'question'."}), 400

    answer, sources = answer_question(store=store, question=question)

    return jsonify({
        "answer" : answer,
        "sources" : [
            {"text" : s.page_content, "source": s.metadata.get("source")}
            for s in sources
        ]
    }), 200


if __name__ == "__main__":
    app.run(port=5000)