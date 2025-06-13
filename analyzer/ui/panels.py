import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QFileDialog, QTextEdit, QGroupBox, QApplication,
                           QComboBox, QSpinBox, QDoubleSpinBox)
from PyQt5.QtGui import QClipboard
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import essentia.standard as es

from .canvas import MatplotlibCanvas

class ControlPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
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
        
        self.setLayout(layout)
    
    def browse_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Audio File", "", 
            "Audio Files (*.mp3 *.wav *.ogg *.flac);;All Files (*)"
        )
        
        if file_path:
            self.file_path_label.setText(file_path)
            # NEW: Enable visualization as soon as file is selected
            if hasattr(self.parent, 'video_viz_panel'):
                self.parent.video_viz_panel.set_audio_file(file_path)
    
    def analyze_audio(self):
        file_path = self.file_path_label.text()
        self.parent.analyze_audio(file_path)
    
    def copy_to_clipboard(self):
        description = self.description_text.toPlainText()
        if description:
            clipboard = QApplication.clipboard()
            clipboard.setText(description)


class VisualizationPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Matplotlib canvas for visualizations
        self.canvas = MatplotlibCanvas(self)
        
        # Buttons for different visualizations
        button_layout = QHBoxLayout()
        
        spectrum_button = QPushButton("Spectrum")
        spectrum_button.clicked.connect(lambda: self.show_spectrum(self.parent.current_audio, self.parent.analyzer.sample_rate))
        
        melbands_button = QPushButton("Mel Bands")
        melbands_button.clicked.connect(lambda: self.show_melbands(self.parent.current_audio, self.parent.analyzer.sample_rate))
        
        mfcc_button = QPushButton("MFCC")
        mfcc_button.clicked.connect(lambda: self.show_mfcc(self.parent.current_audio, self.parent.analyzer.sample_rate))
        
        button_layout.addWidget(spectrum_button)
        button_layout.addWidget(melbands_button)
        button_layout.addWidget(mfcc_button)
        
        # Add widgets to layout
        layout.addWidget(self.canvas)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def show_spectrum(self, audio, sample_rate):
        if audio is None:
            return
            
        try:
            # Ensure audio has even length
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
    
    def show_melbands(self, audio, sample_rate):
        if audio is None:
            return
            
        try:
            # Ensure audio has even length
            if len(audio) % 2 != 0:
                audio = audio[:-1]
                
            # Calculate Nyquist frequency and set high bound safely
            nyquist_freq = sample_rate / 2
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
    
    def show_mfcc(self, audio, sample_rate):
        if audio is None:
            return
            
        try:
            # Ensure audio has even length
            if len(audio) % 2 != 0:
                audio = audio[:-1]
                
            # Calculate Nyquist frequency and set high bound safely
            nyquist_freq = sample_rate / 2
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


# NEW: Video Visualization Thread
class VisualizationThread(QThread):
    """Thread for generating visualizations without blocking UI"""
    progress = pyqtSignal(str)  # Progress messages
    finished = pyqtSignal(str)  # Completion message with file path
    error = pyqtSignal(str)     # Error messages
    
    def __init__(self, audio_file, output_file, duration, fps, style):
        super().__init__()
        self.audio_file = audio_file
        self.output_file = output_file  
        self.duration = duration
        self.fps = fps
        self.style = style
    
    def run(self):
        try:
            from ..visualizer import VisualizationGenerator
            
            self.progress.emit("Initializing visualization generator...")
            generator = VisualizationGenerator()
            
            self.progress.emit("Processing audio and generating frames...")
            result = generator.create_visualization_video(
                self.audio_file,
                self.output_file,
                self.duration,
                self.fps,
                self.style
            )
            
            if result:
                self.finished.emit(f"Visualization saved: {result}")
            else:
                self.error.emit("Failed to generate visualization")
                
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")


