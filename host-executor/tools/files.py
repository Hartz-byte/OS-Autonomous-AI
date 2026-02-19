import os

ALLOWED_ROOT = r"D:\AIML-Projects\OS-Autonomous-AI\workspace"

def is_safe_path(path):
    abs_path = os.path.abspath(path)
    return abs_path.startswith(ALLOWED_ROOT)

def file_operation(payload):
    operation = payload.get("operation")
    path = payload.get("path")
    content = payload.get("content", "")

    if not is_safe_path(path):
        return {"error": "Access denied. Path outside workspace."}

    try:
        if operation == "read":
            with open(path, "r", encoding="utf-8") as f:
                return {"content": f.read()}

        elif operation == "write":
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"status": "written"}

        elif operation == "delete":
            os.remove(path)
            return {"status": "deleted"}

        elif operation == "list":
            return {"files": os.listdir(path)}

        else:
            return {"error": "Invalid operation"}

    except Exception as e:
        return {"error": str(e)}
