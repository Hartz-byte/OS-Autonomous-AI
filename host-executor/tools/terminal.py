import subprocess
import shlex

ALLOWED_COMMANDS = ["git", "npm", "node", "python", "pip", "npx"]

WORKSPACE = r"D:\AIML-Projects\OS-Autonomous-AI\workspace"

def run_terminal(payload):
    command = payload.get("command")

    if not command:
        return {"error": "No command provided"}
    
    if len(command) > 200:
        return {"error": "Command too long"}

    parsed = shlex.split(command)

    if parsed[0] not in ALLOWED_COMMANDS:
        return {"error": "Command not allowed"}

    try:
        result = subprocess.run(
            parsed,
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=120
        )

        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except Exception as e:
        return {"error": str(e)}
