# Make the analyzer module a package
# This allows imports like: from analyzer import AudioAnalyzer

from .audio_analyzer import AudioAnalyzer

__all__ = ['AudioAnalyzer']