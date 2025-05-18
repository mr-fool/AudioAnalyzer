# Makefile for Audio Analyzer on Ubuntu (No Docker)

# Variables
PYTHON := python3
PIP := pip3
VENV := venv
VENV_ACTIVATE := $(VENV)/bin/activate
APP := main.py

# Default target
all: setup run

# Create virtual environment and install dependencies
setup: $(VENV_ACTIVATE)
	@echo "Setup complete. Use 'make run' to start the application."

$(VENV_ACTIVATE): requirements.txt
	@echo "Creating virtual environment and installing dependencies..."
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@. $(VENV_ACTIVATE) && $(PIP) install --upgrade pip
	@echo "Installing system dependencies for Essentia and PyQt5..."
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
		libqt5x11extras5-dev
	@echo "Installing Python dependencies..."
	@. $(VENV_ACTIVATE) && $(PIP) install -r requirements.txt
	@touch $(VENV_ACTIVATE)

# Run the application
run: $(VENV_ACTIVATE)
	@echo "Starting Audio Analyzer..."
	@. $(VENV_ACTIVATE) && $(PYTHON) $(APP)

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV) __pycache__ .pytest_cache .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Install just system dependencies (useful for troubleshooting)
system-deps:
	@echo "Installing system dependencies for Essentia and PyQt5..."
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
		libqt5x11extras5-dev

# Install just Python dependencies (useful for troubleshooting)
python-deps: $(VENV_ACTIVATE)
	@echo "Installing Python dependencies..."
	@. $(VENV_ACTIVATE) && $(PIP) install -r requirements.txt

.PHONY: all setup run clean system-deps python-deps