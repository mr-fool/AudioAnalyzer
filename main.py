import sys
import essentia
from PyQt5.QtWidgets import QApplication

from analyzer.audio_analyzer import AudioAnalyzer
from analyzer.ui.app import AudioAnalyzerApp

def main():
    # Print Essentia version
    print(f"Using Essentia version: {essentia.__version__}")
    
    # Create the application
    app = QApplication(sys.argv)
    
    # Create the analyzer
    analyzer = AudioAnalyzer()
    
    # Create and show the main window
    window = AudioAnalyzerApp(analyzer)
    window.show()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()