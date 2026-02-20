import datetime
import os

LOG_DIR = "logs"
LOG_PATH = os.path.join(LOG_DIR, "executor.log")

os.makedirs(LOG_DIR, exist_ok=True)

def log(entry):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} - {entry}\n")
