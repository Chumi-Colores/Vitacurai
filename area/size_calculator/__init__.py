"""
Sistema de Medición de Carteles Rectangulares

Este sistema utiliza calibración de cámara y geometría 3D para medir
el área real de carteles rectangulares a partir de fotografías.

Módulos principales:
- image_preprocessing: Validación de contornos y corrección de distorsión
- inverse_projection: Proyección inversa 2D → 3D 
- geometric_calculation: Cálculo de área y validación geométrica

Uso básico:
    from size_calculator.main import CartelAreaMeasurer
    
    measurer = CartelAreaMeasurer('calibration.npz')
    result = measurer.measure_cartel_area('cartel.jpg', contours, distance)
    area = result['area_square_meters']

Uso desde línea de comandos:
    python3 main.py -i cartel.jpg -c "100,50 500,60 490,300 110,290" -d 3.0
"""

from .main import CartelAreaMeasurer, parse_contours

__version__ = "1.0.0"
__author__ = "Sistema de Medición de Carteles"

__all__ = [
    'CartelAreaMeasurer',
    'parse_contours'
]