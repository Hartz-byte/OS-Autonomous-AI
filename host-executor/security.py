ALLOWED_ROOT = "D:\\AIML-Projects\\OS-Autonomous-AI\\workspace"

def is_safe_path(path):
    return path.startswith(ALLOWED_ROOT)
