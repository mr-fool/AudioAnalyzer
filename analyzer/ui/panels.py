import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QFileDialog, QTextEdit, QGroupBox)
from PyQt5.QtGui import QClipboard
from PyQt5.QtCore import Qt
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