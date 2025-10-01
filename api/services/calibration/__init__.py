"""
Módulo de servicios de calibración de cámara.

Contiene toda la lógica especializada para calibración de cámara,
incluyendo procesamiento de imágenes y cálculo de parámetros intrínsecos.
"""

from .calibration_service import CalibrationService

__all__ = ['CalibrationService']