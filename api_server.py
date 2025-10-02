"""
Servidor principal de la API Vitacurai.

Este módulo configura y ejecuta el servidor FastAPI con todos los endpoints.
"""

from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import uvicorn

from api.models import CalibrationRequest, CalibrationResponse, HealthResponse, AreaCalculationRequest, AreaCalculationResponse
from api.controllers import CalibrationController, HealthController, AreaController

# Algoritmo de Domingo
from api.algoritmo_domingo import calcular_area_domingo

# Crear instancia de FastAPI
app = FastAPI(
    title="Vitacurai API",
    description="API para calibración de cámara y cálculo de dimensiones de carteles publicitarios",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar controladores
calibration_controller = CalibrationController()
health_controller = HealthController()
area_controller = AreaController()


# ============================================
# ENDPOINTS DE HEALTH CHECK
# ============================================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Endpoint de verificación de salud del servicio.
    
    Returns:
        HealthResponse: Estado actual del servicio
    """
    return health_controller.get_health_status()


@app.get("/", tags=["Info"])
async def root():
    """
    Endpoint raíz con información básica de la API.
    
    Returns:
        dict: Información básica sobre la API y endpoints disponibles
    """
    return {
        "message": "Vitacurai API - Calibración de cámara y cálculo de dimensiones",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "calibration": "/calibrar",
            "area_calculation": "/calcular_area",
            "health": "/health",
            "docs": "/docs"
        }
    }


# ============================================
# ENDPOINTS DE CALIBRACIÓN
# ============================================

@app.post("/calibrar", response_model=CalibrationResponse, tags=["Calibración"])
async def calibrate_camera(
    images: List[UploadFile] = File(..., description="Lista de imágenes JPG/PNG del tablero de ajedrez (mínimo 5, recomendado 10-20)"),
    pattern_size_cols: int = Form(8, description="Número de esquinas internas en columnas"),
    pattern_size_rows: int = Form(5, description="Número de esquinas internas en filas"),
    square_size_mm: float = Form(26.5, description="Tamaño real de cada cuadrado en milímetros")
):
    """
    Calibra una cámara usando imágenes de un tablero de ajedrez.
    
    **Parámetros:**
    - **images**: Lista de imágenes JPG/PNG del tablero de ajedrez (mínimo 5, recomendado 10-20)
    - **pattern_size_cols**: Número de esquinas internas en columnas (default: 8)
    - **pattern_size_rows**: Número de esquinas internas en filas (default: 5) 
    - **square_size_mm**: Tamaño real de cada cuadrado en milímetros (default: 26.5)
    
    **Respuesta exitosa incluye:**
    - Matriz intrínseca de cámara (camera_matrix)
    - Coeficientes de distorsión (dist_coefs)
    - Error RMS de calibración
    - Distancia focal (fx, fy)
    - Centro óptico (cx, cy)
    - Métricas de calidad
    - Metadatos del proceso
    """
    try:
        # Crear objeto request con los parámetros
        calibration_request = CalibrationRequest(
            pattern_size=[pattern_size_cols, pattern_size_rows],
            square_size_mm=square_size_mm
        )
        
        # Llamar al controlador
        result = await calibration_controller.calibrate_camera(
            images=images,
            request=calibration_request
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


# ============================================
# ENDPOINTS DE CÁLCULO DE ÁREA
# ============================================

@app.post("/calcular_area", response_model=AreaCalculationResponse, tags=["Área"])
async def calculate_area(
    image: UploadFile = File(..., description="Imagen del cartel (JPG/PNG)"),
    vertices: List[List[int]] = Form(..., description="Coordenadas de 4 vértices como JSON [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]"),
    focal_distance: List[float] = Form(..., description="Distancia focal como JSON [fx, fy] en píxeles"),
    optical_center: List[float] = Form(..., description="Centro óptico como JSON [cx, cy] en píxeles"),
    distortion_coefs: List[float] = Form(..., description="Coeficientes de distorsión como JSON [k1, k2, p1, p2, k3]"),
    image_url: str = Form("", description="URL de la imagen (opcional)"),
    image_size: str = Form("", description="Tamaño de la imagen como JSON [width, height] (se calcula automáticamente si no se proporciona)")
):
    """
    Calcula las dimensiones y área de un cartel rectangular usando una imagen y coordenadas de vértices.
    
    **Parámetros:**
    - **image**: Imagen del cartel (JPG/PNG)
    - **vertices**: Coordenadas de 4 vértices como JSON [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    - **focal_distance**: Distancia focal como JSON [fx, fy] en píxeles
    - **optical_center**: Centro óptico como JSON [cx, cy] en píxeles  
    - **distortion_coefs**: Coeficientes de distorsión como JSON [k1, k2, p1, p2, k3]
    
    **Respuesta exitosa incluye:**
    - Área del cartel en metros cuadrados
    - Ancho y alto del cartel en metros
    - Métricas de calidad de la medición
    - Ratios de lados paralelos
    - Ángulos promedio y desviación estándar
    - Observaciones sobre la calidad
    - Información detallada del cálculo
    """
    try:
        # Validar que todos los parámetros requeridos estén presentes
        if not all([vertices, focal_distance, optical_center, distortion_coefs]):
            raise HTTPException(
                status_code=400,
                detail="Faltan parámetros requeridos: vertices, focal_distance, optical_center, distortion_coefs"
            )
        
        # Si no se proporciona image_size, calcular desde la imagen
        if not image_size:
            # Aquí podrías leer la imagen y obtener sus dimensiones
            # Por ahora usamos valores por defecto o dejamos que el algoritmo lo maneje
            image_size = "[]"  # El algoritmo de Domingo manejará esto
        
        # Si no se proporciona image_url, usar la imagen subida
        if not image_url:
            # Aquí podrías guardar la imagen temporalmente y crear una URL
            # Por ahora dejamos que el algoritmo maneje la imagen directamente
            image_url = f"uploaded_image_{image.filename}"

        # Usar algoritmo de Domingo
        resultDomingo = calcular_area_domingo(
            vertices=vertices,
            focal_distance=focal_distance,
            optical_center=optical_center,
            image_url=image_url,
            image_size=image_size
        )

        # resultMartin = await area_controller.calculate_area(
        #     image=image,
        #     vertices_str=vertices,
        #     image_size=image_size,
        #     focal_length_str=focal_distance,
        #     optical_center_str=optical_center,
        #     distortion_coefs_str=distortion_coefs
        # )

        return resultDomingo

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


# ============================================
# MANEJO GLOBAL DE ERRORES
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejo personalizado de HTTPExceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Manejo de excepciones generales no capturadas."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Error interno del servidor",
            "detail": str(exc),
            "status_code": 500
        }
    )


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def main():
    """
    Función principal para ejecutar el servidor.
    """
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload en desarrollo
        log_level="info"
    )


if __name__ == "__main__":
    main()
