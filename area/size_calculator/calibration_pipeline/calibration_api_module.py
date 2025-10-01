"""
Módulo de API para calibración de cámara.

Este módulo provee una interfaz simplificada para realizar calibración
de cámara desde imágenes y retornar los parámetros en formato JSON.

IMPORTANTE: Este módulo solo retorna los parámetros en formato JSON.
No guarda automáticamente los archivos. Si necesitas guardar los resultados,
usa la función save_calibration_json() por separado.
"""

import json
import numpy as np
from typing import List, Dict, Any, Union, Optional
from pathlib import Path
import cv2

from chessboard_preprocessing import ChessboardPreprocessor
from camera_calibrator import CameraCalibrator


def _process_image_arrays(preprocessor: ChessboardPreprocessor, 
                         image_arrays: List[np.ndarray]) -> Dict[str, Any]:
    """
    Procesa arrays de imágenes usando el preprocesador de tablero.
    
    Args:
        preprocessor: Instancia del preprocesador configurado
        image_arrays: Lista de arrays numpy con las imágenes
        
    Returns:
        Diccionario con datos de calibración similares al preprocesador original
    """
    # Preparar listas para almacenar resultados
    objpoints = []  # Puntos 3D en el mundo real
    imgpoints = []  # Puntos 2D en la imagen
    image_paths = []  # Para compatibilidad, usaremos índices
    successful_images = 0
    
    for i, image in enumerate(image_arrays):
        try:
            # Procesar imagen individual usando el método del preprocesador
            # Crear un path temporal para compatibilidad
            temp_path = f"temp_image_{i}.jpg"
            
            # Usar el método interno del preprocesador para encontrar esquinas
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Buscar esquinas del tablero
            ret, corners = cv2.findChessboardCorners(gray, preprocessor.pattern_size, None)
            
            if ret:
                # Refinar esquinas
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                
                # Agregar puntos de objeto (3D) y puntos de imagen (2D)
                objpoints.append(preprocessor.pattern_points)
                imgpoints.append(corners2)
                image_paths.append(temp_path)
                successful_images += 1
                
        except Exception as e:
            # Continuar con la siguiente imagen en caso de error
            continue
    
    # Obtener tamaño de imagen desde la primera imagen exitosa
    image_size = None
    if image_arrays:
        h, w = image_arrays[0].shape[:2]
        image_size = (w, h)
    
    # Preparar resultado similar al preprocesador original
    result = {
        'success': successful_images > 0,
        'objpoints': objpoints,
        'imgpoints': imgpoints,
        'image_paths': image_paths,
        'pattern_size': preprocessor.pattern_size,
        'square_size': preprocessor.square_size_mm,
        'image_size': image_size,
        'successful_images': successful_images,
        'total_images': len(image_arrays)
    }
    
    if successful_images == 0:
        result['error'] = "No se pudieron detectar esquinas del tablero en ninguna imagen"
    
    return result


