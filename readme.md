# Audio Analyzer for LLM with Advanced Visualizations

![initial](https://github.com/user-attachments/assets/49bc632c-9113-4201-9e84-f7325730852b)
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
- **Radial Symmetry Mandala**: Organic curved petals with flowing gradients that respond to your music
- **Sacred Geometry**: Complex geometric patterns with mathematical precision and interlocking shapes
- **Kaleidoscope Effects**: Flowing organic shapes with liquid-like movement
- **Audio-Reactive**: Visuals respond in real-time to bass, mid, and treble frequencies
- **Multiple Styles**: Choose between mandala, sacred geometry, kaleidoscope, or mixed (auto-switching) modes
- **MP4 Export**: Generate high-quality video files ready for social media or presentations
- **Customizable Settings**: Adjust duration (5-60s), frame rate (15-30 FPS), visual style, and custom filenames

## 🖥️ Screenshots

### Analysis Results
![spectrum](https://github.com/user-attachments/assets/c42bffb0-4cb7-4b12-a8df-e5b1c9884d5a)
![mel bands](https://github.com/user-attachments/assets/82ff17a1-de40-4ff6-92d2-5735431fb8f5)
![mfcc](https://github.com/user-attachments/assets/80fc9e82-c8c1-4930-9040-b8d52c144178)
### NEW: Video Visualizations
*Example visualizations showing radial symmetry mandala, sacred geometry, and kaleidoscope effects responding to music*

## 📹 Sample Visualizations

### Radial Symmetry Mandala
![mandala](https://github.com/user-attachments/assets/122618c9-2fe7-4bee-8ac3-6101facbc1bd)

*Organic curved petals with flowing gradients responding to bass and mid frequencies*

### Sacred Geometry

![scared_geometry](https://github.com/user-attachments/assets/60c0ede4-e11e-4b3e-9e5c-399a4fbf1083)

*Complex interlocking geometric patterns with mathematical precision*

### Kaleidoscope
![kaleidoscope](https://github.com/user-attachments/assets/b4f29a47-4cd7-43cf-a5dd-0c0185d3419d)

*Flowing organic shapes with liquid-like movement and symmetric mirroring*

### Mixed Mode Examples

![mixed](https://github.com/user-attachments/assets/18c8449b-f2df-4851-a4e8-e99b6f31d7ff)
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
   - Select style: Mandala, Sacred Geometry, Kaleidoscope, or Mixed
   - Enter custom filename (optional)
   - Click "Generate Visualization" to create MP4/AVI file
   - Output saved with your chosen filename or auto-generated name

4. **Analyze audio** (optional):
   - Click "Analyze" to process the file for detailed analysis
   - View the analysis results and description
   - Use the buttons to switch between different audio visualizations
   - Click "Copy to Clipboard" to copy the generated description

### NEW: Video Visualization Styles

#### Radial Symmetry Mandala
- **Organic curved petals** with smooth flowing gradients
- **4 concentric layers** creating depth and complexity
- **36-point smooth curves** for natural organic appearance
- **Audio-reactive**: Bass controls petal count, mid frequencies affect flow patterns
- **Breathing effects**: Petals pulse and flow with the music

#### Sacred Geometry
- **Complex mathematical patterns** with interlocking geometric shapes
- **5 distinct layers**: Outer ring, star polygons, inner polygons, Flower of Life center, connecting lines
- **Perfect symmetry**: Hexagons, triangles, and sacred ratios
- **Audio-reactive**: Different frequency bands control various geometric elements
- **Precision**: Mathematical relationships create harmonious visual balance

#### Kaleidoscope 
- **Flowing organic shapes** with liquid-like movement
- **64 flowing segments** with multiple depth layers
- **Wave-based motion**: Multiple sine/cosine functions create organic flow
- **Symmetric mirroring**: True kaleidoscope effect with dynamic color cycling
- **Audio-reactive**: All frequency ranges contribute to fluid motion

#### Mixed Mode
- **Intelligent auto-switching** between all three styles based on audio characteristics
- **Bass-heavy sections**: Display radial symmetry mandalas
- **Mid-heavy sections**: Show sacred geometry patterns
- **Treble-heavy sections**: Flow with kaleidoscope effects
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

- **"Could not open video writer" error**: The system automatically tries multiple codecs (mp4v, XVID, MJPG, X264) and file formats (MP4, AVI) for maximum compatibility
- **Poor audio reactivity**: Try increasing audio amplitude or adjusting frequency band scaling in the code
- **Performance issues**: Reduce frame rate or duration for faster processing
- **Large file sizes**: Lower frame rate or use shorter durations; 1024px renders require more processing power

### Essentia Installation Issues

- Essentia may fail to build on some systems. The Docker approach avoids these issues by using a pre-configured environment
- If building Essentia from source, refer to the [official installation guide](https://essentia.upf.edu/installing.html)
- The info message about missing SVM classifier models is harmless and doesn't affect functionality

## 🎨 Customization

### Adding New Visualization Styles

The visualization system is designed to be extensible. To add new styles:

1. Create a new generation method in `analyzer/visualizer.py` (e.g., `generate_your_style_frame()`)
2. Add the style to the dropdown in `analyzer/ui/panels.py` 
3. Update the style selection logic in `create_visualization_video()`
4. Consider audio reactivity: map bass, mid, treble, and mel bands to visual parameters

### Modifying Color Palettes

Edit the `color_palettes` dictionary in `VisualizationGenerator.__init__()` to add new color schemes:
```python
self.color_palettes = {
    'your_palette': [(R, G, B), (R, G, B), ...],  # Add custom colors
    'neon': [...],  # Existing palettes
    'plasma': [...]
}
```

### Adjusting Audio Reactivity

Modify the scaling factors in `extract_frame_features()` to change how responsive the visuals are:
```python
bass = min(features['bass'] * 500, 1.0)  # Increase multiplier for more sensitivity
mid = min(features['mid'] * 300, 1.0)    # Adjust these values as needed
treble = min(features['treble'] * 200, 1.0)
```
