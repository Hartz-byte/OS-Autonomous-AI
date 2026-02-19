import requests
from fastapi import FastAPI
from pydantic import BaseModel

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"

app = FastAPI()

class MessageRequest(BaseModel):
    message: str

def ask_llm(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen2:7b-instruct",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]

@app.post("/message")
def handle_message(req: MessageRequest):
    user_input = req.message
    print("User:", user_input)

    reply = ask_llm(user_input)

    print("LLM:", reply)

    return {"reply": reply}
