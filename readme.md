# Audio Analyzer for LLM with Advanced Visualizations

![initial](https://github.com/user-attachments/assets/a4acb904-6942-427b-87fb-f82225b033aa)

A powerful audio analysis tool that extracts musical features from audio files and generates natural language descriptions suitable for use with Large Language Models (LLMs). The application provides comprehensive analysis of key, tempo, mood, instrumentation, and other musical characteristics, visualized through an intuitive PyQt5 interface. **NEW: Now includes stunning 90s-style geometric mandala and kaleidoscope video visualizations!**

## 🎵 Features

### Core Audio Analysis
- **Comprehensive Audio Analysis**: Extract key, BPM, loudness, dissonance, mood, and instruments from audio files
- **LLM-Ready Descriptions**: Generate detailed natural language descriptions of audio characteristics for use with AI models
- **Advanced Visualizations**: Display audio spectrum, mel-band energy, and MFCC coefficients
- **Multi-Format Support**: Process MP3, WAV, OGG, and FLAC audio files
- **Mood Detection**: Identify emotional qualities based on musical features
- **Instrument Recognition**: Detect probable instruments present in the audio

### NEW: Video Visualizations
- **Geometric Mandala Visualizations**: Complex sacred geometry patterns that respond to your music
- **Kaleidoscope Effects**: Flowing organic shapes with liquid-like movement
- **Audio-Reactive**: Visuals respond in real-time to bass, mid, and treble frequencies
- **Multiple Styles**: Choose between mandala, kaleidoscope, or mixed (auto-switching) modes
- **MP4 Export**: Generate high-quality video files ready for social media or presentations
- **Customizable Settings**: Adjust duration (5-60s), frame rate (15-30 FPS), and visual style

## 🖥️ Screenshots

### Analysis Results
![spectrum](https://github.com/user-attachments/assets/b1b8a221-d4c3-4147-8070-2412108e71a7)
![mfcc](https://github.com/user-attachments/assets/1f62abd7-eb77-4d5d-b7ef-23493ba6dc6e)
![mel bands](https://github.com/user-attachments/assets/0f10c0b5-5515-429a-a636-13655688ddf0)


### NEW: Video Visualizations
*Example visualizations showing geometric mandala and kaleidoscope effects responding to music*

## 🛠️ Technology Stack

This application leverages several powerful libraries:

- **[Essentia](https://essentia.upf.edu/)**: Advanced open-source library for audio analysis, developed by the Music Technology Group at Universitat Pompeu Fabra
- **[PyQt5](https://www.riverbankcomputing.com/software/pyqt/)**: Cross-platform GUI toolkit for creating desktop applications
- **[OpenCV](https://opencv.org/)**: Computer vision library for advanced video generation and image processing
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

   # Run the container with GUI support
   docker run -it --rm -e DISPLAY=host.docker.internal:0.0 -e QT_QPA_PLATFORM=xcb -v "${PWD}:/app" audio-analyzer
   ```

   **Note for Command Prompt**: Use `%cd%` instead of `${PWD}`:
   ```cmd
   docker run -it --rm -e DISPLAY=host.docker.internal:0.0 -e QT_QPA_PLATFORM=xcb -v "%cd%:/app" audio-analyzer
   ```

4. **Access Music Files**:
   To analyze music files stored elsewhere on your system, add an additional volume mount:
   ```powershell
   docker run -it --rm -e DISPLAY=host.docker.internal:0.0 -e QT_QPA_PLATFORM=xcb -v "${PWD}:/app" -v "D:/music:/music" audio-analyzer
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
   sudo apt-get install python3-pip python3-pyqt5 python3-numpy python3-matplotlib python3-opencv-dev
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

## 🚀 Usage

### Basic Workflow

1. **Run the application**:
   ```bash
   python3 main.py
   ```

2. **Load an audio file**:
   - Click "Browse" to select an audio file (MP3, WAV, OGG, FLAC)
   - The video visualization panel becomes enabled immediately

3. **Generate visualizations** (NEW):
   - Set duration (5-60 seconds)
   - Choose frame rate (15-30 FPS)
   - Select style: Mandala, Kaleidoscope, or Mixed
   - Click "Generate Visualization" to create MP4 file
   - Output saved as `[filename]_visualization.mp4`

4. **Analyze audio** (optional):
   - Click "Analyze" to process the file for detailed analysis
   - View the analysis results and description
   - Use the buttons to switch between different audio visualizations
   - Click "Copy to Clipboard" to copy the generated description

### NEW: Video Visualization Styles

#### Geometric Mandala
- **Complex sacred geometry patterns** with mathematical precision
- **Multiple concentric layers** of geometric shapes
- **Audio-reactive segments**: Bass controls number of elements, mid frequencies affect rotation
- **Perfect symmetry**: Hexagons, stars, and connecting lines create intricate patterns

#### Kaleidoscope 
- **Flowing organic shapes** with liquid-like movement
- **64 flowing segments** with multiple depth layers
- **Wave-based motion**: Multiple sine/cosine functions create organic flow
- **Symmetric mirroring**: True kaleidoscope effect with dynamic color cycling

#### Mixed Mode
- **Automatic switching** between mandala and kaleidoscope based on audio characteristics
- **Bass-heavy sections**: Display geometric mandalas
- **Treble-heavy sections**: Show flowing kaleidoscopes
- **Seamless transitions**: Smooth changes based on real-time audio analysis

### Integration with LLMs

- Copy the generated description from the application
- Use it as input for ChatGPT, Claude, or other LLMs for music-informed creative content generation
- Perfect for generating album descriptions, playlist narratives, or creative writing prompts

## 🧠 Technical Details

### Analysis Pipeline

The audio analysis process follows these steps:

1. **Loading**: Audio is loaded using Essentia's MonoLoader at 44.1kHz
2. **Feature Extraction**:
   - Spectral analysis using Essentia's Spectrum algorithm
   - MFCCs (Mel-Frequency Cepstral Coefficients) for timbre analysis
   - Mel-band energy distribution for frequency analysis
   - HPCP (Harmonic Pitch Class Profile) for key detection
   - Rhythm extraction for BPM and beat patterns
   - Loudness and dissonance calculation

3. **High-Level Feature Derivation**:
   - Mood detection based on key, tempo, and spectral features
   - Instrument detection using spectral characteristics

4. **Description Generation**:
   - Natural language synthesis of all extracted features
   - Thematic suggestions based on detected mood

### NEW: Visualization Pipeline

1. **Audio Processing**: Frame-by-frame analysis using Essentia algorithms
2. **Feature Mapping**: Bass, mid, treble extracted from spectrum analysis
3. **Geometric Generation**: Mathematical functions create precise patterns
4. **Audio Reactivity**: Real-time mapping of audio features to visual parameters
5. **Video Export**: OpenCV-based MP4 generation with customizable quality

### Visualization Types

#### Traditional Analysis Plots
- **Spectrum**: Frequency domain representation of the audio
- **Mel Bands**: Energy distribution across perceptually-weighted frequency bands
- **MFCC**: Coefficients representing the short-term power spectrum

#### NEW: Video Visualizations
- **Frame Rate**: 15-30 FPS for smooth motion
- **Resolution**: 512x512 pixels (customizable)
- **Color Palettes**: Neon and plasma themes optimized for visual impact
- **Audio Synchronization**: Perfect sync between audio features and visual elements

## 📋 Requirements

- Python 3.8+
- Essentia 2.1+
- PyQt5
- OpenCV 4.5+
- NumPy <2.0 (for Essentia compatibility)
- Pillow 9.0+

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- The [Essentia team](https://essentia.upf.edu/) for their incredible audio analysis library
- Music Technology Group at Universitat Pompeu Fabra
- OpenCV community for powerful computer vision tools

## 🔍 Troubleshooting

### Docker Issues

#### Windows
- If you see "Cannot connect to X server" errors, ensure VcXsrv is running with "Disable access control" checked
- If Windows Defender Firewall prompts appear, allow access for VcXsrv
- For path issues with volume mounts, use forward slashes (/) instead of backslashes (\)
- Use `QT_QPA_PLATFORM=xcb` environment variable if GUI doesn't appear

#### Ubuntu
- If you encounter "Cannot open display" errors, try running `xhost +local:docker` before starting the container
- If you see permission issues, ensure your user is in the docker group: `sudo usermod -aG docker $USER`

### NumPy Compatibility Issues

If you see NumPy version errors with Essentia:
```bash
pip install 'numpy<2.0'
```

Essentia requires NumPy 1.x for compatibility.

### Visualization Issues

- **No MP4 output**: Check that OpenCV video writer supports mp4v codec
- **Poor audio reactivity**: Try increasing audio amplitude or adjusting frequency band scaling
- **Performance issues**: Reduce frame rate or duration for faster processing

### Essentia Installation Issues

- Essentia may fail to build on some systems. The Docker approach avoids these issues by using a pre-configured environment
- If building Essentia from source, refer to the [official installation guide](https://essentia.upf.edu/installing.html)
- The info message about missing SVM classifier models is harmless and doesn't affect functionality

## 🎨 Customization

### Adding New Visualization Styles

The visualization system is designed to be extensible. To add new styles:

1. Create a new generation method in `analyzer/visualizer.py`
2. Add the style to the dropdown in `analyzer/ui/panels.py`
3. Update the style selection logic in `create_visualization_video()`

### Modifying Color Palettes

Edit the `color_palettes` dictionary in `VisualizationGenerator.__init__()` to add new color schemes.

### Adjusting Audio Reactivity

Modify the scaling factors in `extract_frame_features()` to change how responsive the visuals are to different frequency ranges.
