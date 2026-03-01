FROM python:3.10-slim

# Install mpv
RUN apt-get update && apt-get install -y mpv && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "main.py"]
