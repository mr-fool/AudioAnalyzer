# Makefile for Audio Analyzer with Visualizations on Ubuntu (No Docker)

# Variables
PYTHON := python3
PIP := pip3
VENV := venv
VENV_ACTIVATE := $(VENV)/bin/activate
APP := main.py

# Default target
all: setup run

# Check for python3-venv package
check-venv:
	@echo "Checking if python3-venv is installed..."
	@if ! dpkg -l | grep -q python3-venv; then \
		echo "The python3-venv package is not installed. Installing..."; \
		sudo apt-get update && sudo apt-get install -y python3-venv python3-dev; \
	else \
		echo "python3-venv is already installed. Continuing..."; \
	fi

# Create virtual environment
create-venv: check-venv
	@echo "Creating virtual environment..."
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@touch $(VENV_ACTIVATE)

# Install dependencies
install-deps: create-venv
	@echo "Installing dependencies..."
	@. $(VENV_ACTIVATE) && $(PIP) install --upgrade pip
	@echo "Installing system dependencies for Essentia, PyQt5, and OpenCV..."
	@sudo apt-get update && sudo apt-get install -y \
		build-essential \
		pkg-config \
		libyaml-dev \
		libfftw3-dev \
		libavcodec-dev \
		libavformat-dev \
		libavutil-dev \
		libswresample-dev \
		libsamplerate0-dev \
		libtag1-dev \
		libchromaprint-dev \
		libsndfile1-dev \
		python3-dev \
		python3-numpy \
		qtbase5-dev \
		qt5-qmake \
		qttools5-dev-tools \
		libqt5x11extras5-dev \
		libopencv-dev \
		python3-opencv \
		libjpeg-dev \
		libpng-dev \
		libtiff-dev \
		libgtk-3-dev
	@echo "Installing Python dependencies..."
	@. $(VENV_ACTIVATE) && $(PIP) install -r requirements.txt

# Complete setup
setup: install-deps
	@echo "Setup complete. Use 'make run' to start the application."

# Run the application
run:
	@if [ ! -f $(VENV_ACTIVATE) ]; then \
		echo "Virtual environment not found. Please run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Starting Audio Analyzer..."
	@. $(VENV_ACTIVATE) && $(PYTHON) $(APP)

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV) __pycache__ .pytest_cache .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.mp4" -exec rm -f {} +
	@echo "Cleaned up cache files and generated visualizations."

# Install just system dependencies (useful for troubleshooting)
system-deps:
	@echo "Installing system dependencies for Essentia, PyQt5, and OpenCV..."
	@sudo apt-get update && sudo apt-get install -y \
		python3-venv \
		python3-dev \
		build-essential \
		pkg-config \
		libyaml-dev \
		libfftw3-dev \
		libavcodec-dev \
		libavformat-dev \
		libavutil-dev \
		libswresample-dev \
		libsamplerate0-dev \
		libtag1-dev \
		libchromaprint-dev \
		libsndfile1-dev \
		python3-numpy \
		qtbase5-dev \
		qt5-qmake \
		qttools5-dev-tools \
		libqt5x11extras5-dev \
		libopencv-dev \
		python3-opencv \
		libjpeg-dev \
		libpng-dev \
		libtiff-dev \
		libgtk-3-dev

# Install just Python dependencies (useful for troubleshooting)
python-deps: create-venv
	@echo "Installing Python dependencies..."
	@. $(VENV_ACTIVATE) && $(PIP) install -r requirements.txt

# Alternative installation method without virtual environment
direct-install:
	@echo "Installing Python dependencies system-wide (not recommended)..."
	@sudo apt-get update && sudo apt-get install -y \
		python3-pip \
		python3-dev \
		python3-numpy \
		python3-matplotlib \
		python3-pyqt5 \
		python3-opencv
	@echo "Installing Essentia and visualization dependencies..."
	@sudo apt-get install -y \
		build-essential \
		pkg-config \
		libyaml-dev \
		libfftw3-dev \
		libavcodec-dev \
		libavformat-dev \
		libavutil-dev \
		libswresample-dev \
		libsamplerate0-dev \
		libtag1-dev \
		libchromaprint-dev \
		libsndfile1-dev \
		libopencv-dev \
		libjpeg-dev \
		libpng-dev \
		libtiff-dev
	@echo "Installing Python packages..."
	@sudo $(PIP) install essentia opencv-python pillow

# Test visualization (NEW: Quick test target)
test-viz:
	@if [ ! -f $(VENV_ACTIVATE) ]; then \
		echo "Virtual environment not found. Please run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Testing visualization dependencies..."
	@. $(VENV_ACTIVATE) && $(PYTHON) -c "import cv2; import numpy as np; from PIL import Image; import essentia.standard as es; print('All visualization dependencies working!')"

# Show status
status:
	@echo "=== Audio Analyzer Status ==="
	@if [ -d $(VENV) ]; then \
		echo "Virtual environment: EXISTS"; \
		if [ -f $(VENV_ACTIVATE) ]; then \
			echo "Activation script: EXISTS"; \
			echo "Python packages:"; \
			. $(VENV_ACTIVATE) && pip list | grep -E "(essentia|opencv|pillow|PyQt5|numpy)"; \
		fi; \
	else \
		echo "Virtual environment: NOT FOUND"; \
	fi
	@echo "=========================="

.PHONY: all setup run clean system-deps python-deps check-venv create-venv install-deps direct-install test-viz status
