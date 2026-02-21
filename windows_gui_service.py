from fastapi import FastAPI
import pyautogui
import subprocess
import time

app = FastAPI()


@app.post("/gui_action")
def gui_action(payload: dict):

    action = payload.get("action")

    if action == "open_notepad":
        subprocess.Popen("notepad")
        time.sleep(1)
        return {"status": "Notepad opened"}

    elif action == "type_text":
        text = payload.get("text", "")
        pyautogui.write(text, interval=0.05)
        return {"status": "Text typed"}

    elif action == "press_key":
        key = payload.get("key")
        pyautogui.press(key)
        return {"status": f"Pressed {key}"}

    elif action == "click":
        x = payload.get("x")
        y = payload.get("y")
        pyautogui.click(x=int(x), y=int(y))
        return {"status": "Clicked"}

    return {"error": "Invalid action"}
