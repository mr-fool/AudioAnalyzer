import sys
import os
import numpy as np
import essentia
import essentia.standard as es
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QTextEdit, QGroupBox, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QClipboard
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class AnalyzerThread(QThread):
    """Thread for running the audio analysis without freezing the UI"""
    analysis_complete = pyqtSignal(dict)
    analysis_error = pyqtSignal(str)
    
    def __init__(self, file_path, analyzer):
        super().__init__()
        self.file_path = file_path
        self.analyzer = analyzer
        
    def run(self):
        try:
            # Analyze audio
            results = self.analyzer.analyze_audio(self.file_path)
            self.analysis_complete.emit(results)
        except Exception as e:
            self.analysis_error.emit(str(e))

class AudioAnalyzer:
    def __init__(self):
        self.sample_rate = 44100
        self.results = {}
        
    def load_audio(self, file_path):
        """Load audio file using Essentia"""
        try:
            # Load audio file
            audio = es.MonoLoader(filename=file_path, sampleRate=self.sample_rate)()
            return audio
        except Exception as e:
            print(f"Error loading audio: {e}")
            return None
            
    def analyze_audio(self, file_path):
        """Analyze audio using Essentia"""
        results = {}
        
        # Load audio
        audio = self.load_audio(file_path)
        if audio is None:
            raise Exception("Failed to load audio file")
        
        # Ensure audio array has even length for FFT
        if len(audio) % 2 != 0:
            audio = audio[:-1]  # Remove last sample to make it even
            
        # Initialize algorithms
        spectrum = es.Spectrum()
        melBands = es.MelBands()
        mfcc = es.MFCC()
        key = es.Key()
        bpm = es.RhythmExtractor2013()
        loudness = es.Loudness()
        dissonance = es.Dissonance()
        
        # Initialize HPCP with the required algorithms
        spectralPeaks = es.SpectralPeaks()
        hpcp = es.HPCP()
        
        # Extract features with error handling
        try:
            spec = spectrum(audio)
            mel_bands = melBands(spec)
            mfcc_bands = mfcc(spec)[1]
            
            # Calculate HPCP by first getting the spectral peaks
            freqs, mags = spectralPeaks(spec)
            hpcp_output = hpcp(freqs, mags)
            
            # Get key with error handling
            try:
                key_data = key(hpcp_output)
            except Exception as e:
                print(f"Warning: Key detection error: {e}")
                # Use default key if detection fails
                key_data = ("C major", "major")  # Default to C major
                
            rhythm_data = bpm(audio)
            loud = loudness(audio)
            diss = dissonance(spec)
        except Exception as e:
            print(f"Warning: Feature extraction error: {e}")
            # Use default values if extraction fails
            spec = np.zeros(1025)  # Default empty spectrum
            mel_bands = np.zeros(40)  # Default mel bands
            mfcc_bands = np.zeros(13)  # Default MFCC bands
            key_data = ("C major", "major")  # Default to C major
            rhythm_data = (120, np.array([0]), np.array([0]), np.array([0]))  # Default 120 BPM
            loud = -20  # Default loudness
            diss = 0.5  # Default dissonance
        
        # Instrument detection using MusicExtractor
        try:
            music_extractor = es.MusicExtractor(lowlevelStats=['mean', 'stdev'],
                                              rhythmStats=['mean', 'stdev'],
                                              tonalStats=['mean', 'stdev'])
            features = music_extractor(file_path)
        except Exception as e:
            print(f"Warning: MusicExtractor error: {e}")
            # Create a minimal features dict with defaults
            features = self._create_default_features()
        
        # Mood detection based on features
        # Using simple rules based on key, tempo and spectral features
        mood = self._detect_mood(key_data[0], rhythm_data[0], loud, mfcc_bands, mel_bands)
        
        # Instrument detection
        instruments = self._detect_instruments(features)
        
        # Store results
        results["key"] = f"{key_data[0]} {key_data[1]}"  # Key name and scale
        results["bpm"] = round(rhythm_data[0], 1)  # BPM value
        results["loudness"] = round(loud, 2)  # Loudness in dB
        results["dissonance"] = round(diss, 2)  # Dissonance value
        results["mood"] = mood  # Detected mood
        results["instruments"] = instruments  # Detected instruments
        results["advanced_features"] = features  # All extracted features
        results["audio"] = audio  # Store audio for visualization
        
        self.results = results
        return results
    
    def _create_default_features(self):
        """Create default features dict in case MusicExtractor fails"""
        features = {
            'lowlevel.dynamic_complexity': 0.3,
            'rhythm.danceability': 0.5,
            'tonal.chords_number': 3,
            'rhythm.beats_loudness.mean': 0.4,
            'lowlevel.spectral_energy_band_ratio_0.mean': 0.3,
            'lowlevel.spectral_energy_band_ratio_1.mean': 0.2,
            'lowlevel.spectral_energy_band_ratio_2.mean': 0.2,
            'lowlevel.spectral_energy_band_ratio_3.mean': 0.1,
            'lowlevel.spectral_contrast_coeffs_0.mean': 0.1,
            'lowlevel.mfcc_bands.mean': 0.4,
            'lowlevel.spectral_centroid.mean': 1200,
            'lowlevel.spectral_rolloff.mean': 2000,
            'lowlevel.spectral_flatness_db.mean': -35
        }
        return features
    
    def _detect_mood(self, key, bpm, loudness, mfcc_bands, mel_bands):
        """Detect mood of the audio based on extracted features"""
        moods = []
        
        # Tempo based mood detection
        if bpm < 70:
            moods.append("slow")
            moods.append("relaxed")
        elif bpm < 100:
            moods.append("moderate")
            moods.append("steady")
        elif bpm < 120:
            moods.append("upbeat")
        else:
            moods.append("energetic")
            moods.append("fast")
        
        # Loudness based mood
        if loudness < -20:
            moods.append("soft")
            moods.append("intimate")
        elif loudness < -10:
            moods.append("balanced")
        else:
            moods.append("loud")
            moods.append("intense")
        
        # Key based mood (simplified)
        major_keys = ["C major", "G major", "D major", "A major", "E major", "B major", "F# major"]
        minor_keys = ["A minor", "E minor", "B minor", "F# minor", "C# minor", "G# minor", "D# minor"]
        
        if key in major_keys:
            moods.append("happy")
            moods.append("bright")
        elif key in minor_keys:
            moods.append("melancholic")
            moods.append("somber")
        
        # Spectral features for additional mood detection
        # High energy in higher mel bands often indicates brightness
        try:
            high_energy = np.mean(mel_bands[15:]) > np.mean(mel_bands[:15])
            if high_energy:
                moods.append("bright")
                moods.append("sharp")
            else:
                moods.append("warm")
                moods.append("deep")
        except:
            # Default values if calculation fails
            moods.append("balanced")
        
        # Use MFCC for texture
        try:
            mfcc_std = np.std(mfcc_bands)
            if mfcc_std > 15:
                moods.append("complex")
                moods.append("textured")
            else:
                moods.append("simple")
                moods.append("clean")
        except:
            # Default values if calculation fails
            moods.append("textured")
        
        # Remove duplicates and return
        return list(set(moods))
    
    def _detect_instruments(self, features):
        """Detect instruments in the audio based on extracted features"""
        instruments = []
        
        try:
            # Check for percussion
            if features['rhythm.beats_loudness.mean'] > 0.5:
                instruments.append("drums")
            
            # Check for bass
            if features['lowlevel.spectral_energy_band_ratio_0.mean'] > 0.4:
                instruments.append("bass")
            
            # Check for guitar or strings
            if features['lowlevel.spectral_energy_band_ratio_2.mean'] > 0.3:
                if features['lowlevel.spectral_centroid.mean'] < 1500:
                    instruments.append("guitar")
                else:
                    instruments.append("strings")
            
            # Check for piano
            if (features['lowlevel.spectral_energy_band_ratio_1.mean'] > 0.25 and 
                features['lowlevel.spectral_contrast_coeffs_0.mean'] > 0.2):
                instruments.append("piano")
            
            # Check for vocals
            if features['lowlevel.mfcc_bands.mean'] > 0.5:
                instruments.append("vocals")
            
            # Check for brass
            if (features['lowlevel.spectral_energy_band_ratio_3.mean'] > 0.2 and 
                features['lowlevel.spectral_rolloff.mean'] > 3000):
                instruments.append("brass")
            
            # Check for synthesizers
            if features['lowlevel.spectral_flatness_db.mean'] > -30:
                instruments.append("synthesizer")
        except Exception as e:
            print(f"Warning: Instrument detection error: {e}")
        
        # If no instruments detected, add some fallbacks based on general features
        if not instruments:
            try:
                if features['lowlevel.spectral_centroid.mean'] < 1000:
                    instruments.append("bass-heavy instruments")
                elif features['lowlevel.spectral_centroid.mean'] < 2000:
                    instruments.append("mid-range instruments")
                else:
                    instruments.append("high-range instruments")
            except:
                # Most generic fallback
                instruments.append("mixed instruments")
        
        return instruments
    
    def generate_description(self):
        """Generate a detailed description of the audio for LLM input"""
        if not self.results:
            return "No analysis results available."
        
        r = self.results
        
        # Create a descriptive text about the audio
        description = f"This audio track is in {r['key']} with a tempo of {r['bpm']} BPM. "
        description += f"The overall loudness is {r['loudness']} dB, which makes it a "
        
        # Add mood description
        if r['mood']:
            description += f"{', '.join(r['mood'][:3])} piece. "
        
        # Add instruments
        if r['instruments']:
            description += f"The main instruments detected are {', '.join(r['instruments'])}. "
        
        # Add additional characteristics
        if 'advanced_features' in r:
            try:
                f = r['advanced_features']
                
                # Dynamics
                if f['lowlevel.dynamic_complexity'] > 0.5:
                    description += "It has varied dynamics with significant changes in intensity. "
                else:
                    description += "It maintains a relatively consistent dynamic level throughout. "
                
                # Rhythm
                if f['rhythm.danceability'] > 0.6:
                    description += "The rhythm is highly danceable and groovy. "
                else:
                    description += "The rhythm is more complex and less dance-oriented. "
                    
                # Harmony
                if f['tonal.chords_number'] > 4:
                    description += "It has a rich harmonic progression with multiple chord changes. "
                else:
                    description += "It has a simpler harmonic structure with fewer chord changes. "
            except Exception as e:
                print(f"Warning: Error generating additional characteristics: {e}")
                # Add generic description if we can't get specific features
                description += "It has a distinctive sonic character. "
        
        # Summary for lyrics suggestions
        description += "\n\nLyrics for this track should reflect its "
        if r['mood']:
            description += f"{', '.join(r['mood'][:2])} atmosphere"
        else:
            description += "distinctive atmosphere"
            
        description += " and could explore themes that complement its "
        
        # Suggest themes based on mood
        themes = []
        moods = r.get('mood', [])
        
        if any(m in moods for m in ["happy", "bright", "energetic"]):
            themes.extend(["celebration", "optimism", "adventure"])
        elif any(m in moods for m in ["melancholic", "somber", "soft"]):
            themes.extend(["reflection", "longing", "memory"])
        elif any(m in moods for m in ["intense", "complex", "fast"]):
            themes.extend(["struggle", "determination", "passion"])
        else:
            themes.extend(["journey", "transformation", "connection"])
            
        description += f"{', '.join(themes)} themes."
        
        return description


