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
    Modelo para request de cálculo de área de cartel.
    """
    vertices: List[List[float]] = Field(
        description="Coordenadas de los vértices del cartel [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]",
        min_length=4,
        max_length=4
    )
    physical_distance: float = Field(
        gt=0,
        description="Distancia física de la cámara al cartel en metros"
    )
    focal_length: List[float] = Field(
        description="Distancia focal [fx, fy] en píxeles",
        min_length=2,
        max_length=2
    )
    optical_center: List[float] = Field(
        description="Centro óptico [cx, cy] en píxeles",
        min_length=2,
        max_length=2
    )
    distortion_coefs: List[float] = Field(
        description="Coeficientes de distorsión [k1, k2, p1, p2, k3]",
        min_length=5,
        max_length=5
    )


class AreaCalculationResponse(BaseModel):
    """
    Modelo para response de cálculo de área de cartel.
    """
    success: bool = Field(description="Si el cálculo fue exitoso")
    
    # Resultados principales (cuando success=True)
    area_square_meters: Optional[float] = Field(None, description="Área del cartel en metros cuadrados")
    width_meters: Optional[float] = Field(None, description="Ancho del cartel en metros")
    height_meters: Optional[float] = Field(None, description="Alto del cartel en metros")
    
    # Métricas de calidad
    parallel_sides_ratios: Optional[Dict[str, float]] = Field(None, description="Ratios de lados paralelos")
    average_angles: Optional[Dict[str, float]] = Field(None, description="Ángulos promedio y desviación")
    quality: Optional[Dict[str, Any]] = Field(None, description="Información de calidad de la medición")
    observations: Optional[List[str]] = Field(None, description="Observaciones sobre la medición")
    
    # Información del cálculo
    calculation_info: Optional[Dict[str, Any]] = Field(None, description="Información detallada del cálculo")
    
    # Error info (cuando success=False)
    error: Optional[str] = Field(None, description="Mensaje de error si el cálculo falló")


class HealthResponse(BaseModel):
    """
    Modelo para response del health check.
    """
    status: str = Field(description="Estado del servicio")
    message: str = Field(description="Mensaje descriptivo")
    timestamp: str = Field(description="Timestamp del health check")