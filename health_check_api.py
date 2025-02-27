# health_check_api.py
from fastapi import FastAPI
from datetime import datetime
from rabbit.rabbit_class import RabbitMQ
import json

app = FastAPI()

last_consumption_time = None

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
