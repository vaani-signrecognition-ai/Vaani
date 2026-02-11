"""
Sign Language Detector - Inference Classifier

This script runs the sign language detection UI using the modular detector.
For integration into other applications, import from sign_language_detector module.

Usage:
    python inference_classifier.py
    
Or import and use programmatically:
    from sign_language_detector import SignLanguageDetector, run_detector_ui
    run_detector_ui()
"""

from sign_language_detector import run_detector_ui

if __name__ == "__main__":
    run_detector_ui()
