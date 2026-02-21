import os
from logger import log

def file_operation(operation, path, content=None):
    try:
        if not operation or not path:
            return {"error": "Missing operation or path"}

        # Convert Windows paths if needed
        path = path.replace("\\", "/")

        # Auto convert Windows paths
        if path.startswith("C:"):
            path = path.replace("C:", "/mnt/c")

        if path.startswith("D:"):
            path = path.replace("D:", "/mnt/d")

        path = path.replace("\\", "/")

        if operation == "write":
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content or "")
            log(f"File written: {path}")
            return {"status": f"File written to {path}"}

        elif operation == "read":
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
            log(f"File read: {path}")
            return {"content": data}

        elif operation == "delete":
            os.remove(path)
            log(f"File deleted: {path}")
            return {"status": f"Deleted {path}"}

        elif operation == "list":
            files = os.listdir(path)
            log(f"Directory listed: {path}")
            return {"files": files}

        else:
            return {"error": "Invalid operation"}

    except Exception as e:
        log(f"file_operation ERROR: {str(e)}")
        return {"error": str(e)}
