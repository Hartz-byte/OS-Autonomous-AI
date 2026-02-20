import os

def file_operation(operation, path, content=None):
    try:
        if operation == "write":
            with open(path, "w", encoding="utf-8") as f:
                f.write(content or "")
            return {"status": f"File written to {path}"}

        elif operation == "read":
            with open(path, "r", encoding="utf-8") as f:
                return {"content": f.read()}

        elif operation == "delete":
            os.remove(path)
            return {"status": f"Deleted {path}"}

        elif operation == "list":
            return {"files": os.listdir(path)}

        else:
            return {"error": "Invalid operation"}

    except Exception as e:
        return {"error": str(e)}
