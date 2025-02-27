# health_check_api.py
from fastapi import FastAPI
from datetime import datetime
from rabbit.rabbit_class import RabbitMQ
import json
import subprocess
import os
app = FastAPI()

last_consumption_time = None

subscriber_pid_file = "subscriber_pid.txt"

@app.get("/health")
async def check_health():
    global last_consumption_time
    current_time = datetime.now()
    
    if last_consumption_time is None or (current_time - last_consumption_time).total_seconds() > 120:
        return {"status": "unhealthy", "reason": "No recent message consumption"}
    
    try:
        rabbit_connection = RabbitMQ()
        rabbit_connection.connect()
        rabbit_connection.disconnect()
    except Exception as e:
        return {"status": "unhealthy", "reason": f"Failed to connect to RabbitMQ: {str(e)}"}
    
    return {"status": "healthy"}

def update_last_consumption_time():
    global last_consumption_time
    last_consumption_time = datetime.now()
    
def is_process_running(pid):
    try:
        # Execute ps command and check if it returns anything
        output = os.popen(f"ps -p {pid}").read()
        return len(output) > 0
    except Exception as e:
        print(f"Error: {e}")
        return False
    
@app.get("/process_status")
async def check_health():
    status = 0
    with open('subscriber_pid.txt', 'r') as file:
        first_line = file.readline()
        first_line = first_line.strip()
        if is_process_running(first_line):
            status = 1
        else:
            status = 0
    return {"status": status,"pid":first_line}

@app.get("/restart")
async def restart():
    try:
        # Run the script in the background without capturing output
        subprocess.Popen(["./restart_subscriber.sh"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        status = 1  # Script started successfully
    except Exception as e:
        print(f"Error starting script: {e}")
        status = 0

    return {"status": status}