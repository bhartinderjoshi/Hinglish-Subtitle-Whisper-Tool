# Dockerfile for Hugging Face Spaces
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Create necessary directories
RUN mkdir -p /app/templates

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# Run the application
CMD ["python", "web_server.py", "--host", "0.0.0.0", "--port", "7860"]