def calibrate_from_images(
    images: List[Union[np.ndarray, str, Path]],
    pattern_size: tuple = (8, 5),
    square_size: float = 26.5,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Realiza calibración completa de cámara desde lista de imágenes.
    
    Args:
        images: Lista de imágenes (arrays numpy, rutas de archivos, o URLs)
        pattern_size: Tamaño del patrón del tablero (esquinas internas) como (cols, rows)
        square_size: Tamaño real de cada cuadrado en milímetros
        verbose: Si mostrar mensajes de progreso
        
    Returns:
        Diccionario JSON con parámetros completos de calibración.
        NO guarda archivos automáticamente - solo retorna el resultado.
        
    Ejemplo de respuesta exitosa:
        {
            "success": true,
            "camera_matrix": [[fx, 0, cx], [0, fy, cy], [0, 0, 1]],
            "dist_coefs": [k1, k2, p1, p2, k3],
            "rms_error": 1.012,
            "focal_length": {"fx": 3074.1, "fy": 3080.8},
            "optical_center": {"cx": 1511.8, "cy": 2007.4},
            "quality": "⚠️ Aceptable (1.0 ≤ RMS < 2.0)",
            ...
        }
    """
    
    def _print(msg: str):
        """Imprime mensaje solo si verbose=True."""
        if verbose:
            print(msg)
    
    try:
        _print("🔧 Iniciando calibración desde imágenes...")
        
        # Validar entrada
        if not images:
            return {
                "success": False,
                "error": "No se proporcionaron imágenes"
            }
        
        if len(images) < 5:
            return {
                "success": False,
                "error": f"Se requieren al menos 5 imágenes, se proporcionaron {len(images)}"
            }
        
        # ============================================
        # PASO 1: PREPROCESAR IMÁGENES
        # ============================================
        _print(f"📸 Preprocesando {len(images)} imágenes...")
        
        # Convertir todas las imágenes a arrays numpy
        processed_images = []
        for i, img in enumerate(images):
            try:
                if isinstance(img, (str, Path)):
                    # Cargar desde archivo
                    img_array = cv2.imread(str(img))
                    if img_array is None:
                        _print(f"⚠️ No se pudo cargar la imagen {i+1}: {img}")
                        continue
                elif isinstance(img, np.ndarray):
                    img_array = img.copy()
                else:
                    _print(f"⚠️ Tipo de imagen no soportado en posición {i+1}: {type(img)}")
                    continue
                
                processed_images.append(img_array)
                
            except Exception as e:
                _print(f"⚠️ Error procesando imagen {i+1}: {e}")
                continue
        
        if len(processed_images) < 5:
            return {
                "success": False,
                "error": f"Solo se pudieron procesar {len(processed_images)} imágenes válidas (mínimo 5)"
            }
        
        # Crear preprocesador
        preprocessor = ChessboardPreprocessor(
            pattern_size=pattern_size,
            square_size_mm=square_size
        )
        
        # Procesar imágenes para encontrar esquinas
        calibration_data = _process_image_arrays(preprocessor, processed_images)
        
        if not calibration_data['success']:
            return {
                "success": False,
                "error": f"Error en preprocesamiento: {calibration_data.get('error', 'Error desconocido')}"
            }
        
        _print(f"✅ Preprocesamiento completado:")
        _print(f"   - Imágenes exitosas: {calibration_data['successful_images']}")
        _print(f"   - Total procesadas: {calibration_data['total_images']}")
        
        # ============================================
        # PASO 2: CALIBRAR CÁMARA
        # ============================================
        _print("🧮 Ejecutando calibración de cámara...")
        
        calibrator = CameraCalibrator(verbose=verbose)
        calibration_result = calibrator.calibrate(calibration_data)
        
        if not calibration_result['success']:
            return {
                "success": False,
                "error": f"Error en calibración: {calibration_result.get('error', 'Error desconocido')}"
            }
        
        # ============================================
        # PASO 3: FORMATEAR RESPUESTA JSON
        # ============================================
        _print("📊 Formateando resultados...")
        
        # Extraer parámetros
        camera_matrix = calibration_result['camera_matrix']
        dist_coefs = calibration_result['dist_coefs']
        rms_error = calibration_result['rms']
        quality_info = calibration_result['quality']
        num_images = calibration_result['num_images']
        image_size = calibration_result['image_size']
        
        # Construir respuesta JSON completa
        response = {
            "success": True,
            
            # Parámetros esenciales
            "camera_matrix": camera_matrix.tolist(),
            "dist_coefs": dist_coefs.flatten().tolist(),
            "rms_error": float(rms_error),
            
            # Parámetros derivados (más amigables)
            "focal_length": {
                "fx": float(camera_matrix[0, 0]),
                "fy": float(camera_matrix[1, 1])
            },
            "optical_center": {
                "cx": float(camera_matrix[0, 2]),
                "cy": float(camera_matrix[1, 2])
            },
            
            # Métricas de calidad
            "quality": quality_info['description'],
            "quality_level": quality_info['level'],
            "quality_recommendation": quality_info['recommendation'],
            
            # Metadatos del proceso
            "num_images_used": int(num_images),
            "total_images_processed": len(images),
            "successful_images": calibration_data['successful_images'],
            "image_size": {
                "width": int(image_size[0]),
                "height": int(image_size[1])
            },
            
            # Configuración utilizada
            "calibration_config": {
                "pattern_size": list(pattern_size),
                "square_size_mm": float(square_size)
            },
            
            # Información adicional
            "timestamp": str(np.datetime64('now')),
            "distortion_model": "Brown-Conrady (k1, k2, p1, p2, k3)"
        }
        
        _print("✅ Calibración completada exitosamente!")
        _print(f"   RMS: {rms_error:.4f} píxeles")
        _print(f"   Calidad: {quality_info['description']}")
        
        return response
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error inesperado durante calibración: {str(e)}"
        }


def calibrate_from_directory(
    directory_path: Union[str, Path],
    pattern_size: tuple = (8, 5),
    square_size: float = 26.5,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Realiza calibración usando todas las imágenes de un directorio.
    
    Args:
        directory_path: Ruta al directorio con imágenes
        pattern_size: Tamaño del patrón del tablero (esquinas internas)
        square_size: Tamaño real de cada cuadrado en milímetros
        verbose: Si mostrar mensajes de progreso
        
    Returns:
        Diccionario JSON con parámetros completos de calibración.
        NO guarda archivos automáticamente - solo retorna el resultado.
    """
    try:
        directory = Path(directory_path)
        
        if not directory.exists():
            return {
                "success": False,
                "error": f"Directorio no existe: {directory_path}"
            }
        
        # Buscar archivos de imagen
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(directory.glob(f"*{ext}"))
            image_files.extend(directory.glob(f"*{ext.upper()}"))
        
        if not image_files:
            return {
                "success": False,
                "error": f"No se encontraron imágenes en el directorio: {directory_path}"
            }
        
        # Convertir paths a strings y calibrar
        image_paths = [str(img_path) for img_path in sorted(image_files)]
        
        if verbose:
            print(f"📁 Encontradas {len(image_paths)} imágenes en {directory_path}")
        
        # Usar directamente el preprocesador original para directorios
        preprocessor = ChessboardPreprocessor(
            pattern_size=pattern_size,
            square_size_mm=square_size
        )
        
        calibration_data = preprocessor.process_images_from_directory(
            calibration_dir=str(directory),
            verbose=verbose
        )
        
        # El preprocesador lanza excepción en caso de error, no retorna success=False
        if calibration_data['successful_images'] < 3:
            return {
                "success": False,
                "error": f"Se requieren al menos 3 imágenes válidas, solo se procesaron {calibration_data['successful_images']}"
            }
        
        # Calibrar usando los datos del preprocesador
        calibrator = CameraCalibrator(verbose=verbose)
        calibration_result = calibrator.calibrate(calibration_data)
        
        if not calibration_result['success']:
            return {
                "success": False,
                "error": f"Error en calibración: {calibration_result.get('error', 'Error desconocido')}"
            }
        
        # Formatear respuesta JSON igual que en calibrate_from_images
        camera_matrix = calibration_result['camera_matrix']
        dist_coefs = calibration_result['dist_coefs']
        rms_error = calibration_result['rms']
        quality_info = calibration_result['quality']
        num_images = calibration_result['num_images']
        image_size = calibration_result['image_size']
        
        return {
            "success": True,
            
            # Parámetros esenciales
            "camera_matrix": camera_matrix.tolist(),
            "dist_coefs": dist_coefs.flatten().tolist(),
            "rms_error": float(rms_error),
            
            # Parámetros derivados (más amigables)
            "focal_length": {
                "fx": float(camera_matrix[0, 0]),
                "fy": float(camera_matrix[1, 1])
            },
            "optical_center": {
                "cx": float(camera_matrix[0, 2]),
                "cy": float(camera_matrix[1, 2])
            },
            
            # Métricas de calidad
            "quality": quality_info['description'],
            "quality_level": quality_info['level'],
            "quality_recommendation": quality_info['recommendation'],
            
            # Metadatos del proceso
            "num_images_used": int(num_images),
            "total_images_processed": len(image_files),
            "successful_images": calibration_data['successful_images'],
            "image_size": {
                "width": int(image_size[0]),
                "height": int(image_size[1])
            },
            
            # Configuración utilizada
            "calibration_config": {
                "pattern_size": list(pattern_size),
                "square_size_mm": float(square_size)
            },
            
            # Información adicional
            "timestamp": str(np.datetime64('now')),
            "distortion_model": "Brown-Conrady (k1, k2, p1, p2, k3)"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error procesando directorio: {str(e)}"
        }


def save_calibration_json(calibration_result: Dict[str, Any], 
                         output_path: Union[str, Path] = "calibration_result.json") -> bool:
    """
    Guarda el resultado de calibración en un archivo JSON.
    
    Args:
        calibration_result: Resultado de calibración obtenido de calibrate_from_images
        output_path: Ruta donde guardar el archivo JSON
        
    Returns:
        True si se guardó exitosamente, False en caso contrario
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(calibration_result, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Resultado guardado en: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error guardando archivo JSON: {e}")
        return False


# Función de conveniencia para uso rápido
def quick_calibration(images_or_directory: Union[List, str, Path], 
                     **kwargs) -> Dict[str, Any]:
    """
    Función de conveniencia para calibración rápida.
    
    Args:
        images_or_directory: Lista de imágenes o ruta a directorio
        **kwargs: Argumentos adicionales para calibración
        
    Returns:
        Diccionario JSON con parámetros de calibración
    """
    if isinstance(images_or_directory, (str, Path)):
        # Es un directorio
        return calibrate_from_directory(images_or_directory, **kwargs)
    elif isinstance(images_or_directory, list):
        # Es una lista de imágenes
        return calibrate_from_images(images_or_directory, **kwargs)
    else:
        return {
            "success": False,
            "error": f"Tipo de entrada no soportado: {type(images_or_directory)}"
        }


if __name__ == "__main__":
    """Ejemplo de uso del módulo."""
    
    # Ejemplo 1: Calibrar desde directorio
    print("🧪 Probando calibración desde directorio...")
    result1 = calibrate_from_directory(
        directory_path="calibration_images",
        pattern_size=(8, 5),
        square_size=26.5,
        verbose=True
    )
    
    if result1['success']:
        print(f"✅ Calibración exitosa! RMS: {result1['rms_error']:.4f}")
        print(f"📱 Distancia focal: fx={result1['focal_length']['fx']:.1f}, fy={result1['focal_length']['fy']:.1f}")
        print("📄 JSON retornado exitosamente (no guardado automáticamente)")
    else:
        print(f"❌ Error: {result1['error']}")
    
    # Ejemplo 2: Mostrar JSON formateado
    print("\n📄 Resultado JSON:")
    print(json.dumps(result1, indent=2, ensure_ascii=False))
