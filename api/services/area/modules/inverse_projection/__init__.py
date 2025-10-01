"""
Módulo de proyección inversa 2D a 3D.

Este módulo permite convertir coordenadas de píxeles en imágenes 
a coordenadas 3D reales usando parámetros de cámara calibrada.
"""

from .inverse_projector import InverseProjector, project_pixels_to_3d

__all__ = [
    'InverseProjector',
    'project_pixels_to_3d'
]