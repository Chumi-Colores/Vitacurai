"""
Módulo de cálculo geométrico de áreas.

Este módulo se encarga del cálculo de áreas de rectángulos 
en el espacio 3D con validación de calidad geométrica.
"""

from .area_calculator import AreaCalculator, calculate_rectangle_area

__all__ = [
    'AreaCalculator',
    'calculate_rectangle_area'
]