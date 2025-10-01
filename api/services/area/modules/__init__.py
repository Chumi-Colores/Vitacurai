"""
Módulos de cálculo de área - Autocontenidos dentro de la API.

Este paquete contiene todos los módulos necesarios para:
1. Preprocesamiento de imágenes y detección de contornos
2. Proyección inversa 2D → 3D 
3. Cálculo geométrico de áreas
"""

from . import image_preprocessing
from . import inverse_projection
from . import geometric_calculation

__all__ = [
    'image_preprocessing',
    'inverse_projection', 
    'geometric_calculation'
]