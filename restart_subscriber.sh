#!/bin/bash

# Activate the virtual environment
echo "Activating virtual environment..."
source myenv/bin/activate

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
