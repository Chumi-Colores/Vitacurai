"""
Módulo de preprocesamiento de imágenes para medición de carteles.

Este módulo contiene:
- ContourDetector: Detección y validación de contornos rectangulares
- DistortionCorrector: Corrección de distorsión usando parámetros de calibración
"""

from .contour_detector import ContourDetector, validate_and_order_contours
from .distortion_corrector import DistortionCorrector, correct_image_and_contours

__all__ = [
    'ContourDetector',
    'DistortionCorrector', 
    'validate_and_order_contours',
    'correct_image_and_contours'
]