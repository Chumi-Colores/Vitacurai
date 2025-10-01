"""
Servidor principal de la API Vitacurai.

Este módulo configura y ejecuta el servidor FastAPI con todos los endpoints.
"""

from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import uvicorn

from api.models import CalibrationRequest, CalibrationResponse, HealthResponse
from api.controllers import CalibrationController, HealthController


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
            "area_calculation": "/calcular_area (próximamente)",
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
# ENDPOINTS DE CÁLCULO DE ÁREA (PLACEHOLDER)
# ============================================

@app.post("/calcular_area", tags=["Área"])
async def calculate_area():
    """
    Calcula las dimensiones de un cartel rectangular en una imagen.
    
    **NOTA:** Este endpoint será implementado en la siguiente fase del proyecto.
    
    **Funcionalidad planeada:**
    - Recibir imagen de un cartel publicitario
    - Recibir coordenadas de los vértices del cartel  
    - Usar parámetros de calibración para calcular dimensiones reales
    - Retornar ancho y alto del cartel en centímetros
    """
    return {
        "message": "Endpoint de cálculo de área",
        "status": "En desarrollo",
        "description": "Este endpoint será implementado en la siguiente fase del proyecto"
    }


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
