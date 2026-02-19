# ATHENA OS

## OpenClaw-Based Autonomous Windows AI Agent

---

## 1. SYSTEM OBJECTIVE

Athena OS is a self-hosted, WhatsApp-controlled AI agent built using:

- OpenClaw (agent brain)
- Local LLM (quantized)
- Dockerized orchestration
- Windows host-level execution daemon

It can:

- Browse internet
- Create/update/fix projects
- Open and control IDE
- Run terminal commands
- Manage files
- Verify execution results
- Operate safely with permission rules

---

## 2. FINAL ARCHITECTURE (PRODUCTION DESIGN)

```
                   ┌──────────────────────────┐
                   │       WhatsApp User      │
                   └──────────────┬───────────┘
                                  │
                                  ▼
                    ┌────────────────────────┐
                    │ WhatsApp Bridge (Node) │
                    │ (Docker Container)     │
                    └──────────────┬─────────┘
                                   │
                                   ▼
                    ┌────────────────────────┐
                    │   OpenClaw Agent Core  │
                    │ (Planner + Reasoner)   │
                    │  (Docker Container)    │
                    └──────────────┬─────────┘
                                   │ Tool Calls (HTTP)
                                   ▼
        ┌────────────────────────────────────────────────┐
        │ Windows Host Execution Daemon (Safe Agent)    │
        │  • Terminal Executor                           │
        │  • File Manager                                │
        │  • IDE Controller                              │
        │  • Browser Automation                          │
        │  • Verification Engine                         │
        └────────────────────────────────────────────────┘
```

---

## 3. WHY THIS ARCHITECTURE?

### Do NOT run OS automation inside Docker

**Because:**

- Windows GUI apps cannot be safely controlled
- Desktop automation breaks in container
- Security risks via privileged mode

### Instead:

- Docker = AI Brain only
- Windows Host = Execution Layer

This is clean, scalable, and secure.

---

## 4. CORE COMPONENTS

### 4.1 OpenClaw Agent Core (Docker)

**Purpose**

- Understand instructions
- Plan execution steps
- Choose tools
- Generate structured tool calls
- Maintain context memory

**Model Choice (Your Hardware Optimized)**

**Recommended:**

Qwen2-7B-Instruct (4-bit quantized) via llama.cpp

**Why?**

- 7B fits 4GB VRAM
- Strong instruction following
- Better coding than LLaMA 2 7B
- Works with GGUF quantization

**Alternative:**

Mistral 7B Instruct (Q4)

**Running Model**

Inside Docker:

llama.cpp server mode

OpenClaw calls local LLM endpoint:

```
http://localhost:8080/completion
```

---

## 5. TOOL-BASED ARCHITECTURE (OpenClaw)

OpenClaw will use strict tool definitions.

It NEVER executes raw commands directly.

### 5.1 Tool Definitions

**Terminal Tool**

```json
{
  "name": "run_terminal",
  "description": "Execute safe terminal commands",
  "parameters": {
    "command": "string"
  }
}
```

**Execution Rules:**

Block dangerous commands:

- format
- del /s
- shutdown
- reg delete

Only allow:

- git
- npm
- python
- node
- pip
- docker
- npx

**File Management Tool**

```json
{
  "name": "file_operation",
  "parameters": {
    "operation": "read/write/delete/list",
    "path": "string",
    "content": "string (optional)"
  }
}
```

**Restrictions:**

Allowed root directory:

```
C:\AthenaWorkspace\
```

No system directory access.

**IDE Control Tool**

Since you're on Windows:

Assume VS Code or Antigravity IDE.

```json
{
  "name": "ide_command",
  "parameters": {
    "action": "open/run/build/command_palette",
    "project_path": "string",
    "instruction": "string"
  }
}
```

**Implementation:**

Launch IDE via CLI:

```
code C:\AthenaWorkspace\project
```

Use PowerShell automation

Use AutoHotkey for UI-based commands

**Browser Tool**

Use Playwright on host.

```json
{
  "name": "browser_search",
  "parameters": {
    "query": "string"
  }
}
```

It:

- Opens Chromium headless
- Scrapes top results
- Returns structured JSON

**Project Creation Tool**

```json
{
  "name": "project_create",
  "parameters": {
    "type": "react/flask/node/python",
    "name": "string"
  }
}
```

Internally calls terminal tool.

**Verification Tool**

```json
{
  "name": "verify_project",
  "parameters": {
    "path": "string",
    "check_type": "run_tests/build/lint"
  }
}
```

AI must:

- Run tests
- Check exit code
- Parse output
- Confirm success

---

## 6. WINDOWS HOST EXECUTION DAEMON

This is critical.

A minimal Python service running on Windows.

**Responsibilities**

- Accept HTTP requests from OpenClaw
- Validate tool calls
- Execute commands safely
- Return structured results

**Technology**

- Python 3.11
- FastAPI
- subprocess (safe mode)
- Playwright
- PyAutoGUI
- AutoHotkey (optional)

**Example Execution Flow**

OpenClaw calls:

```
POST /tool/run_terminal
{
  "command": "npm install"
}
```

Daemon:

```python
subprocess.run(
  command,
  shell=True,
  cwd="C:\\AthenaWorkspace",
  timeout=120
)
```

Returns:

```json
{
  "status": "success",
  "stdout": "...",
  "stderr": ""
}
```

---

## 7. WHATSAPP CONTROL

OpenClaw does NOT natively provide WhatsApp.

So we implement:

whatsapp-web.js (Docker container)

**Flow:**

Message → Forward to OpenClaw → Receive tool plan → Execute → Reply result

---

## 8. AUTONOMOUS PROJECT WORKFLOW

**Example:**

User: Create a full-stack React + Flask project called AthenaApp

**Flow:**

OpenClaw breaks into steps:

- Create React frontend
- Create Flask backend
- Setup CORS
- Install dependencies
- Run both servers
- Verify endpoints

Calls tools sequentially

Verifies build success

Sends summary via WhatsApp

---

## 9. SECURITY MODEL

Critical for OS autonomy.

**Directory Sandbox**

All operations limited to:

```
C:\AthenaWorkspace\
```

**Command Whitelist**

Only allowed commands list.

No arbitrary execution.

**Confirmation Mode**

For:

- Delete operations
- Overwrites
- Dependency removals

AI must ask:

"Are you sure?"

**Logging**

All actions stored in:

```
C:\AthenaLogs\
```

---

## 10. BROWSING SYSTEM

Use Playwright:

- Headless Chromium
- Extract structured results
- Return JSON summary to AI

AI processes summary, not raw HTML.

---

## 11. PERFORMANCE EXPECTATION

With 7B Q4 model:

- ~10-20 tokens/sec
- Suitable for coding + planning
- Multi-step autonomy supported

Your 16GB RAM is enough.

---

## 12. DEPLOYMENT STRUCTURE

```
/athena
  /docker
  /openclaw
  /whatsapp-bridge
  /host-executor
  /workspace
```

Docker runs:

- openclaw container
- llama.cpp server
- whatsapp bridge

Host runs:

- execution daemon
