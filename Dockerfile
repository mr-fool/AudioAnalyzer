FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV QT_X11_NO_MITSHM=1
ENV PYTHONUNBUFFERED=1

# Add universe repository
RUN apt-get update && apt-get install -y software-properties-common && \
    add-apt-repository universe

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pyqt5 \
    libyaml-dev \
    libfftw3-dev \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libsamplerate0-dev \
    libtag1-dev \
    libchromaprint-dev \
    libsndfile1-dev \
    libx11-xcb1 \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# First install numpy 1.x explicitly
RUN pip3 install "numpy<2.0"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set display for X11 forwarding
ENV DISPLAY=host.docker.internal:0.0

# Command to run the application
CMD ["python3", "main.py"]