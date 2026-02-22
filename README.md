# OS Autonomous AI

OS Autonomous AI is a self-hosted, WhatsApp-controlled autonomous agent system designed to bridge high-level natural language instructions with low-level Windows OS automation. It allows you to control your PC remotely through a chat interface, performing tasks ranging from file management to GUI interaction and web research.

## Architecture

The system follows a triple-layer architecture to ensure security, path synchronization, and full OS access.

1.  Agent Core (Brain): A Dockerized Python service that runs the autonomous loop. It uses a local LLM to plan, reason, and execute tool calls.
2.  Executor Bridge (Bridge): A translation layer that manages communication between the Linux-based Docker environment and the Windows Host. It handles path normalization (e.g., converting /mnt/d/ to D:\) to ensure the AI understands the file system across different environments.
3.  Windows GUI Service (Body): A native Windows daemon that performs physical actions like typing, clicking, and launching applications that cannot be executed from within a container.

## Features

- WhatsApp Interface: Control your computer via WhatsApp messages from any device.
- GUI Automation: Open applications, type text, click coordinates, and manage system folders like the Recycle Bin.
- Advanced File Operations: Support for reading, writing, copying, moving, and listing files across all connected drives.
- Autonomous Problem Solving: Uses a ReAct loop to observe tool outputs and iterate until a task is completed.
- Web Intelligence: Integrated Google Search capabilities to fetch real-time information and organic search results.
- Path Normalization: Seamlessly handles Windows and Linux pathing issues between the host and Docker containers.

## System Requirements

This project is optimized for performance on consumer-grade hardware.

- CPU: 4+ Cores (Modern i5/i7 or Ryzen 5/7).
- RAM: 16GB Minimum.
- GPU: 4GB VRAM Minimum (Required for local LLM acceleration).
- Storage: 20GB free space for Docker images and the local model.
- OS: Windows 10/11 with WSL2 and Docker Desktop installed.

## Model Setup

The system uses Qwen2-7B-Instruct as its primary reasoning engine.

1.  Install Ollama from https://ollama.ai/.
2.  Download the model by running the following command in your terminal:
    ```bash
    ollama pull qwen2:7b-instruct
    ```
3.  Ensure Ollama is running in the background before starting the project services.

## Setup and Installation

1.  Configure Environment: Create a .env file in the root directory with your API keys:
    ```env
    SERP_API_KEY=your_serp_api_key_here
    ```

2.  Install Host Dependencies:
    Navigate to the host-executor folder and install the required Python packages:
    ```bash
    cd host-executor
    pip install -r requirements.txt
    ```

## Running the Project

The system requires two separate terminals to be running simultaneously.

Terminal 1: Windows Host Daemon
Launch the GUI service from the root directory. Ensure your virtual environment is activated if applicable.
```bash
uvicorn windows_gui_service:app --host 0.0.0.0 --port 9000
```

Terminal 2: Docker Orchestration
Navigate to the docker directory and start the core services.
```bash
cd docker
docker-compose up --build
```

After starting, check the whatsapp-bridge container logs to scan the QR code for WhatsApp authentication.

## Integrated Tools

- windows_gui: Handles opening files, folders, notepad, and typing text.
- file_operation: Manages read, write, copy, move, and delete actions.
- browser_search: Retrieves organic search results and information from the web.
- cli_command: Executes terminal commands within the Docker environment.

## Future Roadmap

- Full OS Autonomy: Expanding capabilities to automate every installed application.
- Multi-Tasking: Enhancing the reasoning loop to handle and track multiple complex tasks in a single session.
- Production-Grade Coding: Deep integration with IDEs to write, debug, and fix project code autonomously.
- PC-Wide Automation: Transitioning from specific tool-based actions to a generalized "human-on-the-loop" OS controller.
- Dynamic Model Switching: Automatically switching between lightweight models for routing and larger models for complex logic.

License: This project is for educational and personal use. Use with caution as it allows an AI direct access to your operating system.
