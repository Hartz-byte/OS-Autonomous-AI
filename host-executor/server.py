from fastapi import FastAPI
from tools.terminal import run_terminal
from tools.files import file_operation
from tools.browser import browser_search

app = FastAPI()

@app.post("/tool/run_terminal")
def terminal(payload: dict):
    return run_terminal(payload)

@app.post("/tool/file_operation")
def file_ops(payload: dict):
    return file_operation(payload)

@app.post("/tool/browser_search")
def browser(payload: dict):
    return browser_search(payload)