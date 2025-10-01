"""
Controladores para manejar las requests HTTP de los endpoints de la API.
"""

from fastapi import HTTPException, UploadFile, File, Depends, Form
from typing import List
import datetime

from .models import CalibrationRequest, CalibrationResponse, HealthResponse, AreaCalculationRequest, AreaCalculationResponse
from .services import services


class CalibrationController:
    """
    Controlador para endpoints relacionados con calibración de cámara.
    """
    
    def __init__(self):
        """Inicializa el controlador."""
        pass
    
    async def calibrate_camera(self, 
                             images: List[UploadFile] = File(...),
                             request: CalibrationRequest = Depends()) -> CalibrationResponse:
        """
        Endpoint para calibrar cámara usando imágenes de tablero de ajedrez.
        
        Args:
            images: Lista de archivos de imagen subidos
            request: Parámetros de calibración (pattern_size, square_size_mm)
            
        Returns:
            CalibrationResponse con parámetros de calibración
            
        Raises:
            HTTPException: Si hay errores en validación o procesamiento
        """
        try:
            # Validar tipos de archivo
            for image in images:
                if not image.content_type.startswith('image/'):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Archivo {image.filename} no es una imagen válida"
                    )
            
            # Validar parámetros de entrada
            validation_result = services.validate_calibration_parameters(
                pattern_size=tuple(request.pattern_size),
                square_size_mm=request.square_size_mm
            )
            
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=400,
                    detail=validation_result["error"]
                )
            
            # Realizar calibración usando el orquestador de servicios
            result = await services.calibrate_camera(
                image_files=images,
                pattern_size=tuple(request.pattern_size),
                square_size_mm=request.square_size_mm
            )
            
            # Convertir resultado a modelo Pydantic
            return CalibrationResponse(**result)
            
        except HTTPException:
            # Re-lanzar HTTPExceptions
            raise
        except Exception as e:
            # Capturar cualquier otro error no manejado
            raise HTTPException(
                status_code=500,
                detail=f"Error interno del servidor: {str(e)}"
            )


class HealthController:
    """
    Controlador para endpoints de health check.
    """
    
    def get_health_status(self) -> HealthResponse:
        """
        Endpoint de health check para verificar que el servicio está funcionando.
        
        Returns:
            HealthResponse con estado del servicio
        """
        return HealthResponse(
            status="healthy",
            message="Vitacurai API funcionando correctamente",
            timestamp=datetime.datetime.now().isoformat()
        )


class AreaController:
    """
    Controlador para endpoints de cálculo de área de carteles.
    """
    
    def __init__(self):
        """Inicializa el controlador."""
        pass
    
    async def calculate_area(self, 
                           image: UploadFile = File(...),
                           vertices_str: str = Form(...),
                           physical_distance: float = Form(...),
                           focal_length_str: str = Form(...),
                           optical_center_str: str = Form(...),
                           distortion_coefs_str: str = Form(...)) -> AreaCalculationResponse:
        """
        Endpoint para calcular el área de un cartel usando una imagen y coordenadas de vértices.
        
        Args:
            image: Archivo de imagen del cartel
            vertices_str: Coordenadas de los vértices como string JSON [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            physical_distance: Distancia física de la cámara al cartel en metros
            focal_length_str: Distancia focal como string JSON [fx, fy]
            optical_center_str: Centro óptico como string JSON [cx, cy]
            distortion_coefs_str: Coeficientes de distorsión como string JSON [k1, k2, p1, p2, k3]
            
        Returns:
            AreaCalculationResponse con área calculada y métricas de calidad
            
        Raises:
            HTTPException: Si hay errores en validación o procesamiento
        """
        try:
            import json
            
            # Validar tipo de archivo
            if not image.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail=f"Archivo {image.filename} no es una imagen válida"
                )
            
            # Parsear parámetros JSON
            try:
                vertices = json.loads(vertices_str)
                focal_length = json.loads(focal_length_str)
                optical_center = json.loads(optical_center_str)
                distortion_coefs = json.loads(distortion_coefs_str)
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error al parsear parámetros JSON: {str(e)}"
                )
            
            # Validar parámetros de entrada básicos
            if not isinstance(vertices, list) or len(vertices) != 4:
                raise HTTPException(
                    status_code=400,
                    detail="Se requieren exactamente 4 vértices para el cálculo"
                )
            
            if not isinstance(focal_length, list) or len(focal_length) != 2:
                raise HTTPException(
                    status_code=400,
                    detail="focal_length debe tener exactamente 2 valores [fx, fy]"
                )
            
            if not isinstance(optical_center, list) or len(optical_center) != 2:
                raise HTTPException(
                    status_code=400,
                    detail="optical_center debe tener exactamente 2 valores [cx, cy]"
                )
            
            if not isinstance(distortion_coefs, list) or len(distortion_coefs) != 5:
                raise HTTPException(
                    status_code=400,
                    detail="distortion_coefs debe tener exactamente 5 valores [k1, k2, p1, p2, k3]"
                )
            
            # Realizar cálculo de área usando el orquestador de servicios
            result = await services.calculate_area(
                image_file=image,
                vertices=vertices,
                physical_distance=physical_distance,
                focal_length=focal_length,
                optical_center=optical_center,
                distortion_coefs=distortion_coefs
            )
            
            # Convertir resultado a modelo Pydantic
            return AreaCalculationResponse(**result)
            
        except HTTPException:
            # Re-lanzar HTTPExceptions
            raise
        except Exception as e:
            # Capturar cualquier otro error no manejado
            raise HTTPException(
                status_code=500,
                detail=f"Error interno del servidor: {str(e)}"
            )