# NEW: Video Visualization Control Panel
class VideoVisualizationPanel(QWidget):
    """
    Panel for generating video visualizations
    Integrates with your existing AudioAnalyzer
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_audio_file = None
        self.visualization_thread = None
        self.init_ui()
    
    def init_ui(self):
        """Setup the visualization UI elements"""
        layout = QVBoxLayout()
        
        # Create group box for video visualization
        viz_group = QGroupBox("Video Visualization")
        viz_layout = QVBoxLayout()
        
        # Settings layout
        settings_layout = QHBoxLayout()
        
        # Duration setting
        settings_layout.addWidget(QLabel("Duration (s):"))
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(5.0, 60.0)
        self.duration_spin.setValue(10.0)
        self.duration_spin.setSingleStep(1.0)
        settings_layout.addWidget(self.duration_spin)
        
        # FPS setting
        settings_layout.addWidget(QLabel("FPS:"))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(['15', '20', '24', '30'])
        self.fps_combo.setCurrentText('24')
        settings_layout.addWidget(self.fps_combo)
        
        # Style setting
        settings_layout.addWidget(QLabel("Style:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(['mixed', 'mandala', 'sacred_geometry', 'kaleidoscope'])
        settings_layout.addWidget(self.style_combo)
        
        viz_layout.addLayout(settings_layout)
        
        # Generate button
        self.generate_btn = QPushButton("Generate Visualization")
        self.generate_btn.clicked.connect(self.generate_visualization)
        self.generate_btn.setEnabled(False)  # Disabled until audio is loaded
        viz_layout.addWidget(self.generate_btn)
        
        # Status label
        self.status_label = QLabel("Load an audio file to enable visualization")
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        viz_layout.addWidget(self.status_label)
        
        viz_group.setLayout(viz_layout)
        layout.addWidget(viz_group)
        self.setLayout(layout)
    
    def set_audio_file(self, audio_file_path):
        """Called when an audio file is selected (no analysis required)"""
        self.current_audio_file = audio_file_path
        self.generate_btn.setEnabled(True)
        self.status_label.setText(f"Ready to visualize: {os.path.basename(audio_file_path)}")
        self.status_label.setStyleSheet("color: green;")
    
    def clear_audio_file(self):
        """Called when audio file is cleared"""
        self.current_audio_file = None
        self.generate_btn.setEnabled(False)
        self.status_label.setText("Load an audio file to enable visualization")
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
    
    def generate_visualization(self):
        """Generate the visualization"""
        if not self.current_audio_file:
            self.status_label.setText("No audio file loaded")
            self.status_label.setStyleSheet("color: red;")
            return
        
        # Get settings
        duration = self.duration_spin.value()
        fps = int(self.fps_combo.currentText())
        style = self.style_combo.currentText()
        
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(self.current_audio_file))[0]
        output_file = f"{base_name}_visualization.mp4"
        
        # Disable button during processing
        self.generate_btn.setEnabled(False)
        self.status_label.setText("Generating visualization...")
        self.status_label.setStyleSheet("color: blue;")
        
        # Start visualization in separate thread
        self.visualization_thread = VisualizationThread(
            self.current_audio_file,
            output_file,
            duration,
            fps,
            style
        )
        
        # Connect signals
        self.visualization_thread.progress.connect(self.on_progress)
        self.visualization_thread.finished.connect(self.on_finished)
        self.visualization_thread.error.connect(self.on_error)
        
        # Start the thread
        self.visualization_thread.start()
    
    def on_progress(self, message):
        """Handle progress updates"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: blue;")
    
    def on_finished(self, message):
        """Handle completion"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: green;")
        self.generate_btn.setEnabled(True)
        self.visualization_thread = None
    
    def on_error(self, error_message):
        """Handle errors"""
        self.status_label.setText(f"Error: {error_message}")
        self.status_label.setStyleSheet("color: red;")
        self.generate_btn.setEnabled(True)
        self.visualization_thread = None
