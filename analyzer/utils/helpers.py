from PyQt5.QtCore import QThread, pyqtSignal

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