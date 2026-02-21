import os
import re
from fastapi import FastAPI
from tools.terminal import run_terminal
from tools.files import file_operation
from tools.browser import browser_search
import subprocess
import requests
from logger import log

app = FastAPI()

def normalize_path(path: str):
    path = path.replace("\\", "/")

    # Convert D:/ or D:\ to /mnt/d/
    if re.match(r"^[A-Za-z]:", path):
        drive = path[0].lower()
        path = f"/mnt/{drive}" + path[2:]

    # Convert /D/... to /mnt/d/...
    if re.match(r"^/[A-Za-z]/", path):
        drive = path[1].lower()
        path = f"/mnt/{drive}/{path[3:]}"

    return path

@app.post("/tool/run_terminal")
def terminal(payload: dict):
    log(f"run_terminal called: {payload}")
    return run_terminal(payload.get("command"))

@app.post("/tool/file_operation")
def file_ops(payload: dict):
    log(f"file_operation called: {payload}")
    return file_operation(
        operation=payload.get("operation"),
        path=normalize_path(payload.get("path")),
        content=payload.get("content")
    )

@app.post("/tool/browser_search")
def browser(payload: dict):
    log(f"browser_search called: {payload}")
    return browser_search(payload)

@app.post("/tool/cli_command")
def cli_command(payload: dict):
    try:
        result = subprocess.run(
            payload["command"],
            shell=True,
            capture_output=True,
            text=True
        )

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }

    except Exception as e:
        return {"error": str(e)}

@app.post("/tool/windows_gui")
def windows_gui(payload: dict):
    try:
        response = requests.post(
            "http://host.docker.internal:9000/gui_action",
            json=payload,
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}
