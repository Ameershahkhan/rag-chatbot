from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_core import load_chunks, build_vector_store, answer_question, make_agent, ask_agent
import uuid

app = Flask(__name__)
CORS(app)


# Built ONCE when the server starts, not on every request
chunks = load_chunks()
store = build_vector_store(chunks=chunks)
agent = make_agent(store)



@app.get("/health")
def health():
    return jsonify({"status" : "ok"})


@app.post("/chat")
def chat_rag():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    thread_id = (data.get("thread_id") or "").strip() or str(uuid.uuid4())


    if not question:
        return jsonify({"error" : "Please send a non-empty 'question'."}), 400

    try:
        answer = ask_agent(agent, question, thread_id)
    except Exception:
        app.logger.exception("Agent Error")
        return jsonify({"error" : "Something Went Wrong"}), 500

    
    return jsonify({
        "answer" : answer,
        "thread_id" : thread_id
    }), 200


if __name__ == "__main__":
    app.run(port=5000)