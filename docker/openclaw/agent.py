import requests
import json
from fastapi import FastAPI
from pydantic import BaseModel

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
EXECUTOR_URL = "http://executor:8000"

app = FastAPI()

class MessageRequest(BaseModel):
    message: str

TOOLS = """
You have access to the following tools:

1. browser_search
   payload: {"query": "search term"}

2. file_operation
   payload: {
       "operation": "read | write | delete | list",
       "path": "absolute path inside workspace",
       "content": "optional"
   }

3. run_terminal
   payload: {"command": "allowed command"}

To use a tool, respond ONLY in this JSON format:

{
  "tool": "tool_name",
  "payload": { ... }
}

If no tool is needed, respond with:
{
  "final": "your answer"
}
"""

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

def call_tool(tool_name, payload):
    response = requests.post(
        f"{EXECUTOR_URL}/tool/{tool_name}",
        json=payload
    )
    return response.json()

def autonomous_loop(user_input):
    context = f"""
You are an autonomous AI agent.
Decide step by step how to complete the user's request.

User request:
{user_input}

{TOOLS}
"""

    for _ in range(5):  # max 5 tool iterations
        reply = ask_llm(context)
        print("LLM RAW:", reply)

        try:
            decision = json.loads(reply)
        except:
            return reply

        if "final" in decision:
            return decision["final"]

        if "tool" in decision:
            tool_name = decision["tool"]
            payload = decision["payload"]

            print(f"Calling tool: {tool_name}")
            tool_result = call_tool(tool_name, payload)

            context += f"\nTool result:\n{tool_result}\n"

        else:
            return reply

    return "Task stopped after max steps."

@app.post("/message")
def handle_message(req: MessageRequest):
    print("User:", req.message)
    result = autonomous_loop(req.message)
    print("Final:", result)
    return {"reply": result}
