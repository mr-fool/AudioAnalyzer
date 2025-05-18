# Make the ui module a package
# This allows imports like: from analyzer.ui import AudioAnalyzerApp

from .app import AudioAnalyzerApp
from .canvas import MatplotlibCanvas
from .panels import ControlPanel, VisualizationPanel

__all__ = ['AudioAnalyzerApp', 'MatplotlibCanvas', 'ControlPanel', 'VisualizationPanel']