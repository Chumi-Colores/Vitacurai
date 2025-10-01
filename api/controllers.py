"""
Controladores para manejar las requests HTTP de los endpoints de la API.
"""

from fastapi import HTTPException, UploadFile, File, Depends
from typing import List
import datetime

from .models import CalibrationRequest, CalibrationResponse, HealthResponse
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
    Controlador para endpoints de cálculo de área (implementación futura).
    """
    
    def __init__(self):
        """Inicializa el controlador (implementación futura)."""
        pass
    
    # TODO: Implementar calculate_area method cuando se requiera