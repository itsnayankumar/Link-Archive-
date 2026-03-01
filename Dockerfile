# Use an official, lightweight Python image
FROM python:3.10-slim

# Install system dependencies (MPV and FFmpeg are great for media handling)
RUN apt-get update && apt-get install -y \
    mpv \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to cache the pip installs
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project files into the container
COPY . .

# The command that runs when the container starts
CMD ["python", "main.py"]
