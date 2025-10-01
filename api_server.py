"""
Servidor principal de la API Vitacurai.

Este módulo configura y ejecuta el servidor FastAPI con todos los endpoints.
"""

from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import uvicorn

from api.models import CalibrationRequest, CalibrationResponse, HealthResponse, AreaCalculationRequest, AreaCalculationResponse
from api.controllers import CalibrationController, HealthController, AreaController


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
    images: List[UploadFile] = File(..., description="Lista de imágenes del tablero de ajedrez (mínimo 5)"),
    pattern_size_cols: int = Form(8, description="Número de columnas de esquinas internas del tablero"),
    pattern_size_rows: int = Form(5, description="Número de filas de esquinas internas del tablero"),
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
    
    **Ejemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/calibrar" \\
         -F "images=@imagen1.jpg" \\
         -F "images=@imagen2.jpg" \\
         -F "images=@imagen3.jpg" \\
         -F "pattern_size_cols=8" \\
         -F "pattern_size_rows=5" \\
         -F "square_size_mm=26.5"
    ```
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
    image: UploadFile = File(..., description="Imagen del cartel a medir (JPG/PNG)"),
    vertices: str = Form(..., description="Coordenadas de vértices como JSON: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]"),
    physical_distance: float = Form(..., description="Distancia física de la cámara al cartel en metros"),
    focal_length: str = Form(..., description="Distancia focal como JSON: [fx, fy]"),
    optical_center: str = Form(..., description="Centro óptico como JSON: [cx, cy]"),
    distortion_coefs: str = Form(..., description="Coeficientes de distorsión como JSON: [k1, k2, p1, p2, k3]")
):
    """
    Calcula las dimensiones y área de un cartel rectangular usando una imagen y coordenadas de vértices.
    
    **Parámetros:**
    - **image**: Imagen del cartel (JPG/PNG)
    - **vertices**: Coordenadas de 4 vértices como JSON [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    - **physical_distance**: Distancia física de la cámara al cartel en metros
    - **focal_length**: Distancia focal como JSON [fx, fy] en píxeles
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
    
    **Ejemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/calcular_area" \\
         -F "image=@cartel.jpg" \\
         -F "vertices=[[100, 100], [400, 120], [380, 300], [80, 280]]" \\
         -F "physical_distance=2.5" \\
         -F "focal_length=[800.0, 800.0]" \\
         -F "optical_center=[320.0, 240.0]" \\
         -F "distortion_coefs=[0.1, -0.2, 0.001, 0.002, 0.05]"
    ```
    """
    try:
        # Llamar al controlador
        result = await area_controller.calculate_area(
            image=image,
            vertices_str=vertices,
            physical_distance=physical_distance,
            focal_length_str=focal_length,
            optical_center_str=optical_center,
            distortion_coefs_str=distortion_coefs
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
