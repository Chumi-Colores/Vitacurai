"""
Paquete de servicios de la API Vitacurai.

Este paquete contiene toda la lógica de negocio organizada por funcionalidad:
- calibration: Servicios relacionados con calibración de cámara
- area_calculation: Servicios de cálculo de área (futuro)
"""

from typing import List, Dict, Any
from fastapi import UploadFile

from .calibration import CalibrationService
from .area import AreaCalculationService


class Services:
    """
    Orquestador principal de servicios.
    
    Esta clase actúa como punto de entrada único para todos los servicios,
    derivando las solicitudes a los servicios especializados correspondientes.
    """
    
    def __init__(self):
        """Inicializa el orquestador de servicios."""
        self.calibration_service = CalibrationService()
        self.area_calculation_service = AreaCalculationService()
    
    async def calibrate_camera(self, 
                             image_files: List[UploadFile],
                             pattern_size: tuple = (8, 5),
                             square_size_mm: float = 26.5) -> Dict[str, Any]:
        """
        Deriva la solicitud de calibración al servicio especializado.
        
        Args:
            image_files: Lista de archivos de imagen subidos
            pattern_size: Tamaño del patrón del tablero (cols, rows)
            square_size_mm: Tamaño del cuadrado en milímetros
            
        Returns:
            Diccionario JSON con resultado de calibración
        """
        return await self.calibration_service.calibrate_camera(
            image_files=image_files,
            pattern_size=pattern_size,
            square_size_mm=square_size_mm
        )
    
    def validate_calibration_parameters(self, 
                                      pattern_size: tuple,
                                      square_size_mm: float) -> Dict[str, Any]:
        """
        Deriva la validación de parámetros al servicio especializado.
        
        Args:
            pattern_size: Tamaño del patrón
            square_size_mm: Tamaño del cuadrado
            
        Returns:
            Diccionario con resultado de validación
        """
        return self.calibration_service.validate_calibration_parameters(
            pattern_size=pattern_size,
            square_size_mm=square_size_mm
        )
    
    async def calculate_area(self, 
                           image_file: UploadFile,
                           vertices: List[List[float]],
                           physical_distance: float,
                           focal_length: List[float],
                           optical_center: List[float],
                           distortion_coefs: List[float]) -> Dict[str, Any]:
        """
        Deriva la solicitud de cálculo de área al servicio especializado.
        
        Args:
            image_file: Archivo de imagen del cartel
            vertices: Coordenadas de los vértices del cartel
            physical_distance: Distancia física de la cámara al cartel en metros
            focal_length: Distancia focal [fx, fy] en píxeles
            optical_center: Centro óptico [cx, cy] en píxeles
            distortion_coefs: Coeficientes de distorsión [k1, k2, p1, p2, k3]
            
        Returns:
            Diccionario JSON con resultado del cálculo de área
        """
        # Leer los datos de la imagen
        image_bytes = await image_file.read()
        
        # Llamar al servicio con los datos de la imagen
        return self.area_calculation_service.calculate_cartel_area(
            image_data=image_bytes,
            vertices=vertices,
            physical_distance=physical_distance,
            focal_length=tuple(focal_length),
            optical_center=tuple(optical_center),
            distortion_coefs=distortion_coefs
        )


# Instancia singleton del orquestador de servicios
services = Services()

__version__ = "1.0.0"
__all__ = ['Services', 'services']