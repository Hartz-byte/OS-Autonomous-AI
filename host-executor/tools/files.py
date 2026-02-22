import os
import shutil
from logger import log

def file_operation(operation, path, content=None, destination=None):
    try:
        if not operation or not path:
            return {"error": "Missing operation or path"}

        # Helper to normalize individual paths
        def fix_path(p):
            if not p: return p
            p = p.replace("\\", "/")
            if p.startswith("C:"):
                p = p.replace("C:", "/mnt/c")
            if p.startswith("D:"):
                p = p.replace("D:", "/mnt/d")
            return p

        path = fix_path(path)
        destination = fix_path(destination)

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
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            log(f"File/Dir deleted: {path}")
            return {"status": f"Deleted {path}"}

        elif operation == "list":
            files = os.listdir(path)
            log(f"Directory listed: {path}")
            return {"files": files}

        elif operation == "copy":
            if not destination:
                return {"error": "Missing destination for copy"}
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            if os.path.isdir(path):
                shutil.copytree(path, destination, dirs_exist_ok=True)
            else:
                shutil.copy2(path, destination)
            log(f"Copied {path} to {destination}")
            return {"status": f"Copied {path} to {destination}"}

        elif operation == "move":
            if not destination:
                return {"error": "Missing destination for move"}
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.move(path, destination)
            log(f"Moved {path} to {destination}")
            return {"status": f"Moved {path} to {destination}"}

        else:
            return {"error": "Invalid operation"}

    except Exception as e:
        log(f"file_operation ERROR: {str(e)}")
        return {"error": str(e)}
