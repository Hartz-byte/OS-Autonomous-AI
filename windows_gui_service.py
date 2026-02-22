from fastapi import FastAPI
import pyautogui
import subprocess
import time
import os

app = FastAPI()


@app.post("/gui_action")
def gui_action(payload: dict):
    action = payload.get("action")
    path = payload.get("path")
    print(f"Received GUI action: {action}, path: {path}")

    if action == "open_notepad":
        subprocess.Popen("notepad")
        time.sleep(1.5)  # Increased delay for focus
        return {"status": "Notepad opened"}

    elif action == "type_text":
        text = payload.get("text", "")
        pyautogui.write(text, interval=0.1)  # Slower typing for reliability
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
    
    elif action == "open_file":
        # Use os.startfile for better Windows integration
        try:
            os.startfile(path)
            return {"status": f"Opened file {path}"}
        except Exception as e:
            # Fallback to explorer
            subprocess.Popen(f'explorer "{path}"')
            return {"status": f"Opened {path} via explorer", "error": str(e)}

    elif action == "open_folder":
        # os.startfile also works for directories
        try:
            os.startfile(path)
            return {"status": f"Opened folder {path}"}
        except Exception as e:
            subprocess.Popen(f'explorer "{path}"')
            return {"status": f"Opened folder {path} via explorer", "error": str(e)}

    elif action == "open_recycle_bin":
        subprocess.Popen("explorer shell:RecycleBinFolder")
        return {"status": "Recycle Bin opened"}

    return {"error": f"Invalid action: {action}"}
