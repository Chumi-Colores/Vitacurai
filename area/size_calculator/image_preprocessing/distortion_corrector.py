"""
Módulo de corrección de distorsión de imagen.

Este módulo se encarga de:
1. Cargar parámetros de calibración
2. Corregir distorsión de imagen usando parámetros de calibración
3. Transformar coordenadas de contornos corregidos
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional, Dict, Any
import os


class DistortionCorrector:
    """
    Corrector de distorsión usando parámetros de calibración de cámara.
    """
    
    def __init__(self, calibration_file: str, verbose: bool = True):
        """
        Inicializa el corrector con parámetros de calibración.
        
        Args:
            calibration_file: Ruta al archivo .npz de calibración
            verbose: Si mostrar mensajes de progreso
        """
        self.verbose = verbose
        self.calibration_file = calibration_file
        self.camera_matrix = None
        self.dist_coeffs = None
        self.new_camera_matrix = None
        self.roi = None
        
        self._load_calibration_parameters()
    
    def _print(self, message: str):
        """Imprime mensaje solo si verbose=True."""
        if self.verbose:
            print(message)
    
    def _load_calibration_parameters(self):
        """
        Carga los parámetros de calibración desde archivo.
        """
        if not os.path.exists(self.calibration_file):
            raise FileNotFoundError(f"❌ No se encontró archivo de calibración: {self.calibration_file}")
        
        try:
            # Cargar datos de calibración
            calib_data = np.load(self.calibration_file)
            
            self.camera_matrix = calib_data['camera_matrix']
            self.dist_coeffs = calib_data['dist_coefs']
            
            self._print("✅ Parámetros de calibración cargados exitosamente")
            self._print(f"   📐 Matriz de cámara: {self.camera_matrix[0,0]:.1f}x{self.camera_matrix[1,1]:.1f}")
            self._print(f"   🎯 Centro óptico: ({self.camera_matrix[0,2]:.1f}, {self.camera_matrix[1,2]:.1f})")
            
        except Exception as e:
            raise ValueError(f"❌ Error cargando calibración: {e}")
    
    def correct_image_distortion(self, image: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Corrige la distorsión de una imagen.
        
        Args:
            image: Imagen de entrada (BGR)
            
        Returns:
            Tupla de (imagen_corregida, información_de_transformación)
        """
        h, w = image.shape[:2]
        
        # Obtener matriz de cámara optimizada
        self.new_camera_matrix, self.roi = cv2.getOptimalNewCameraMatrix(
            self.camera_matrix, 
            self.dist_coeffs, 
            (w, h), 
            1,  # alpha=1 mantiene todos los píxeles originales
            (w, h)
        )
        
        # Corregir distorsión
        undistorted = cv2.undistort(
            image, 
            self.camera_matrix, 
            self.dist_coeffs, 
            None, 
            self.new_camera_matrix
        )
        
        # Recortar imagen según ROI
        x, y, w_roi, h_roi = self.roi
        undistorted_cropped = undistorted[y:y+h_roi, x:x+w_roi]
        
        transform_info = {
            'original_size': (w, h),
            'corrected_size': (w_roi, h_roi),
            'roi': self.roi,
            'camera_matrix_original': self.camera_matrix,
            'camera_matrix_corrected': self.new_camera_matrix
        }
        
        self._print(f"✅ Distorsión corregida")
        self._print(f"   📏 Tamaño original: {w}x{h}")
        self._print(f"   📏 Tamaño corregido: {w_roi}x{h_roi}")
        self._print(f"   ✂️  ROI: x={x}, y={y}, w={w_roi}, h={h_roi}")
        
        return undistorted_cropped, transform_info
    
    def transform_contour_coordinates(self, 
                                    contours: List[Tuple[int, int]], 
                                    transform_info: Dict[str, Any]) -> List[Tuple[int, int]]:
        """
        Transforma coordenadas de contornos a imagen corregida.
        
        Args:
            contours: Lista de puntos (x, y) en imagen original
            transform_info: Información de transformación de correct_image_distortion
            
        Returns:
            Lista de puntos transformados
        """
        # Convertir contornos a formato numpy
        contours_array = np.array(contours, dtype=np.float32).reshape(-1, 1, 2)
        
        # Aplicar corrección de distorsión a los puntos
        undistorted_points = cv2.undistortPoints(
            contours_array,
            self.camera_matrix,
            self.dist_coeffs,
            None,
            self.new_camera_matrix
        )
        
        # Convertir de vuelta a lista de tuplas y aplicar offset de ROI
        roi_x, roi_y, _, _ = transform_info['roi']
        
        transformed_contours = []
        for point in undistorted_points.reshape(-1, 2):
            # Ajustar por el offset del ROI
            x = int(point[0] - roi_x)
            y = int(point[1] - roi_y) 
            transformed_contours.append((x, y))
        
        self._print(f"✅ {len(contours)} puntos transformados")
        self._print(f"   Original: {contours}")
        self._print(f"   Corregido: {transformed_contours}")
        
        return transformed_contours
    
    def get_corrected_camera_parameters(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Obtiene los parámetros de cámara corregidos para cálculos posteriores.
        
        Returns:
            Tupla de (camera_matrix_corregida, coeficientes_distorsion_nulos)
        """
        if self.new_camera_matrix is None:
            raise ValueError("❌ Debe corregir una imagen primero para obtener parámetros")
        
        # Los coeficientes de distorsión son cero para imagen corregida
        zero_dist_coeffs = np.zeros_like(self.dist_coeffs)
        
        return self.new_camera_matrix, zero_dist_coeffs


def correct_image_and_contours(image_path: str, 
                             contours: List[Tuple[int, int]], 
                             calibration_file: str,
                             verbose: bool = True) -> Tuple[np.ndarray, List[Tuple[int, int]], Dict[str, Any]]:
    """
    Función de conveniencia para corregir imagen y contornos de una vez.
    
    Args:
        image_path: Ruta a la imagen
        contours: Lista de puntos del rectángulo
        calibration_file: Ruta al archivo de calibración
        verbose: Si mostrar mensajes de progreso
        
    Returns:
        Tupla de (imagen_corregida, contornos_corregidos, parámetros_cámara)
    """
    # Cargar imagen
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"❌ No se pudo cargar la imagen: {image_path}")
    
    # Crear corrector
    corrector = DistortionCorrector(calibration_file, verbose=verbose)
    
    # Corregir distorsión de imagen
    corrected_image, transform_info = corrector.correct_image_distortion(image)
    
    # Transformar coordenadas de contornos
    corrected_contours = corrector.transform_contour_coordinates(contours, transform_info)
    
    # Obtener parámetros de cámara corregidos
    camera_matrix, dist_coeffs = corrector.get_corrected_camera_parameters()
    
    camera_params = {
        'camera_matrix': camera_matrix,
        'dist_coeffs': dist_coeffs,
        'transform_info': transform_info
    }
    
    return corrected_image, corrected_contours, camera_params