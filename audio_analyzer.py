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
            audio = es.MonoLoader(filename=file_path, sampleRate=self.sample_rate)()
            return audio
        except Exception as e:
            print(f"Error loading audio: {e}")
            return None
            
    def analyze_audio(self, file_path):
        """Analyze audio using Essentia"""
        results = {}
        
        audio = self.load_audio(file_path)
        if audio is None:
            raise Exception("Failed to load audio file")
        
        if len(audio) % 2 != 0:
            audio = audio[:-1]
            
        nyquist_freq = self.sample_rate / 2
        high_freq_bound = min(22000, nyquist_freq - 50)
        
        spectrum = es.Spectrum()
        melBands = es.MelBands(inputSize=len(audio) // 2 + 1, 
                              highFrequencyBound=high_freq_bound)
        mfcc = es.MFCC(inputSize=len(audio) // 2 + 1, 
                      highFrequencyBound=high_freq_bound)
        key = es.Key()
        bpm = es.RhythmExtractor2013()
        loudness = es.Loudness()
        dissonance = es.Dissonance()
        
        spectralPeaks = es.SpectralPeaks()
        hpcp = es.HPCP()
        
        try:
            spec = spectrum(audio)
            mel_bands = melBands(spec)
            mfcc_bands = mfcc(spec)[1]
            
            freqs, mags = spectralPeaks(spec)
            hpcp_output = hpcp(freqs, mags)
            diss = dissonance(freqs, mags)
            
            try:
                key_data = key(hpcp_output)
            except Exception as e:
                print(f"Warning: Key detection error: {e}")
                key_data = ("C major", "major")
                
            rhythm_data = bpm(audio)
            loud = loudness(audio)
        except Exception as e:
            print(f"Warning: Feature extraction error: {e}")
            spec = np.zeros(1025)
            mel_bands = np.zeros(40)
            mfcc_bands = np.zeros(13)
            key_data = ("C major", "major")
            rhythm_data = (120, np.array([0]), np.array([0]), np.array([0]))
            loud = -20
            diss = 0.5
        
        try:
            music_extractor = es.MusicExtractor(lowlevelStats=['mean', 'stdev'],
                                              rhythmStats=['mean', 'stdev'],
                                              tonalStats=['mean', 'stdev'])
            features = music_extractor(file_path)
            
            print(f"MusicExtractor features type: {type(features)}")
            if isinstance(features, tuple):
                print(f"Features tuple length: {len(features)}")
                if features and len(features) > 0:
                    print(f"First element type: {type(features[0])}")
            
            if isinstance(features, tuple) and features:
                first_element = features[0]
                if hasattr(first_element, 'descriptorNames'):
                    print("First element is a Pool, converting to dictionary")
                    features_dict = {}
                    for name in first_element.descriptorNames():
                        try:
                            features_dict[name] = first_element[name]
                        except Exception as e:
                            print(f"Error accessing Pool descriptor {name}: {e}")
                elif isinstance(first_element, dict):
                    features_dict = first_element
                else:
                    print(f"Unknown first element type: {type(first_element)}")
                    features_dict = self._create_default_features()
            else:
                features_dict = features
                
        except Exception as e:
            print(f"Warning: MusicExtractor error: {e}")
            features_dict = self._create_default_features()
        
        mood = self._detect_mood(key_data[0], rhythm_data[0], loud, mfcc_bands, mel_bands)
        instruments = self._detect_instruments(features_dict)
        
        results["key"] = f"{key_data[0]} {key_data[1]}"
        results["bpm"] = round(rhythm_data[0], 1)
        results["loudness"] = round(loud, 2)
        results["dissonance"] = round(diss, 2)
        results["mood"] = mood
        results["instruments"] = instruments
        results["advanced_features"] = features_dict
        results["audio"] = audio
        
        print(f"Feature dictionary structure: {type(features_dict)}")
        if isinstance(features_dict, dict):
            print(f"Feature dictionary keys sample: {list(features_dict.keys())[:5] if features_dict else []}")
        
        self.results = results
        return results
    
    def _create_default_features(self):
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
        moods = []
        
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
        
        if loudness < -20:
            moods.append("soft")
            moods.append("intimate")
        elif loudness < -10:
            moods.append("balanced")
        else:
            moods.append("loud")
            moods.append("intense")
        
        major_keys = ["C major", "G major", "D major", "A major", "E major", "B major", "F# major"]
        minor_keys = ["A minor", "E minor", "B minor", "F# minor", "C# minor", "G# minor", "D# minor"]
        
        if key in major_keys:
            moods.append("happy")
            moods.append("bright")
        elif key in minor_keys:
            moods.append("melancholic")
            moods.append("somber")
        
        try:
            high_energy = np.mean(mel_bands[15:]) > np.mean(mel_bands[:15])
            if high_energy:
                moods.append("bright")
                moods.append("sharp")
            else:
                moods.append("warm")
                moods.append("deep")
        except:
            moods.append("balanced")
        
        try:
            mfcc_std = np.std(mfcc_bands)
            if mfcc_std > 15:
                moods.append("complex")
                moods.append("textured")
            else:
                moods.append("simple")
                moods.append("clean")
        except:
            moods.append("textured")
        
        return list(set(moods))
    
    def _detect_instruments(self, features):
        instruments = []
        
        try:
            if hasattr(features, 'descriptorNames'):
                if 'rhythm.beats_loudness.mean' in features.descriptorNames() and features['rhythm.beats_loudness.mean'] > 0.5:
                    instruments.append("drums")
                
                if 'lowlevel.spectral_energy_band_ratio_0.mean' in features.descriptorNames() and features['lowlevel.spectral_energy_band_ratio_0.mean'] > 0.4:
                    instruments.append("bass")
                
                if 'lowlevel.spectral_energy_band_ratio_2.mean' in features.descriptorNames() and features['lowlevel.spectral_energy_band_ratio_2.mean'] > 0.3:
                    if 'lowlevel.spectral_centroid.mean' in features.descriptorNames() and features['lowlevel.spectral_centroid.mean'] < 1500:
                        instruments.append("guitar")
                    else:
                        instruments.append("strings")
                
                if ('lowlevel.spectral_energy_band_ratio_1.mean' in features.descriptorNames() and 
                    'lowlevel.spectral_contrast_coeffs_0.mean' in features.descriptorNames() and
                    features['lowlevel.spectral_energy_band_ratio_1.mean'] > 0.25 and 
                    features['lowlevel.spectral_contrast_coeffs_0.mean'] > 0.2):
                    instruments.append("piano")
                
                if 'lowlevel.mfcc_bands.mean' in features.descriptorNames() and features['lowlevel.mfcc_bands.mean'] > 0.5:
                    instruments.append("vocals")
                
                if ('lowlevel.spectral_energy_band_ratio_3.mean' in features.descriptorNames() and
                    'lowlevel.spectral_rolloff.mean' in features.descriptorNames() and
                    features['lowlevel.spectral_energy_band_ratio_3.mean'] > 0.2 and 
                    features['lowlevel.spectral_rolloff.mean'] > 3000):
                    instruments.append("brass")
                
                if 'lowlevel.spectral_flatness_db.mean' in features.descriptorNames() and features['lowlevel.spectral_flatness_db.mean'] > -30:
                    instruments.append("synthesizer")
                    
            elif isinstance(features, tuple):
                if features and isinstance(features[0], dict):
                    features = features[0]
                    
                    if features.get('rhythm.beats_loudness.mean', 0) > 0.5:
                        instruments.append("drums")
                    
                    if features.get('lowlevel.spectral_energy_band_ratio_0.mean', 0) > 0.4:
                        instruments.append("bass")
                    
                    if features.get('lowlevel.spectral_energy_band_ratio_2.mean', 0) > 0.3:
                        if features.get('lowlevel.spectral_centroid.mean', 0) < 1500:
                            instruments.append("guitar")
                        else:
                            instruments.append("strings")
                    
                    if (features.get('lowlevel.spectral_energy_band_ratio_1.mean', 0) > 0.25 and 
                        features.get('lowlevel.spectral_contrast_coeffs_0.mean', 0) > 0.2):
                        instruments.append("piano")
                    
                    if features.get('lowlevel.mfcc_bands.mean', 0) > 0.5:
                        instruments.append("vocals")
                    
                    if (features.get('lowlevel.spectral_energy_band_ratio_3.mean', 0) > 0.2 and 
                        features.get('lowlevel.spectral_rolloff.mean', 0) > 3000):
                        instruments.append("brass")
                    
                    if features.get('lowlevel.spectral_flatness_db.mean', -50) > -30:
                        instruments.append("synthesizer")
                else:
                    return ["mixed instruments"]
            elif isinstance(features, dict):
                if features.get('rhythm.beats_loudness.mean', 0) > 0.5:
                    instruments.append("drums")
                
                if features.get('lowlevel.spectral_energy_band_ratio_0.mean', 0) > 0.4:
                    instruments.append("bass")
                
                if features.get('lowlevel.spectral_energy_band_ratio_2.mean', 0) > 0.3:
                    if features.get('lowlevel.spectral_centroid.mean', 0) < 1500:
                        instruments.append("guitar")
                    else:
                        instruments.append("strings")
                
                if (features.get('lowlevel.spectral_energy_band_ratio_1.mean', 0) > 0.25 and 
                    features.get('lowlevel.spectral_contrast_coeffs_0.mean', 0) > 0.2):
                    instruments.append("piano")
                
                if features.get('lowlevel.mfcc_bands.mean', 0) > 0.5:
                    instruments.append("vocals")
                
                if (features.get('lowlevel.spectral_energy_band_ratio_3.mean', 0) > 0.2 and 
                    features.get('lowlevel.spectral_rolloff.mean', 0) > 3000):
                    instruments.append("brass")
                
                if features.get('lowlevel.spectral_flatness_db.mean', -50) > -30:
                    instruments.append("synthesizer")
        except Exception as e:
            print(f"Warning: Instrument detection error: {e}")
        
        if not instruments:
            try:
                if hasattr(features, 'descriptorNames'):
                    if 'lowlevel.spectral_centroid.mean' in features.descriptorNames():
                        if features['lowlevel.spectral_centroid.mean'] < 1000:
                            instruments.append("bass-heavy instruments")
                        elif features['lowlevel.spectral_centroid.mean'] < 2000:
                            instruments.append("mid-range instruments")
                        else:
                            instruments.append("high-range instruments")
                elif isinstance(features, dict):
                    if features.get('lowlevel.spectral_centroid.mean', 0) < 1000:
                        instruments.append("bass-heavy instruments")
                    elif features.get('lowlevel.spectral_centroid.mean', 0) < 2000:
                        instruments.append("mid-range instruments")
                    else:
                        instruments.append("high-range instruments")
            except:
                instruments.append("mixed instruments")
        
        if not instruments:
            instruments.append("mixed instruments")
        
        return instruments
    
    def generate_description(self):
        if not self.results:
            return "No analysis results available."
        
        r = self.results
        
        description = f"This audio track is in {r['key']} with a tempo of {r['bpm']} BPM. "
        description += f"The overall loudness is {r['loudness']} dB, which makes it a "
        
        if r['mood']:
            description += f"{', '.join(r['mood'][:3])} piece. "
        
        if r['instruments']:
            description += f"The main instruments detected are {', '.join(r['instruments'])}. "
        
        if 'advanced_features' in r:
            try:
                f = r['advanced_features']
                valid_features = False
                
                if hasattr(f, 'descriptorNames'):
                    valid_features = True
                    if 'lowlevel.dynamic_complexity' in f.descriptorNames() and f['lowlevel.dynamic_complexity'] > 0.5:
                        description += "It has varied dynamics with significant changes in intensity. "
                    else:
                        description += "It maintains a relatively consistent dynamic level throughout. "
                    
                    if 'rhythm.danceability' in f.descriptorNames() and f['rhythm.danceability'] > 0.6:
                        description += "The rhythm is highly danceable and groovy. "
                    else:
                        description += "The rhythm is more complex and less dance-oriented. "
                        
                    if 'tonal.chords_number' in f.descriptorNames() and f['tonal.chords_number'] > 4:
                        description += "It has a rich harmonic progression with multiple chord changes. "
                    else:
                        description += "It has a simpler harmonic structure with fewer chord changes. "
                
                elif isinstance(f, tuple):
                    if f and hasattr(f[0], 'descriptorNames'):
                        valid_features = True
                        pool = f[0]
                        if 'lowlevel.dynamic_complexity' in pool.descriptorNames() and pool['lowlevel.dynamic_complexity'] > 0.5:
                            description += "It has varied dynamics with significant changes in intensity. "
                        else:
                            description += "It maintains a relatively consistent dynamic level throughout. "
                        
                        if 'rhythm.danceability' in pool.descriptorNames() and pool['rhythm.danceability'] > 0.6:
                            description += "The rhythm is highly danceable and groovy. "
                        else:
                            description += "The rhythm is more complex and less dance-oriented. "
                            
                        if 'tonal.chords_number' in pool.descriptorNames() and pool['tonal.chords_number'] > 4:
                            description += "It has a rich harmonic progression with multiple chord changes. "
                        else:
                            description += "It has a simpler harmonic structure with fewer chord changes. "
                    elif f and isinstance(f[0], dict):
                        valid_features = True
                        dict_f = f[0]
                        if dict_f.get('lowlevel.dynamic_complexity', 0) > 0.5:
                            description += "It has varied dynamics with significant changes in intensity. "
                        else:
                            description += "It maintains a relatively consistent dynamic level throughout. "
                        
                        if dict_f.get('rhythm.danceability', 0) > 0.6:
                            description += "The rhythm is highly danceable and groovy. "
                        else:
                            description += "The rhythm is more complex and less dance-oriented. "
                            
                        if dict_f.get('tonal.chords_number', 0) > 4:
                            description += "It has a rich harmonic progression with multiple chord changes. "
                        else:
                            description += "It has a simpler harmonic structure with fewer chord changes. "
                elif isinstance(f, dict):
                    valid_features = True
                    if f.get('lowlevel.dynamic_complexity', 0) > 0.5:
                        description += "It has varied dynamics with significant changes in intensity. "
                    else:
                        description += "It maintains a relatively consistent dynamic level throughout. "
                    
                    if f.get('rhythm.danceability', 0) > 0.6:
                        description += "The rhythm is highly danceable and groovy. "
                    else:
                        description += "The rhythm is more complex and less dance-oriented. "
                        
                    if f.get('tonal.chords_number', 0) > 4:
                        description += "It has a rich harmonic progression with multiple chord changes. "
                    else:
                        description += "It has a simpler harmonic structure with fewer chord changes. "
                
                if not valid_features:
                    description += "It has a distinctive sonic character. "
            except Exception as e:
                print(f"Warning: Error generating additional characteristics: {e}")
                description += "It has a distinctive sonic character. "
        
        description += "\n\nLyrics for this track should reflect its "
        if r['mood']:
            description += f"{', '.join(r['mood'][:2])} atmosphere"
        else:
            description += "distinctive atmosphere"
            
        description += " and could explore themes that complement its "
        
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
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super(MatplotlibCanvas, self).__init__(self.fig)
        self.setParent(parent)
        plt.rcParams.update({
            'axes.facecolor': '#F0F0F0',
            'figure.facecolor': '#F0F0F0',
        })

class AudioAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.analyzer = AudioAnalyzer()
        self.current_audio = None
        self.results = None
        self.setWindowTitle("Audio Analyzer for LLM")
        self.setGeometry(100, 100, 900, 600)
        self.init_ui()
        
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        left_panel = self.create_control_panel()
        right_panel = self.create_visualization_panel()
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 500])
        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
    def create_control_panel(self):
        control_panel = QWidget()
        layout = QVBoxLayout()
        file_group = QGroupBox("Audio File")
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setWordWrap(True)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(browse_button)
        file_group.setLayout(file_layout)
        analyze_button = QPushButton("Analyze")
        analyze_button.clicked.connect(self.analyze_audio)
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout()
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        results_group.setLayout(results_layout)
        description_group = QGroupBox("Description for LLM")
        description_layout = QVBoxLayout()
        self.description_text = QTextEdit()
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(self.copy_to_clipboard)
        description_layout.addWidget(self.description_text)
        description_layout.addWidget(copy_button)
        description_group.setLayout(description_layout)
        layout.addWidget(file_group)
        layout.addWidget(analyze_button)
        layout.addWidget(results_group)
        layout.addWidget(description_group)
        control_panel.setLayout(layout)
        return control_panel
        
    def create_visualization_panel(self):
        visualization_panel = QWidget()
        layout = QVBoxLayout()
        self.canvas = MatplotlibCanvas(visualization_panel)
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
        layout.addWidget(self.canvas)
        layout.addLayout(button_layout)
        visualization_panel.setLayout(layout)
        return visualization_panel
    
    def browse_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Audio File", "", 
            "Audio Files (*.mp3 *.wav *.ogg *.flac);;All Files (*)"
        )
        if file_path:
            self.file_path_label.setText(file_path)
    
    def analyze_audio(self):
        file_path = self.file_path_label.text()
        if file_path == "No file selected" or not os.path.exists(file_path):
            self.results_text.setText("Please select a valid audio file first.")
            return
        self.results_text.setText("Analyzing audio...")
        self.description_text.setText("")
        self.analysis_thread = AnalyzerThread(file_path, self.analyzer)
        self.analysis_thread.analysis_complete.connect(self.update_results)
        self.analysis_thread.analysis_error.connect(self.show_error)
        self.analysis_thread.start()
    
    @pyqtSlot(dict)
    def update_results(self, results):
        self.results = results
        self.current_audio = results.get('audio')
        result_text = f"Key: {results['key']}\n"
        result_text += f"BPM: {results['bpm']}\n"
        result_text += f"Loudness: {results['loudness']} dB\n"
        result_text += f"Dissonance: {results['dissonance']}\n\n"
        result_text += f"Detected Mood: {', '.join(results['mood'][:5])}\n\n"
        result_text += f"Detected Instruments: {', '.join(results['instruments'])}"
        self.results_text.setText(result_text)
        description = self.analyzer.generate_description()
        self.description_text.setText(description)
        self.show_spectrum()
    
    @pyqtSlot(str)
    def show_error(self, error_msg):
        self.results_text.setText(f"Error during analysis: {error_msg}\n\nPlease try a different audio file or format.")
        self.canvas.ax.clear()
        self.canvas.ax.text(0.5, 0.5, "Analysis failed - No visualization available", 
                          horizontalalignment='center', verticalalignment='center')
        self.canvas.draw()
    
    def copy_to_clipboard(self):
        description = self.description_text.toPlainText()
        if description:
            clipboard = QApplication.clipboard()
            clipboard.setText(description)
    
    def show_spectrum(self):
        if self.current_audio is None:
            return
        try:
            audio = self.current_audio
            if len(audio) % 2 != 0:
                audio = audio[:-1]
            spectrum = es.Spectrum()
            spec = spectrum(audio)
            self.canvas.ax.clear()
            self.canvas.ax.plot(spec[:len(spec)//2])
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
        if self.current_audio is None:
            return
        try:
            audio = self.current_audio
            if len(audio) % 2 != 0:
                audio = audio[:-1]
            nyquist_freq = self.analyzer.sample_rate / 2
            high_freq_bound = min(22000, nyquist_freq - 50)
            spectrum = es.Spectrum()
            mel_bands = es.MelBands(inputSize=len(audio) // 2 + 1,
                                  highFrequencyBound=high_freq_bound)
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
        if self.current_audio is None:
            return
        try:
            audio = self.current_audio
            if len(audio) % 2 != 0:
                audio = audio[:-1]
            nyquist_freq = self.analyzer.sample_rate / 2
            high_freq_bound = min(22000, nyquist_freq - 50)
            spectrum = es.Spectrum()
            mfcc = es.MFCC(inputSize=len(audio) // 2 + 1,
                         highFrequencyBound=high_freq_bound)
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
    print(f"Using Essentia version: {essentia.__version__}")
    app = QApplication(sys.argv)
    window = AudioAnalyzerApp()
    window.show()
    sys.exit(app.exec_())
