# Simple Dockerfile for AudioAnalyzer with visualization
FROM python:3.10-slim

# Install only necessary system dependencies
RUN apt-get update && apt-get install -y \
    # Audio processing
    ffmpeg \
    libsndfile1-dev \
    libasound2-dev \
    # Build tools
    gcc \
    g++ \
    pkg-config \
    # Qt dependencies (for your existing UI)
    libqt5gui5 \
    libqt5core5a \
    libqt5widgets5 \
    # Basic image processing
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONPATH="/app"
ENV QT_QPA_PLATFORM=offscreen

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy your existing analyzer code structure
COPY analyzer/ ./analyzer/
COPY main.py .

# Create output directory for visualizations
RUN mkdir -p /app/output

# Default command - your existing PyQt5 application
CMD ["python", "main.py"]
