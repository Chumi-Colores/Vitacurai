"""
Calibration Pipeline Package

Paquete modular para calibración automática de cámaras usando tablero de ajedrez.

Módulos:
- chessboard_preprocessing: Preprocesamiento de imágenes
- camera_calibrator: Calibración de cámara
- main: Módulo principal que orquesta todo el proceso
"""

from .chessboard_preprocessing import (
    ChessboardPreprocessor,
    extract_calibration_parameters
)

from .camera_calibrator import (
    CameraCalibrator,
    load_calibration_parameters
)

__version__ = "2.0.0"
__author__ = "Capstone Project"

__all__ = [
    'ChessboardPreprocessor',
    'extract_calibration_parameters',
    'CameraCalibrator',
    'load_calibration_parameters'
]