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

IMPORTANT:
- If the user greets (Hello, Hi, Hey), DO NOT call any tool.
- If the answer can be generated from general knowledge, DO NOT use browser_search.

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
    try:
        response = requests.post(
            f"{EXECUTOR_URL}/tool/{tool_name}",
            json=payload,
            timeout=120
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def autonomous_loop(user_input):
    context = f"""
You are an autonomous AI agent.

RULES:
- Only call a tool if absolutely necessary.
- Never call the same tool twice with identical payload.
- After receiving tool results, you MUST either:
  1) Provide final answer
  OR
  2) Call a DIFFERENT tool.

User request:
{user_input}

{TOOLS}
"""

    previous_calls = set()

    for step in range(5):
        reply = ask_llm(context)
        print("LLM RAW:", reply)

        # Extract JSON safely
        try:
            start = reply.find("{")
            end = reply.rfind("}") + 1
            json_str = reply[start:end]
            decision = json.loads(json_str)
        except:
            return reply.strip()

        if "final" in decision:
            return decision["final"]

        if "tool" in decision:
            tool_name = decision["tool"]
            payload = decision["payload"]

            call_signature = f"{tool_name}:{json.dumps(payload, sort_keys=True)}"

            if call_signature in previous_calls:
                return "Stopping due to repeated identical tool calls."

            previous_calls.add(call_signature)

            print(f"Calling tool: {tool_name}")
            tool_result = call_tool(tool_name, payload)

            context += f"""
Tool used: {tool_name}
Tool result:
{tool_result}

Now analyze the result and provide final answer unless another tool is strictly required.
"""

        else:
            return reply.strip()

    return "Task stopped after max steps."

@app.post("/message")
def handle_message(req: MessageRequest):
    print("User:", req.message)
    result = autonomous_loop(req.message)
    print("Final:", result)
    return {"reply": result}
