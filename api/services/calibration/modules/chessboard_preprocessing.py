"""
Módulo de preprocesamiento para calibración de cámara con tablero de ajedrez.
Basado en el notebook lab03.ipynb

Este módulo extrae imágenes de un directorio y aplica el preprocesamiento
necesario para obtener los parámetros de calibración de la cámara.
"""

import os
import glob
import numpy as np
import cv2
from typing import List, Tuple, Optional, Dict, Any


class ChessboardPreprocessor:
    """
    Clase para procesar imágenes de tablero de ajedrez y preparar datos
    para calibración de cámara.
    """
    
    def __init__(self, pattern_size: Tuple[int, int] = (8, 5), 
                 square_size_mm: float = 26.5):
        """
        Inicializa el preprocesador con parámetros del tablero de ajedrez.
        
        Args:
            pattern_size: Número de esquinas internas (columnas, filas)
            square_size_mm: Tamaño del cuadrado en milímetros
        """
        self.pattern_size = pattern_size
        self.square_size_mm = square_size_mm
        self.square_size = square_size_mm  # Mantenemos en mm como en lab03
        
        # Generar puntos 3D del patrón del tablero
        self.pattern_points = self._generate_pattern_points()
    
    def _generate_pattern_points(self) -> np.ndarray:
        """
        Genera las coordenadas 3D del patrón del tablero de ajedrez.
        
        Returns:
            Array numpy con las coordenadas 3D de las esquinas del tablero
        """
        # Crear índices siguiendo el método del lab03
        indices = np.indices(self.pattern_size, dtype=np.float32)
        indices *= self.square_size
        
        # Transponer y reorganizar para obtener coordenadas (x, y)
        coords_3D = np.transpose(indices, [2, 1, 0])
        coords_3D = coords_3D.reshape(-1, 2)
        
        # Añadir coordenada z=0 (asunción planar)
        pattern_points = np.concatenate([
            coords_3D, 
            np.zeros([coords_3D.shape[0], 1], dtype=np.float32)
        ], axis=-1)
        
        return pattern_points
    
    def process_single_image(self, image_path: str, 
                           verbose: bool = True) -> Optional[np.ndarray]:
        """
        Procesa una sola imagen para detectar y refinar las esquinas del tablero.
        
        Args:
            image_path: Ruta a la imagen
            verbose: Si mostrar mensajes de progreso
            
        Returns:
            Array numpy con las coordenadas 2D de las esquinas detectadas,
            o None si no se detecta el tablero
        """
        if verbose:
            print(f'Procesando {os.path.basename(image_path)}')
        
        # Cargar imagen en escala de grises
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"Error: No se pudo cargar {image_path}")
            return None
        
        # Detectar esquinas del tablero de ajedrez
        found, corners = cv2.findChessboardCorners(img, self.pattern_size)
        
        if found:
            # Refinar posición de esquinas con precisión subpíxel
            # Criterios: EPS + COUNT, max_iter=30, epsilon=0.001
            term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.001)
            cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), term)
            
            if verbose:
                print('✓ Tablero detectado correctamente')
            
            return corners.reshape(-1, 2)
        else:
            if verbose:
                print('✗ No se pudo detectar el tablero de ajedrez')
            return None
    
    def process_images_from_directory(self, 
                                    calibration_dir: str = "calibration_images",
                                    image_extensions: List[str] = ['.jpg', '.jpeg', '.png'],
                                    verbose: bool = True) -> Dict[str, Any]:
        """
        Extrae y procesa todas las imágenes de un directorio para calibración.
        
        Args:
            calibration_dir: Directorio con las imágenes de calibración
            image_extensions: Extensiones de archivo a buscar
            verbose: Si mostrar mensajes de progreso
            
        Returns:
            Diccionario con los datos necesarios para calibración:
            {
                'objpoints': Lista de puntos 3D del patrón,
                'imgpoints': Lista de puntos 2D detectados,
                'image_paths': Lista de rutas de imágenes procesadas exitosamente,
                'pattern_size': Tamaño del patrón,
                'square_size': Tamaño del cuadrado en mm,
                'failed_images': Lista de imágenes que fallaron,
                'total_images': Número total de imágenes encontradas,
                'successful_images': Número de imágenes procesadas exitosamente
            }
        """
        # Construir lista de archivos de imagen
        image_paths = []
        for ext in image_extensions:
            pattern = os.path.join(calibration_dir, f"*{ext}")
            image_paths.extend(glob.glob(pattern))
            pattern_upper = os.path.join(calibration_dir, f"*{ext.upper()}")
            image_paths.extend(glob.glob(pattern_upper))
        
        image_paths = sorted(list(set(image_paths)))  # Eliminar duplicados y ordenar
        
        if verbose:
            print(f"Encontradas {len(image_paths)} imágenes en {calibration_dir}")
        
        if len(image_paths) == 0:
            raise ValueError(f"No se encontraron imágenes en {calibration_dir}")
        
        # Procesar cada imagen
        objpoints = []  # Puntos 3D en el mundo real
        imgpoints = []  # Puntos 2D en el plano de la imagen
        successful_paths = []
        failed_images = []
        
        for img_path in image_paths:
            corners = self.process_single_image(img_path, verbose=verbose)
            
            if corners is not None:
                objpoints.append(self.pattern_points)
                imgpoints.append(corners)
                successful_paths.append(img_path)
            else:
                failed_images.append(img_path)
        
        if verbose:
            print(f"\nResumen del preprocesamiento:")
            print(f"  - Imágenes procesadas exitosamente: {len(successful_paths)}")
            print(f"  - Imágenes fallidas: {len(failed_images)}")
            
            if len(failed_images) > 0:
                print(f"  - Archivos fallidos: {[os.path.basename(f) for f in failed_images]}")
        
        if len(objpoints) < 3:
            raise ValueError(
                f"Se necesitan al menos 3 imágenes válidas para calibración. "
                f"Solo se procesaron exitosamente {len(objpoints)} imágenes."
            )
        
        return {
            'objpoints': objpoints,
            'imgpoints': imgpoints,
            'image_paths': successful_paths,
            'pattern_size': self.pattern_size,
            'square_size': self.square_size_mm,
            'failed_images': failed_images,
            'total_images': len(image_paths),
            'successful_images': len(successful_paths)
        }
    
    def visualize_detection(self, image_path: str, 
                           save_path: Optional[str] = None) -> bool:
        """
        Visualiza la detección de esquinas en una imagen.
        
        Args:
            image_path: Ruta a la imagen
            save_path: Ruta donde guardar la imagen con esquinas dibujadas (opcional)
            
        Returns:
            True si se detectaron esquinas, False en caso contrario
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"Error: No se pudo cargar {image_path}")
            return False
        
        found, corners = cv2.findChessboardCorners(img, self.pattern_size)
        
        if found:
            # Refinar esquinas
            term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.001)
            cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), term)
            
            # Dibujar esquinas
            vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            cv2.drawChessboardCorners(vis, self.pattern_size, corners, found)
            
            if save_path:
                cv2.imwrite(save_path, vis)
                print(f"Imagen con esquinas guardada en: {save_path}")
            
            return True
        else:
            print(f"No se detectaron esquinas en {image_path}")
            return False


def extract_calibration_parameters(calibration_dir: str = "calibration_images",
                                 pattern_size: Tuple[int, int] = (8, 5),
                                 square_size_mm: float = 26.5,
                                 verbose: bool = True) -> Dict[str, Any]:
    """
    Función principal para extraer parámetros de calibración de un directorio de imágenes.
    
    Args:
        calibration_dir: Directorio con imágenes del tablero de ajedrez
        pattern_size: Número de esquinas internas (columnas, filas)
        square_size_mm: Tamaño del cuadrado en milímetros
        verbose: Si mostrar mensajes de progreso
        
    Returns:
        Diccionario con todos los parámetros necesarios para cv2.calibrateCamera()
    """
    # Crear instancia del preprocesador
    preprocessor = ChessboardPreprocessor(pattern_size, square_size_mm)
    
    # Procesar imágenes
    calibration_data = preprocessor.process_images_from_directory(
        calibration_dir=calibration_dir,
        verbose=verbose
    )
    
    if verbose:
        print(f"\n✓ Preprocesamiento completado exitosamente")
        print(f"  - Datos listos para cv2.calibrateCamera()")
        print(f"  - Patrón: {pattern_size[0]}x{pattern_size[1]} esquinas internas")
        print(f"  - Tamaño de cuadrado: {square_size_mm}mm")
    
    return calibration_data