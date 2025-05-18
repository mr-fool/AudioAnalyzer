# Audio Analyzer for LLM

![screen](https://github.com/user-attachments/assets/fc6b3ec4-15d9-447a-8982-5cc3982c8df1)

A powerful audio analysis tool that extracts musical features from audio files and generates natural language descriptions suitable for use with Large Language Models (LLMs). The application provides comprehensive analysis of key, tempo, mood, instrumentation, and other musical characteristics, visualized through an intuitive PyQt5 interface.

## 🎵 Features

- **Comprehensive Audio Analysis**: Extract key, BPM, loudness, dissonance, mood, and instruments from audio files
- **LLM-Ready Descriptions**: Generate detailed natural language descriptions of audio characteristics for use with AI models
- **Advanced Visualizations**: Display audio spectrum, mel-band energy, and MFCC coefficients
- **Multi-Format Support**: Process MP3, WAV, OGG, and FLAC audio files
- **Mood Detection**: Identify emotional qualities based on musical features
- **Instrument Recognition**: Detect probable instruments present in the audio

## 🖥️ Screenshots

### Analysis Results
![spectrum](https://github.com/user-attachments/assets/b7fcbb28-a415-4b02-ae7d-7715c90ca341)
![mel bands](https://github.com/user-attachments/assets/bca379a5-c83d-49a5-bdbe-2d158d1cb3fd)
![mfcc co](https://github.com/user-attachments/assets/6aaade4b-b789-4774-9864-3983ffc98e6d)

## 🛠️ Technology Stack

This application leverages several powerful libraries:

- **[Essentia](https://essentia.upf.edu/)**: Advanced open-source library for audio analysis, developed by the Music Technology Group at Universitat Pompeu Fabra
- **[PyQt5](https://www.riverbankcomputing.com/software/pyqt/)**: Cross-platform GUI toolkit for creating desktop applications
- **[NumPy](https://numpy.org/)**: Fundamental package for scientific computing with Python
- **[Matplotlib](https://matplotlib.org/)**: Comprehensive library for creating static, animated, and interactive visualizations

## 🔧 Installation

### Docker Installation (Recommended)

Docker provides the easiest and most consistent way to run the application across different platforms.

#### Windows with Docker

1. **Prerequisites**:
   - Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
   - Install [VcXsrv Windows X Server](https://sourceforge.net/projects/vcxsrv/)

2. **Start VcXsrv**:
   - Launch XLaunch from Start menu
   - Select "Multiple windows" and click Next
   - Select "Start no client" and click Next
   - Check "Disable access control" (important) and uncheck "Native opengl", then click Next
   - Click Finish to start the X server

3. **Build and Run**:
   ```powershell
   # Build the Docker image
   docker build -t audio-analyzer .

   # Run the container
   docker run -it --rm -e DISPLAY=host.docker.internal:0.0 -v "${PWD}:/app" audio-analyzer
   ```

   **Note for Windows Command Prompt**: Use `%cd%` instead of `${PWD}`:
   ```cmd
   docker run -it --rm -e DISPLAY=host.docker.internal:0.0 -v "%cd%:/app" audio-analyzer
   ```

4. **Access Music Files**:
   To analyze music files stored elsewhere on your system, add an additional volume mount:
   ```powershell
   docker run -it --rm -e DISPLAY=host.docker.internal:0.0 -v "${PWD}:/app" -v "D:/music:/music" audio-analyzer
   ```
   Then your music files will be available at `/music` in the container.

#### Ubuntu with Docker

1. **Install Docker**:
   ```bash
   sudo apt-get update
   sudo apt-get install docker.io
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker $USER
   # Log out and back in for the group to take effect
   ```

2. **Build and Run**:
   ```bash
   # Build the Docker image
   docker build -t audio-analyzer .

   # Run the container
   docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v "$(pwd):/app" audio-analyzer
   ```

3. **If X11 Display Issues**:
   ```bash
   xhost +local:docker
   ```

### Ubuntu Native Installation

1. Install system dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip python3-pyqt5 python3-numpy python3-matplotlib
   ```

2. Install Essentia:
   ```bash
   sudo apt-get install libyaml-dev libfftw3-dev libavcodec-dev libavformat-dev libavutil-dev libavresample-dev
   sudo pip3 install essentia
   ```

3. Clone the repository:
   ```bash
   git clone https://github.com/username/audio-analyzer-llm.git
   cd audio-analyzer-llm
   ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Using the Makefile (Ubuntu)

A Makefile is provided for simplified installation and usage on Ubuntu:

```bash
# Set up the environment and install dependencies
make setup

# Run the application
make run

# Clean up virtual environment and cache files
make clean
```

### Other Operating Systems

While the application can work on other operating systems, Essentia installation can be challenging. See the [Essentia installation guide](https://essentia.upf.edu/installing.html) for detailed instructions for your platform.

## 🚀 Usage

1. Run the application:
   ```bash
   python3 main.py
   ```

2. Using the interface:
   - Click "Browse" to select an audio file (MP3, WAV, OGG, FLAC)
   - Click "Analyze" to process the file
   - View the analysis results and description
   - Use the buttons to switch between different audio visualizations
   - Click "Copy to Clipboard" to copy the generated description

3. Integration with LLMs:
   - Copy the generated description from the application
   - Use it as input for ChatGPT, Claude, or other LLMs for music-informed creative content generation

## 🧠 Technical Details

### Analysis Pipeline

The audio analysis process follows these steps:

1. **Loading**: Audio is loaded and converted to a mono signal at 44.1kHz
2. **Feature Extraction**:
   - Spectral analysis using FFT
   - MFCCs (Mel-Frequency Cepstral Coefficients) for timbre analysis
   - HPCP (Harmonic Pitch Class Profile) for key detection
   - Rhythm extraction for BPM and beat patterns
   - Loudness and dissonance calculation

3. **High-Level Feature Derivation**:
   - Mood detection based on key, tempo, and spectral features
   - Instrument detection using spectral characteristics

4. **Description Generation**:
   - Natural language synthesis of all extracted features
   - Thematic suggestions based on detected mood

### Visualization Types

- **Spectrum**: Frequency domain representation of the audio
- **Mel Bands**: Energy distribution across perceptually-weighted frequency bands
- **MFCC**: Coefficients representing the short-term power spectrum

## 📋 Requirements

- Python 3.8+
- Essentia 2.1+
- PyQt5
- NumPy
- Matplotlib

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- The [Essentia team](https://essentia.upf.edu/) for their incredible audio analysis library
- Music Technology Group at Universitat Pompeu Fabra

## 🔍 Troubleshooting

### Docker Issues

#### Windows
- If you see "Cannot connect to X server" errors, ensure VcXsrv is running with "Disable access control" checked
- If Windows Defender Firewall prompts appear, allow access for VcXsrv
- For path issues with volume mounts, use forward slashes (/) instead of backslashes (\)

#### Ubuntu
- If you encounter "Cannot open display" errors, try running `xhost +local:docker` before starting the container
- If you see permission issues, ensure your user is in the docker group: `sudo usermod -aG docker $USER`

### Essentia Installation Issues

- Essentia may fail to build on some systems. The Docker approach avoids these issues by using a pre-configured environment
- If building Essentia from source, refer to the [official installation guide](https://essentia.upf.edu/installing.html)
