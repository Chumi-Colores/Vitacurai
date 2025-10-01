"""
Módulos de calibración de cámara - Autocontenidos dentro de la API.

Este paquete contiene todos los módulos necesarios para la calibración de cámara:
1. Preprocesamiento de imágenes de tablero de ajedrez
2. Calibración de parámetros intrínsecos de cámara
3. API simplificada para calibración desde imágenes o directorios
"""

from .calibration_api_module import (
    calibrate_from_images,
    calibrate_from_directory,
    save_calibration_json,
    quick_calibration
)
from .chessboard_preprocessing import ChessboardPreprocessor, extract_calibration_parameters
from .camera_calibrator import CameraCalibrator, load_calibration_parameters

__all__ = [
    'calibrate_from_images',
    'calibrate_from_directory',
    'save_calibration_json',
    'quick_calibration',
    'ChessboardPreprocessor',
    'extract_calibration_parameters',
    'CameraCalibrator',
    'load_calibration_parameters'
]