const API_URL = "http://localhost:5000/chat";

const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("question");
const sendBtn = document.getElementById("send");
const newChatBtn = document.getElementById("new-chat");

function getThreadId() {
  let id = localStorage.getItem("thread_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("thread_id", id);
  }
  return id;
}

function addMessage(text, role) {
  const div = document.createElement("div");
  div.className = "msg " + role;
  div.textContent = text; // textContent is safe: it never runs HTML
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

function setLoading(isLoading) {
  sendBtn.disabled = isLoading;
  inputEl.disabled = isLoading;
}

function greet() {
  addMessage("Hi! Ask me about GreenTech's products, warranty, returns or shipping.", "bot");
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = inputEl.value.trim();
  if (!question) return;

  addMessage(question, "user");
  inputEl.value = "";
  setLoading(true);
  const reply = addMessage("Thinking...", "bot");

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question, thread_id: getThreadId() }),
    });
    const data = await response.json();
    reply.textContent = response.ok ? data.answer : (data.error || "Something went wrong.");
  } catch (error) {
    reply.textContent = "Cannot reach the server. Is Flask running?";
  } finally {
    setLoading(false);
    inputEl.focus();
  }
});

newChatBtn.addEventListener("click", () => {
  localStorage.removeItem("thread_id"); // next message gets a fresh thread_id
  messagesEl.innerHTML = "";            // safe here: we are only clearing
  greet();
});

greet();

 