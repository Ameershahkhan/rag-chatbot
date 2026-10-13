from dotenv import load_dotenv
load_dotenv()
from langchain.chat_models import init_chat_model


model = init_chat_model("groq:openai/gpt-oss-20b")

reply = model.invoke("Write two lines about lahore.")

print(reply.content)
print("---")
print(model.invoke("What is the current weather of lahore?").content)