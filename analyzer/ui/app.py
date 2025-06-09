import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QSplitter)
from PyQt5.QtCore import Qt, pyqtSlot
import essentia.standard as es

from .panels import ControlPanel, VisualizationPanel, VideoVisualizationPanel
from ..utils.helpers import AnalyzerThread

class AudioAnalyzerApp(QMainWindow):
    def __init__(self, analyzer):
        super().__init__()
        self.analyzer = analyzer
        self.current_audio = None
        self.current_file_path = None  # NEW: Track current file path
        self.results = None
        self.setWindowTitle("Audio Analyzer for LLM")
        self.setGeometry(100, 100, 1100, 700)  # Made slightly larger for new panel
        self.init_ui()
        
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Create panels
        self.control_panel = ControlPanel(self)
        self.visualization_panel = VisualizationPanel(self)
        self.video_viz_panel = VideoVisualizationPanel(self)  # NEW: Video visualization panel
        
        # Create left panel with controls and video visualization
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.control_panel)
        left_layout.addWidget(self.video_viz_panel)  # NEW: Add video viz panel
        left_widget.setLayout(left_layout)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)  # Left side: controls + video viz
        splitter.addWidget(self.visualization_panel)  # Right side: plots
        splitter.setSizes([500, 600])  # Adjusted sizes
        
        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def analyze_audio(self, file_path):
        if file_path == "No file selected" or not os.path.exists(file_path):
            self.control_panel.results_text.setText("Please select a valid audio file first.")
            return
        
        # NEW: Store the current file path and enable visualization immediately
        self.current_file_path = file_path
        self.video_viz_panel.set_audio_file(file_path)  # Enable visualization right away
        
        self.control_panel.results_text.setText("Analyzing audio...")
        self.control_panel.description_text.setText("")
        
        self.analysis_thread = AnalyzerThread(file_path, self.analyzer)
        self.analysis_thread.analysis_complete.connect(self.update_results)
        self.analysis_thread.analysis_error.connect(self.show_error)
        self.analysis_thread.start()
    
    @pyqtSlot(dict)
    def update_results(self, results):
        self.results = results
        self.current_audio = results.get('audio')
        
        # Update results text
        result_text = f"Key: {results['key']}\n"
        result_text += f"BPM: {results['bpm']}\n"
        result_text += f"Loudness: {results['loudness']} dB\n"
        result_text += f"Dissonance: {results['dissonance']}\n\n"
        result_text += f"Detected Mood: {', '.join(results['mood'][:5])}\n\n"
        result_text += f"Detected Instruments: {', '.join(results['instruments'])}"
        
        self.control_panel.results_text.setText(result_text)
        
        # Generate description
        description = self.analyzer.generate_description()
        self.control_panel.description_text.setText(description)
        
        # Show spectrum visualization
        self.visualization_panel.show_spectrum(self.current_audio, self.analyzer.sample_rate)
        
        # NEW: Enable video visualization now that audio is analyzed
        if self.current_file_path:
            self.video_viz_panel.set_audio_file(self.current_file_path)
    
    @pyqtSlot(str)
    def show_error(self, error_msg):
        self.control_panel.results_text.setText(
            f"Error during analysis: {error_msg}\n\nPlease try a different audio file or format."
        )
        
        canvas = self.visualization_panel.canvas
        canvas.ax.clear()
        canvas.ax.text(0.5, 0.5, "Analysis failed - No visualization available", 
                      horizontalalignment='center', verticalalignment='center')
        canvas.draw()
        
        # NEW: Clear video visualization on error
        self.video_viz_panel.clear_audio_file()