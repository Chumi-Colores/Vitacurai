"""
Módulo de calibración de cámara.

Este módulo contiene la clase CameraCalibrator que realiza la calibración
de cámara usando los datos preprocesados del módulo chessboard_preprocessing.
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple, Optional
import os
import json


class CameraCalibrator:
    """
    Clase para realizar calibración de cámara usando parámetros preprocesados.
    """
    
    def __init__(self, verbose: bool = True):
        """
        Inicializa el calibrador de cámara.
        
        Args:
            verbose: Si mostrar mensajes de progreso
        """
        self.verbose = verbose
        self.camera_matrix = None
        self.dist_coefs = None
        self.rvecs = None
        self.tvecs = None
        self.rms = None
        self.image_size = None
        
    def _print(self, message: str):
        """Imprime mensaje solo si verbose=True."""
        if self.verbose:
            print(message)
    
    def calibrate(self, calibration_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza la calibración de cámara usando datos preprocesados.
        
        Args:
            calibration_data: Diccionario con datos de chessboard_preprocessing
            
        Returns:
            Diccionario con resultados de calibración
        """
        self._print("🔧 Iniciando calibración de cámara...")
        
        try:
            # Extraer datos necesarios
            objpoints = calibration_data['objpoints']
            imgpoints = calibration_data['imgpoints']
            
            # Obtener dimensiones de imagen
            sample_image_path = calibration_data['image_paths'][0]
            sample_image = cv2.imread(sample_image_path, cv2.IMREAD_GRAYSCALE)
            h, w = sample_image.shape[:2]
            self.image_size = (w, h)
            
            self._print(f"   📐 Dimensiones de imagen: {w} x {h}")
            self._print(f"   📊 Número de imágenes: {len(objpoints)}")
            self._print(f"   🎯 Puntos por imagen: {len(objpoints[0])}")
            
            # Realizar calibración con OpenCV
            self._print("   🧮 Ejecutando cv2.calibrateCamera()...")
            
            self.rms, self.camera_matrix, self.dist_coefs, self.rvecs, self.tvecs = cv2.calibrateCamera(
                objpoints,
                imgpoints,
                (w, h),
                None,
                None
            )
            
            # Evaluar calidad
            quality = self._evaluate_calibration_quality(self.rms)
            
            self._print(f"\n✅ Calibración completada:")
            self._print(f"   📈 RMS (Error de reproyección): {self.rms:.4f} píxeles")
            self._print(f"   🏆 Calidad: {quality['description']}")
            
            if self.verbose:
                self._print(f"\n📊 Matriz de cámara (parámetros intrínsecos):")
                self._print(f"   fx: {self.camera_matrix[0,0]:.2f}, fy: {self.camera_matrix[1,1]:.2f}")
                self._print(f"   cx: {self.camera_matrix[0,2]:.2f}, cy: {self.camera_matrix[1,2]:.2f}")
                
                self._print(f"\n🔧 Coeficientes de distorsión:")
                self._print(f"   [k1, k2, p1, p2, k3] = {self.dist_coefs.ravel()}")
            
            # Preparar resultado
            result = {
                'success': True,
                'rms': self.rms,
                'camera_matrix': self.camera_matrix,
                'dist_coefs': self.dist_coefs,
                'rvecs': self.rvecs,
                'tvecs': self.tvecs,
                'image_size': self.image_size,
                'quality': quality,
                'num_images': len(objpoints),
                'pattern_size': calibration_data['pattern_size'],
                'square_size': calibration_data['square_size']
            }
            
            return result
            
        except Exception as e:
            self._print(f"❌ Error durante la calibración: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _evaluate_calibration_quality(self, rms: float) -> Dict[str, Any]:
        """
        Evalúa la calidad de la calibración basada en el RMS.
        
        Args:
            rms: Error de reproyección RMS
            
        Returns:
            Diccionario con información de calidad
        """
        if rms < 0.5:
            return {
                'level': 'excellent',
                'description': '🎉 Excelente (RMS < 0.5)',
                'recommendation': 'Calibración óptima'
            }
        elif rms < 1.0:
            return {
                'level': 'good',
                'description': '✅ Buena (0.5 ≤ RMS < 1.0)',
                'recommendation': 'Calibración satisfactoria'
            }
        elif rms < 2.0:
            return {
                'level': 'acceptable',
                'description': '⚠️ Aceptable (1.0 ≤ RMS < 2.0)',
                'recommendation': 'Considerar mejorar con más imágenes'
            }
        else:
            return {
                'level': 'poor',
                'description': '❌ Pobre (RMS ≥ 2.0)',
                'recommendation': 'Recalibrar con mejores imágenes'
            }
    
    def save_parameters(self, 
                       output_file: str = "camera_calibration.npz",
                       json_file: Optional[str] = None) -> bool:
        """
        Guarda los parámetros de calibración en archivo.
        
        Args:
            output_file: Archivo .npz para guardar parámetros
            json_file: Archivo .json opcional para metadatos
            
        Returns:
            True si se guardó exitosamente, False en caso contrario
        """
        if self.camera_matrix is None:
            self._print("❌ No hay parámetros de calibración para guardar")
            return False
        
        try:
            # Guardar en formato NumPy
            np.savez(
                output_file,
                camera_matrix=self.camera_matrix,
                dist_coefs=self.dist_coefs,
                rvecs=self.rvecs,
                tvecs=self.tvecs,
                rms=self.rms,
                image_size=np.array(self.image_size)
            )
            
            self._print(f"💾 Parámetros guardados en: {output_file}")
            
            # Guardar metadatos en JSON si se especifica
            if json_file:
                metadata = {
                    'rms': float(self.rms),
                    'image_size': list(self.image_size),
                    'camera_matrix': self.camera_matrix.tolist(),
                    'dist_coefs': self.dist_coefs.tolist()
                }
                
                with open(json_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                self._print(f"📄 Metadatos guardados en: {json_file}")
            
            return True
            
        except Exception as e:
            self._print(f"❌ Error guardando parámetros: {e}")
            return False
    
    def test_undistortion(self, test_image_path: str, 
                         output_path: str = "undistorted_test.jpg") -> bool:
        """
        Prueba la corrección de distorsión en una imagen.
        
        Args:
            test_image_path: Ruta de imagen para probar
            output_path: Ruta donde guardar imagen corregida
            
        Returns:
            True si se procesó exitosamente, False en caso contrario
        """
        if self.camera_matrix is None:
            self._print("❌ No hay parámetros de calibración disponibles")
            return False
        
        try:
            # Cargar imagen
            img = cv2.imread(test_image_path)
            if img is None:
                self._print(f"❌ No se pudo cargar la imagen: {test_image_path}")
                return False
            
            # Corregir distorsión
            undistorted = cv2.undistort(img, self.camera_matrix, self.dist_coefs)
            
            # Guardar resultado
            cv2.imwrite(output_path, undistorted)
            
            self._print(f"🔧 Corrección de distorsión completada:")
            self._print(f"   📥 Imagen original: {test_image_path}")
            self._print(f"   📤 Imagen corregida: {output_path}")
            
            return True
            
        except Exception as e:
            self._print(f"❌ Error en corrección de distorsión: {e}")
            return False


def load_calibration_parameters(npz_file: str) -> Optional[Dict[str, Any]]:
    """
    Carga parámetros de calibración desde archivo .npz.
    
    Args:
        npz_file: Ruta al archivo .npz
        
    Returns:
        Diccionario con parámetros o None si falla
    """
    try:
        data = np.load(npz_file)
        return {
            'camera_matrix': data['camera_matrix'],
            'dist_coefs': data['dist_coefs'],
            'rvecs': data.get('rvecs', None),
            'tvecs': data.get('tvecs', None),
            'rms': data.get('rms', None),
            'image_size': tuple(data.get('image_size', [0, 0]))
        }
    except Exception as e:
        print(f"Error cargando parámetros: {e}")
        return None