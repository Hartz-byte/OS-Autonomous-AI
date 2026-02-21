from fastapi import FastAPI
from tools.terminal import run_terminal
from tools.files import file_operation
from tools.browser import browser_search
from logger import log

app = FastAPI()

@app.post("/tool/run_terminal")
def terminal(payload: dict):
    log(f"run_terminal called: {payload}")
    return run_terminal(payload.get("command"))

@app.post("/tool/file_operation")
def file_ops(payload: dict):
    log(f"file_operation called: {payload}")
    return file_operation(
        operation=payload.get("operation"),
        path=payload.get("path"),
        content=payload.get("content")
    )

@app.post("/tool/browser_search")
def browser(payload: dict):
    log(f"browser_search called: {payload}")
    return browser_search(payload)
