import requests
import json
import re
from fastapi import FastAPI
from pydantic import BaseModel

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
EXECUTOR_URL = "http://executor:8000"

app = FastAPI()


class MessageRequest(BaseModel):
    message: str


# PROMPT
TOOLS = """
You are an autonomous AI agent.

STRICT RULES:
- Respond with ONLY valid JSON.
- Never include text outside JSON.
- Never return both "tool" and "final" together.
- Do NOT rewrite, modify, simplify, or correct file paths.
- Always use the EXACT path provided by the user.
- If greeting (Hi, Hello, Hey) → respond with final.
- If general knowledge → respond with final.
- Only call tool if real execution is required.

TOOL PRIORITY (IMPORTANT):
1. windows_gui → GUI actions (open apps, open files on system, typing, browser)
2. file_operation → read/write/delete/list/copy/move files
3. cli_command → Linux container terminal
4. browser_search → internet

Available tools:

1. browser_search
   payload: {"query": "search term"}

2. file_operation
   payload: {
       "operation": "read | write | delete | list | copy | move",
       "path": "source path (absolute)",
       "destination": "target path (absolute, required for copy/move)",
       "content": "text content (optional for write)"
   }

3. cli_command
   payload: {"command": "terminal command"}

4. windows_gui
   payload: {
       "action": "open_notepad | type_text | open_file | open_folder | open_recycle_bin",
       "text": "text to type (optional)",
       "path": "absolute path to file or folder (required for open_file/open_folder)"
   }

TO CALL A TOOL:
{
  "tool": "tool_name",
  "payload": { ... }
}

TO FINISH:
{
  "final": "your answer"
}

Do NOT return final unless task is fully complete.
"""


# INTENT CLASSIFIER
def classify_intent(user_input: str):
    text = user_input.lower().strip()

    if text in ["hi", "hello", "hey"]:
        return "greeting"

    return "llm"


# LLM CALL
def ask_llm(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "qwen2:7b-instruct",
                "prompt": prompt,
                "stream": False
            },
            timeout=300
        )

        data = response.json()

        if "response" in data:
            return data["response"]

        if "error" in data:
            return f'{{"final": "LLM error: {data["error"]}"}}'

        return '{"final": "Unexpected LLM response format."}'

    except Exception as e:
        return f'{{"final": "LLM connection error: {str(e)}"}}'


# JSON EXTRACTION
def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        return json.loads(match.group())
    except:
        return None


# TOOL CALL
def call_tool(tool_name, payload):
    try:
        response = requests.post(
            f"{EXECUTOR_URL}/tool/{tool_name}",
            json=payload,
            timeout=180
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


# AUTONOMOUS LOOP
def autonomous_loop(user_input):

    intent = classify_intent(user_input)

    # GREETING
    if intent == "greeting":
        return "Hello!"

    # LLM HANDLED TASKS
    context = f"""
User request:
{user_input}

{TOOLS}
"""

    previous_calls = set()

    for step in range(8):

        reply = ask_llm(context)
        decision = extract_json(reply)

        if not decision:
            return reply.strip()

        # FINAL
        if "final" in decision:
            return decision["final"]

        # TOOL
        if "tool" in decision:
            tool_name = decision["tool"]
            payload = decision["payload"]

            call_signature = f"{tool_name}:{json.dumps(payload, sort_keys=True)}"

            if call_signature in previous_calls:
                return "Stopped due to repeated identical tool call."

            previous_calls.add(call_signature)

            tool_result = call_tool(tool_name, payload)

            context += f"""
Tool used: {tool_name}
Result:
{json.dumps(tool_result, indent=2)}

If more steps are needed, call another tool.
If task is complete, return final.
Respond ONLY in JSON.
"""

        else:
            return reply.strip()

    return "Task stopped after max steps."


# FASTAPI
@app.post("/message")
def handle_message(req: MessageRequest):
    result = autonomous_loop(req.message)
    return {"reply": result}
