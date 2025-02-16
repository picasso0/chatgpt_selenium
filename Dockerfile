# Use the official Python image as a base
FROM python:3.10

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
    RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
    RUN apt-get -y update
    RUN apt-get install -y chromium
    
    # install chromedriver
    RUN apt-get install -yqq unzip
    RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
    RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/


# Set environment variables
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Command to run the application
CMD ["uvicorn","main:app","--host","0.0.0.0","--port", "8000","--reload"]
# CMD ["python", "-u", "app.py"]
