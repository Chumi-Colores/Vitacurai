"""
Módulo de proyección inversa 2D a 3D.

Este módulo contiene:
- InverseProjector: Conversión de coordenadas de píxeles a coordenadas 3D reales
"""

from .inverse_projector import InverseProjector, project_pixels_to_3d

__all__ = [
    'InverseProjector',
    'project_pixels_to_3d'
]