#!/bin/bash

# Check if Python 3.11 is installed
if ! python3.11 --version; then
    echo "Python 3.11 is not installed. Installing..."
    
    # Install Python 3.11 (example for Ubuntu/Debian-based systems)
    sudo apt update
    sudo apt install software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install python3.11
    
    # Ensure Python 3.11 is now available
    if ! python3.11 --version; then
        echo "Failed to install Python 3.11."
        exit 1
    fi
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "myenv" ]; then
    echo "Creating virtual environment..."
    python3.11 -m venv myenv
else
    echo "Virtual environment 'myenv' already exists. Skipping creation."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source myenv/bin/activate

# Install packages from requirements.txt
echo "Installing packages from requirements.txt..."
pip install -r requirements.txt


# Kill any existing python subscriber.py processes
echo "Killing any existing subscriber.py processes..."
pkill -f "python subscriber.py"

# Run subscriber.py and store its PID
echo "Running subscriber.py..."
python subscriber.py &
SUBSCRIBER_PID=$!

# Optionally, you can save the PID to a file for later use
echo "Subscriber PID: $SUBSCRIBER_PID"
echo "$SUBSCRIBER_PID" > subscriber_pid.txt

chmod +x restart_subscriber.sh
# Run Uvicorn FastAPI server
echo "Running Uvicorn FastAPI server..."
uvicorn health_check_api:app --host 0.0.0.0 --port 8000 --forwarded-allow-ips '*'