class MatplotlibCanvas(FigureCanvas):
    """Matplotlib canvas for displaying visualizations"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        
        super(MatplotlibCanvas, self).__init__(self.fig)
        
        self.setParent(parent)
        
        # Set some matplotlib params for better integration with Qt dark themes
        plt.rcParams.update({
            'axes.facecolor': '#F0F0F0',
            'figure.facecolor': '#F0F0F0',
        })


class AudioAnalyzerApp(QMainWindow):
    """Main application window for the Audio Analyzer"""
    def __init__(self):
        super().__init__()
        
        self.analyzer = AudioAnalyzer()
        self.current_audio = None
        self.results = None
        
        self.setWindowTitle("Audio Analyzer for LLM")
        self.setGeometry(100, 100, 900, 600)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Create left panel (control panel)
        left_panel = self.create_control_panel()
        
        # Create right panel (visualization panel)
        right_panel = self.create_visualization_panel()
        
        # Create splitter to allow resizing
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 500])
        
        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
    def create_control_panel(self):
        """Create the control panel (left side)"""
        control_panel = QWidget()
        layout = QVBoxLayout()
        
        # File selection
        file_group = QGroupBox("Audio File")
        file_layout = QHBoxLayout()
        
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setWordWrap(True)
        
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_file)
        
        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(browse_button)
        file_group.setLayout(file_layout)
        
        # Analyze button
        analyze_button = QPushButton("Analyze")
        analyze_button.clicked.connect(self.analyze_audio)
        
        # Results area
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        
        results_layout.addWidget(self.results_text)
        results_group.setLayout(results_layout)
        
        # Description area
        description_group = QGroupBox("Description for LLM")
        description_layout = QVBoxLayout()
        
        self.description_text = QTextEdit()
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(self.copy_to_clipboard)
        
        description_layout.addWidget(self.description_text)
        description_layout.addWidget(copy_button)
        description_group.setLayout(description_layout)
        
        # Add all widgets to the main layout
        layout.addWidget(file_group)
        layout.addWidget(analyze_button)
        layout.addWidget(results_group)
        layout.addWidget(description_group)
        
        control_panel.setLayout(layout)
        return control_panel
        
    def create_visualization_panel(self):
        """Create the visualization panel (right side)"""
        visualization_panel = QWidget()
        layout = QVBoxLayout()
        
        # Matplotlib canvas for visualizations
        self.canvas = MatplotlibCanvas(visualization_panel)
        
        # Buttons for different visualizations
        button_layout = QHBoxLayout()
        
        spectrum_button = QPushButton("Spectrum")
        spectrum_button.clicked.connect(self.show_spectrum)
        
        melbands_button = QPushButton("Mel Bands")
        melbands_button.clicked.connect(self.show_melbands)
        
        mfcc_button = QPushButton("MFCC")
        mfcc_button.clicked.connect(self.show_mfcc)
        
        button_layout.addWidget(spectrum_button)
        button_layout.addWidget(melbands_button)
        button_layout.addWidget(mfcc_button)
        
        # Add widgets to layout
        layout.addWidget(self.canvas)
        layout.addLayout(button_layout)
        
        visualization_panel.setLayout(layout)
        return visualization_panel
    
    def browse_file(self):
        """Open file dialog to select an audio file"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Audio File", "", 
            "Audio Files (*.mp3 *.wav *.ogg *.flac);;All Files (*)"
        )
        
        if file_path:
            self.file_path_label.setText(file_path)
    
    def analyze_audio(self):
        """Analyze the selected audio file"""
        file_path = self.file_path_label.text()
        
        if file_path == "No file selected" or not os.path.exists(file_path):
            self.results_text.setText("Please select a valid audio file first.")
            return
        
        # Update UI
        self.results_text.setText("Analyzing audio...")
        self.description_text.setText("")
        
        # Create and start analysis thread
        self.analysis_thread = AnalyzerThread(file_path, self.analyzer)
        self.analysis_thread.analysis_complete.connect(self.update_results)
        self.analysis_thread.analysis_error.connect(self.show_error)
        self.analysis_thread.start()
    
    @pyqtSlot(dict)
    def update_results(self, results):
        """Update UI with analysis results"""
        self.results = results
        self.current_audio = results.get('audio')
        
        # Display basic results
        result_text = f"Key: {results['key']}\n"
        result_text += f"BPM: {results['bpm']}\n"
        result_text += f"Loudness: {results['loudness']} dB\n"
        result_text += f"Dissonance: {results['dissonance']}\n\n"
        result_text += f"Detected Mood: {', '.join(results['mood'][:5])}\n\n"
        result_text += f"Detected Instruments: {', '.join(results['instruments'])}"
        
        self.results_text.setText(result_text)
        
        # Generate description
        description = self.analyzer.generate_description()
        self.description_text.setText(description)
        
        # Show spectrum visualization
        self.show_spectrum()
    
    @pyqtSlot(str)
    def show_error(self, error_msg):
        """Display error message"""
        self.results_text.setText(f"Error during analysis: {error_msg}\n\nPlease try a different audio file or format.")
        
        # Show a basic visualization to avoid a blank canvas
        self.canvas.ax.clear()
        self.canvas.ax.text(0.5, 0.5, "Analysis failed - No visualization available", 
                          horizontalalignment='center', verticalalignment='center')
        self.canvas.draw()
    
    def copy_to_clipboard(self):
        """Copy description to clipboard"""
        description = self.description_text.toPlainText()
        if description:
            clipboard = QApplication.clipboard()
            clipboard.setText(description)
    
    def show_spectrum(self):
        """Show spectrum visualization"""
        if self.current_audio is None:
            return
        
        try:
            # Ensure audio has even length
            audio = self.current_audio
            if len(audio) % 2 != 0:
                audio = audio[:-1]
                
            spectrum = es.Spectrum()
            spec = spectrum(audio)
            
            self.canvas.ax.clear()
            self.canvas.ax.plot(spec[:len(spec)//2])  # Only plot first half (up to Nyquist frequency)
            self.canvas.ax.set_title("Audio Spectrum")
            self.canvas.ax.set_xlabel("Frequency Bin")
            self.canvas.ax.set_ylabel("Magnitude")
            
            self.canvas.draw()
        except Exception as e:
            print(f"Error displaying spectrum: {e}")
            self.canvas.ax.clear()
            self.canvas.ax.text(0.5, 0.5, "Unable to display spectrum", 
                              horizontalalignment='center', verticalalignment='center')
            self.canvas.draw()
    
    def show_melbands(self):
        """Show mel bands visualization"""
        if self.current_audio is None:
            return
        
        try:
            # Ensure audio has even length
            audio = self.current_audio
            if len(audio) % 2 != 0:
                audio = audio[:-1]
                
            spectrum = es.Spectrum()
            mel_bands = es.MelBands()
            spec = spectrum(audio)
            bands = mel_bands(spec)
            
            self.canvas.ax.clear()
            self.canvas.ax.bar(range(len(bands)), bands)
            self.canvas.ax.set_title("Mel Bands")
            self.canvas.ax.set_xlabel("Mel Band")
            self.canvas.ax.set_ylabel("Magnitude")
            
            self.canvas.draw()
        except Exception as e:
            print(f"Error displaying mel bands: {e}")
            self.canvas.ax.clear()
            self.canvas.ax.text(0.5, 0.5, "Unable to display mel bands", 
                              horizontalalignment='center', verticalalignment='center')
            self.canvas.draw()
    
    def show_mfcc(self):
        """Show MFCC visualization"""
        if self.current_audio is None:
            return
        
        try:
            # Ensure audio has even length
            audio = self.current_audio
            if len(audio) % 2 != 0:
                audio = audio[:-1]
                
            spectrum = es.Spectrum()
            mfcc = es.MFCC()
            spec = spectrum(audio)
            mfcc_bands = mfcc(spec)[1]
            
            self.canvas.ax.clear()
            self.canvas.ax.bar(range(len(mfcc_bands)), mfcc_bands)
            self.canvas.ax.set_title("MFCC Coefficients")
            self.canvas.ax.set_xlabel("MFCC Coefficient")
            self.canvas.ax.set_ylabel("Value")
            
            self.canvas.draw()
        except Exception as e:
            print(f"Error displaying MFCC: {e}")
            self.canvas.ax.clear()
            self.canvas.ax.text(0.5, 0.5, "Unable to display MFCC coefficients", 
                              horizontalalignment='center', verticalalignment='center')
            self.canvas.draw()


if __name__ == "__main__":
    # Print Essentia version
    print(f"Using Essentia version: {essentia.__version__}")
    
    # Start the PyQt5 application
    app = QApplication(sys.argv)
    window = AudioAnalyzerApp()
    window.show()
    sys.exit(app.exec_())
