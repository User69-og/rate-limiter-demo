import subprocess
import time

print("==========================================")
print("Launching Presentation in 3 Windows...")
print("==========================================")

NEW_WINDOW = subprocess.CREATE_NEW_CONSOLE

# We set the directory here so we don't have to use 'cd' in the command prompt
PROJECT_DIR = r"E:\Projects\Rate Limiting"

# Point directly to the virtual environment's Python executable
VENV_PYTHON = r"venv\Scripts\python.exe"

# 1. Open Window 1: The Server
print("[1/3] Popping open Server window...")
server_cmd = f"title FastAPI Server && color 0A && {VENV_PYTHON} -m uvicorn server:app"
subprocess.Popen(['cmd', '/k', server_cmd], cwd=PROJECT_DIR, creationflags=NEW_WINDOW)

# Wait 3 seconds for the server to boot up
time.sleep(3)

# 2. Open Window 2: The Load Test
print("[2/3] Popping open Client window...")
client_cmd = f"title Load Generator && color 0C && {VENV_PYTHON} client.py"
subprocess.Popen(['cmd', '/k', client_cmd], cwd=PROJECT_DIR, creationflags=NEW_WINDOW)

# Wait 10 seconds for the client to finish
time.sleep(10)

# 3. Open Window 3: The Dashboard Generator
print("[3/3] Popping open Visualizer window...")
plot_cmd = f"title Dashboard Generator && color 0B && {VENV_PYTHON} plot.py"
subprocess.Popen(['cmd', '/k', plot_cmd], cwd=PROJECT_DIR, creationflags=NEW_WINDOW)

print("==========================================")
print("All windows launched! You can close this main terminal now.")
print("==========================================")