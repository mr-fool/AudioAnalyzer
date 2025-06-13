# Optimized Dockerfile for AudioAnalyzer with GUI support
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Audio processing
    ffmpeg \
    libsndfile1-dev \
    libasound2-dev \
    # Build tools
    gcc \
    g++ \
    pkg-config \
    # Qt dependencies
    libqt5gui5 \
    libqt5core5a \
    libqt5widgets5 \
    # OpenCV
    libopencv-dev \
    # X11 and Qt GUI dependencies
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-xkb1 \
    xkb-data \
    libxkbcommon-x11-0 \
    # Network utilities (removed wget since we don't need it)
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONPATH="/app"
ENV QT_QPA_PLATFORM=offscreen  
ENV XDG_RUNTIME_DIR=/tmp

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY analyzer/ ./analyzer/
COPY main.py .

# Create output directory
RUN mkdir -p /app/output

# Default command
CMD ["python", "main.py"]
