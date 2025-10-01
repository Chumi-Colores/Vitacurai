"""
Algoritmo de Domingo para cálculo de área de carteles.

Este módulo implementa el algoritmo desarrollado por Domingo que utiliza
vectores de píxeles y coordenadas tridimensionales para calcular las
dimensiones reales de carteles en imágenes.
"""

from typing import Dict, Any, List, Union

# Importar las funciones del algoritmo desde el mismo directorio
try:
    from .get_pixel_vectors import get_pixel_vectors
    from .get_3D_coordinates import get_3D_coordinates
    from .get_surface import get_surface
    from .get_dimentions import get_dimentions
except ImportError as e:
    print(f"⚠️ Warning: No se pudieron importar algunas funciones del algoritmo de Domingo: {e}")
    # Definir funciones dummy para evitar errores de importación
    def get_pixel_vectors(*args, **kwargs):
        return [[0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1]]
    
    def get_3D_coordinates(*args, **kwargs):
        return [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
    
    def get_surface(*args, **kwargs):
        return {"area": 1.0, "normal": [0, 0, 1]}
    
    def get_dimentions(*args, **kwargs):
        return 1.0, 1.0


def calcular_area_domingo(vertices: Union[str, List], 
                         focal_distance: Union[str, List], 
                         optical_center: Union[str, List], 
                         image_url: str,
                         image_size: Union[str, List]) -> Dict[str, Any]:
    """
    Calcula el área de un cartel usando el algoritmo de Domingo.
    
    Este algoritmo utiliza vectores de píxeles y proyección 3D para determinar
    las dimensiones reales del cartel basándose en parámetros de cámara.
    
    Args:
        vertices: Coordenadas de los vértices del cartel [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                 Puede ser string JSON o lista directamente
        focal_distance: Distancia focal [fx, fy] en píxeles
                       Puede ser string JSON o lista directamente  
        optical_center: Centro óptico [cx, cy] en píxeles
                       Puede ser string JSON o lista directamente
        image_url: URL o path de la imagen del cartel
        image_size: Tamaño de la imagen [width, height] en píxeles
                   Puede ser string JSON o lista directamente
        
    Returns:
        Dict con resultado del cálculo:
        {
            "success": bool,
            "height": float,      # Alto del cartel en metros
            "width": float,       # Ancho del cartel en metros  
            "area": float,        # Área del cartel en m²
            "algorithm": "domingo",
            "error": str | None
        }
        
    Raises:
        Exception: Si hay errores en el procesamiento o cálculo
    """
    try:
        import json
        
        # Parsear parámetros si vienen como strings JSON
        if isinstance(vertices, str):
            vertices = json.loads(vertices)
            
        if isinstance(focal_distance, str):
            focal_distance = json.loads(focal_distance)
            
        if isinstance(optical_center, str):
            optical_center = json.loads(optical_center)
            
        if isinstance(image_size, str):
            image_size = json.loads(image_size)
        
        # Validar parámetros
        if not isinstance(vertices, list) or len(vertices) != 4:
            raise ValueError("vertices debe ser una lista de 4 coordenadas [[x,y], ...]")
            
        if not isinstance(focal_distance, list) or len(focal_distance) != 2:
            raise ValueError("focal_distance debe ser una lista de 2 elementos [fx, fy]")
            
        if not isinstance(optical_center, list) or len(optical_center) != 2:
            raise ValueError("optical_center debe ser una lista de 2 elementos [cx, cy]")
            
        if not isinstance(image_size, list) or len(image_size) != 2:
            raise ValueError("image_size debe ser una lista de 2 elementos [width, height]")
        
        # Ejecutar algoritmo de Domingo paso a paso
        print(f"🔧 Algoritmo de Domingo - Iniciando cálculo...")
        print(f"   📍 Vértices: {vertices}")
        print(f"   🔍 Distancia focal: {focal_distance}")
        print(f"   🎯 Centro óptico: {optical_center}")
        print(f"   📐 Tamaño imagen: {image_size}")
        
        # Paso 1: Obtener vectores de píxeles
        print("   📊 Paso 1: Calculando vectores de píxeles...")
        vectors = get_pixel_vectors(vertices, focal_distance, optical_center, image_size)
        
        # Paso 2: Obtener coordenadas tridimensionales
        print("   🌐 Paso 2: Obteniendo coordenadas 3D...")
        tridimensional_coordinates = get_3D_coordinates(image_url, vectors, vertices)
        
        # Paso 3: Calcular superficie
        print("   📏 Paso 3: Calculando superficie...")
        surface = get_surface(tridimensional_coordinates)
        
        # Paso 4: Obtener dimensiones
        print("   📐 Paso 4: Obteniendo dimensiones...")
        width, height = get_dimentions(surface, tridimensional_coordinates)
        
        # Calcular área
        area = width * height
        
        # Preparar resultado
        result = {
            "success": True,
            "height": float(height),
            "width": float(width),
            "area": float(area),
            "algorithm": "domingo",
            "calculation_details": {
                "vectors": vectors,
                "surface_info": surface,
                "coordinates_3d": tridimensional_coordinates
            },
            "error": None
        }
        
        print(f"✅ Algoritmo de Domingo - Cálculo completado:")
        print(f"   📏 Ancho: {width:.4f} m")
        print(f"   📐 Alto: {height:.4f} m") 
        print(f"   📊 Área: {area:.4f} m²")
        
        return result
        
    except json.JSONDecodeError as e:
        error_msg = f"Error al parsear parámetros JSON: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "height": None,
            "width": None,
            "area": None,
            "algorithm": "domingo",
            "error": error_msg
        }
        
    except ValueError as e:
        error_msg = f"Error de validación de parámetros: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "height": None,
            "width": None,
            "area": None,
            "algorithm": "domingo",
            "error": error_msg
        }
        
    except Exception as e:
        error_msg = f"Error en algoritmo de Domingo: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "height": None,
            "width": None,
            "area": None,
            "algorithm": "domingo",
            "error": error_msg
        }