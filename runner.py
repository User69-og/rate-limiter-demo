import subprocess
import time
import sys
import os

print("==========================================")
print("Starting Rate Limiting Test Suite...")
print("==========================================")

# 1. Start the FastAPI Server in the background
print("[1/4] Booting up FastAPI Server...")
server_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "server:app", "--port", "8000"],
    stdout=subprocess.DEVNULL,  # Hides server logs to keep console clean
    stderr=subprocess.DEVNULL
)

# Give it 3 seconds to fully initialize
time.sleep(3)

try:
    # 2. Run the Load Generator
    print("[2/4] Executing Asynchronous Load Test (takes ~6 seconds)...")
    client_result = subprocess.run([sys.executable, "client.py"])
    
    if client_result.returncode != 0:
        print("Error: Client script failed.")
        sys.exit(1)

    # 3. Generate the Dashboard
    print("[3/4] Generating Analytics Dashboard...")
    plot_result = subprocess.run([sys.executable, "plot.py"])

    if plot_result.returncode != 0:
        print("Error: Plot script failed.")
        sys.exit(1)

finally:
    # 4. GUARANTEED CLEANUP (No more zombie processes!)
    print("[4/4] Shutting down Server safely...")
    server_process.terminate()
    server_process.wait()
    print("==========================================")
    print("SUCCESS! Open 'rate_limit_dashboard.png' to see your results.")
    print("==========================================")