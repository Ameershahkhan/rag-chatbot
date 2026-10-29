const API_URL = "http://localhost:5000/chat";

// Edit these to match the PDFs you loaded.
const SUGGESTIONS = [
  "What is a checkpointer?",
  "How does chunk overlap work?",
  "Why do we use embeddings?",
];

const threadEl = document.getElementById("thread");
const emptyEl = document.getElementById("empty");
const suggestionsEl = document.getElementById("suggestions");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("question");
const sendBtn = document.getElementById("send");
const newChatBtn = document.getElementById("new-chat");

let busy = false;

function getThreadId() {
  let id = localStorage.getItem("thread_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("thread_id", id);
  }
  return id;
}

function scrollToEnd() {
  threadEl.scrollTop = threadEl.scrollHeight;
}

function setBusy(isBusy) {
  busy = isBusy;
  sendBtn.disabled = isBusy;
  inputEl.disabled = isBusy;
}

// Turns "(file.pdf, p. 3)" in an answer into a highlighted chip.
// Everything is added as text nodes, so the answer can never run HTML.
const CITATION = /\(([^()]*\.pdf[^()]*)\)/gi;

function renderAnswer(el, text) {
  el.className = "a";
  el.replaceChildren();
  let last = 0;
  for (const match of text.matchAll(CITATION)) {
    if (match.index > last) el.append(text.slice(last, match.index));
    const chip = document.createElement("span");
    chip.className = "cite";
    chip.textContent = match[1].trim();
    el.append(chip);
    last = match.index + match[0].length;
  }
  if (last < text.length) el.append(text.slice(last));
}

function showWaiting(el) {
  el.className = "a waiting";
  const dots = document.createElement("span");
  dots.className = "dots";
  for (let i = 0; i < 3; i++) dots.append(document.createElement("span"));
  el.replaceChildren(dots, "Searching your documents");
}

function showError(el, message) {
  el.className = "a error";
  el.textContent = message;
}

function addTurn(question) {
  const turn = document.createElement("article");
  turn.className = "turn";

  const q = document.createElement("p");
  q.className = "q";
  q.textContent = question;

  const a = document.createElement("p");
  showWaiting(a);

  turn.append(q, a);
  threadEl.append(turn);
  scrollToEnd();
  return a;
}

async function ask(question) {
  question = question.trim();
  if (!question || busy) return;

  emptyEl.hidden = true;
  const answerEl = addTurn(question);
  inputEl.value = "";
  setBusy(true);

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question, thread_id: getThreadId() }),
    });
    const data = await response.json().catch(() => ({}));
    if (response.ok) {
      renderAnswer(answerEl, data.answer);
    } else {
      showError(answerEl, data.error || "The server returned an error. Check the Flask terminal for details.");
    }
  } catch (error) {
    showError(answerEl, "Can't reach the server. Start it with python app.py, then ask again.");
  } finally {
    setBusy(false);
    scrollToEnd();
    inputEl.focus();
  }
}

formEl.addEventListener("submit", (event) => {
  event.preventDefault();
  ask(inputEl.value);
});

newChatBtn.addEventListener("click", () => {
  localStorage.removeItem("thread_id"); // the next message starts a fresh memory
  threadEl.querySelectorAll(".turn").forEach((turn) => turn.remove());
  emptyEl.hidden = false;
  inputEl.focus();
});

for (const text of SUGGESTIONS) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "suggestion";
  button.textContent = text;
  button.addEventListener("click", () => ask(text));
  suggestionsEl.append(button);
}