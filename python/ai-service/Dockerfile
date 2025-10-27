FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install whisper.cpp
WORKDIR /tmp
RUN git clone https://github.com/ggerganov/whisper.cpp.git && \
    cd whisper.cpp && \
    make && \
    cp main /usr/local/bin/whisper && \
    cd .. && \
    rm -rf whisper.cpp

# Create models directory and download base model
RUN mkdir -p /app/models
WORKDIR /app/models
RUN wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app
COPY main.py .

# Create directory for temporary files
RUN mkdir -p /tmp/audio_uploads

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV WHISPER_MODEL_PATH=/app/models/ggml-base.en.bin

# Run the application
CMD ["python", "main.py"]
