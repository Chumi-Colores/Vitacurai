"""
Modelos Pydantic para validación de requests y responses de la API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class CalibrationRequest(BaseModel):
    """
    Modelo para request de calibración de cámara.
    """
    pattern_size: List[int] = Field(
        default=[8, 5], 
        description="Tamaño del patrón del tablero [cols, rows] (esquinas internas)",
        min_length=2,
        max_length=2
    )
    square_size_mm: float = Field(
        default=26.5,
        gt=0,
        description="Tamaño real de cada cuadrado en milímetros"
    )


class CalibrationResponse(BaseModel):
    """
    Modelo para response de calibración de cámara.
    """
    success: bool = Field(description="Si la calibración fue exitosa")
    
    # Parámetros esenciales (cuando success=True)
    camera_matrix: Optional[List[List[float]]] = Field(None, description="Matriz intrínseca de cámara 3x3")
    dist_coefs: Optional[List[float]] = Field(None, description="Coeficientes de distorsión [k1, k2, p1, p2, k3]")
    rms_error: Optional[float] = Field(None, description="Error RMS de reproyección en píxeles")
    
    # Parámetros derivados
    focal_length: Optional[Dict[str, float]] = Field(None, description="Distancia focal {fx, fy}")
    optical_center: Optional[Dict[str, float]] = Field(None, description="Centro óptico {cx, cy}")
    
    # Métricas de calidad
    quality: Optional[str] = Field(None, description="Descripción textual de la calidad")
    quality_level: Optional[str] = Field(None, description="Nivel de calidad: excellent, good, acceptable, poor")
    quality_recommendation: Optional[str] = Field(None, description="Recomendación para mejora")
    
    # Metadatos
    num_images_used: Optional[int] = Field(None, description="Número de imágenes utilizadas en calibración")
    total_images_processed: Optional[int] = Field(None, description="Total de imágenes procesadas")
    successful_images: Optional[int] = Field(None, description="Imágenes procesadas exitosamente")
    image_size: Optional[Dict[str, int]] = Field(None, description="Tamaño de imagen {width, height}")
    
    # Configuración
    calibration_config: Optional[Dict[str, Any]] = Field(None, description="Configuración usada en calibración")
    
    # Error info (cuando success=False)
    error: Optional[str] = Field(None, description="Mensaje de error si la calibración falló")


class AreaCalculationRequest(BaseModel):
    """
    Modelo para request de cálculo de área (para implementación futura).
    """
    image_url: str = Field(description="URL de la imagen del cartel")
    vertices: List[List[float]] = Field(
        description="Coordenadas de los vértices del cartel [[x1,y1], [x2,y2], ...]",
        min_length=4
    )
    focal_distance: float = Field(gt=0, description="Distancia focal en píxeles")


class AreaCalculationResponse(BaseModel):
    """
    Modelo para response de cálculo de área (para implementación futura).
    """
    success: bool = Field(description="Si el cálculo fue exitoso")
    width: Optional[float] = Field(None, description="Ancho del cartel")
    height: Optional[float] = Field(None, description="Alto del cartel") 
    units: str = Field(default="cm", description="Unidades de medición")
    error: Optional[str] = Field(None, description="Mensaje de error si el cálculo falló")


class HealthResponse(BaseModel):
    """
    Modelo para response del health check.
    """
    status: str = Field(description="Estado del servicio")
    message: str = Field(description="Mensaje descriptivo")
    timestamp: str = Field(description="Timestamp del health check")