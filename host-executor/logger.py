import datetime

LOG_PATH = r"D:\AIML-Projects\OS-Autonomous-AI\logs\executor.log"

def log(entry):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} - {entry}\n")
