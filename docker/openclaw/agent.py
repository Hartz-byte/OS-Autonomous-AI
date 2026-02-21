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


TOOLS = """
You are an autonomous AI agent.

STRICT RULES:
- You MUST respond with ONLY valid JSON.
- Never include text outside JSON.
- Never return both "tool" and "final" together.
- If greeting (Hi, Hello, Hey) → respond with final.
- If general knowledge → respond with final.
- Only call tool if real-time or external data is required.

Available tools:

1. browser_search
   payload: {"query": "search term"}

2. file_operation
   payload: {
       "operation": "read | write | delete | list",
       "path": "absolute path inside workspace",
       "content": "optional"
   }

3. cli_command
   payload: {
       "command": "terminal command"
   }

Use cli_command for ANY terminal execution.

When calling cli_command, always use:

{
  "tool": "cli_command",
  "payload": {
    "command": "node -v"
  }
}


TO CALL A TOOL:
{
  "tool": "tool_name",
  "payload": { ... }
}

TO ANSWER DIRECTLY:
{
  "final": "your answer"
}

DO NOT respond with "final" unless the task is completed.

If writing a file on Windows C drive, use:
"/mnt/c/Users/etern/Desktop/filename.txt"

Never assume a username. Always use "etern".
"""


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

        # Debug logging
        print("OLLAMA RAW RESPONSE:", data)

        if "response" in data:
            return data["response"]

        if "error" in data:
            return f'{{"final": "LLM error: {data["error"]}"}}'

        return '{"final": "Unexpected LLM response format."}'

    except Exception as e:
        return f'{{"final": "LLM connection error: {str(e)}"}}'


# SAFE JSON EXTRACTION
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


# FORMAT SEARCH RESULTS CLEANLY
def format_search_results(results):
    if not results:
        return "No relevant results were found."

    formatted = "Here are the latest results:\n\n"

    for i, item in enumerate(results, 1):
        formatted += f"{i}. {item}\n\n"

    return formatted.strip()


# AUTONOMOUS LOOP
def autonomous_loop(user_input):
    context = f"""
User request:
{user_input}

{TOOLS}
"""

    previous_calls = set()

    for step in range(5):
        reply = ask_llm(context)
        print("LLM RAW:", reply)

        decision = extract_json(reply)

        if not decision:
            return reply.strip()

        # FINAL ANSWER
        if "final" in decision:
            return decision["final"]

        # TOOL CALL
        if "tool" in decision:
            tool_name = decision["tool"]
            payload = decision["payload"]

            call_signature = f"{tool_name}:{json.dumps(payload, sort_keys=True)}"

            if call_signature in previous_calls:
                return "Stopped due to repeated identical tool call."

            previous_calls.add(call_signature)

            print(f"Calling tool: {tool_name}")
            tool_result = call_tool(tool_name, payload)
            print("TOOL RESULT:", tool_result)

            # Special formatting for search results
            if tool_name == "browser_search":
                results = tool_result.get("results", [])
                formatted = format_search_results(results)

                context += f"""
Tool used: {tool_name}
Raw result:
{json.dumps(tool_result, indent=2)}

Now provide final answer ONLY in JSON:

{{
  "final": "{formatted}"
}}
"""
            else:
                context += f"""
Tool used: {tool_name}
Result:
{json.dumps(tool_result, indent=2)}

Now respond ONLY with:

{{
  "final": "your summarized answer"
}}
"""

        else:
            return reply.strip()

    return "Task stopped after max steps."


# FASTAPI ENDPOINT
@app.post("/message")
def handle_message(req: MessageRequest):
    print("User:", req.message)

    result = autonomous_loop(req.message)

    print("Final:", result)

    # Always return clean text to WhatsApp
    return {"reply": result}
