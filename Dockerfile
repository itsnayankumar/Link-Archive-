FROM python:3.10-slim

# Force Python outputs to Render logs instantly
ENV PYTHONUNBUFFERED=1

# Install mpv and ffmpeg just in case you need them later
RUN apt-get update && apt-get install -y mpv ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Expose the port Render expects
EXPOSE 10000

CMD ["python", "main.py"]
