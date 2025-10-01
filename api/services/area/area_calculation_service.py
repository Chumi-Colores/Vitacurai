"""
Servicio especializado de cálculo de área de carteles.

Este servicio implementa la lógica del sistema de medición de carteles,
pero recibe directamente los parámetros de calibración de cámara como entrada.
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any, Union
import cv2
import numpy as np
import tempfile
import json
import io


class AreaCalculationService:
    """
    Servicio especializado en cálculo de área de carteles.
    
    Implementa la misma lógica que area/size_calculator/main.py pero recibe
    directamente los parámetros de calibración de cámara como entrada.
    """
    
    def __init__(self, verbose: bool = True):
        """
        Inicializa el servicio de cálculo de área.
        
        Args:
            verbose: Si mostrar mensajes detallados durante el procesamiento
        """
        self.verbose = verbose
        self._setup_calculation_modules()
    
    def _setup_calculation_modules(self):
        """Configura los módulos de cálculo internos de la API."""
        # Importar módulos internos de la API
        try:
            from .modules.image_preprocessing import validate_and_order_contours
            from .modules.inverse_projection import project_pixels_to_3d
            from .modules.geometric_calculation import calculate_rectangle_area
            
            # Asignar funciones a variables de instancia
            self._validate_and_order_contours = validate_and_order_contours
            self._project_pixels_to_3d = project_pixels_to_3d
            self._calculate_rectangle_area = calculate_rectangle_area
            
        except ImportError as e:
            raise ImportError(f"No se pudieron importar los módulos internos de cálculo: {e}")
    
    def _print(self, message: str):
        """Imprime mensaje solo si verbose=True."""
        if self.verbose:
            print(message)
    
    def calculate_cartel_area(self,
                            image_data: Union[str, np.ndarray, bytes],
                            vertices: List[List[float]],
                            physical_distance: float,
                            focal_length: Tuple[float, float],
                            optical_center: Tuple[float, float],
                            distortion_coefs: List[float]) -> Dict[str, Any]:
        """
        Calcula las dimensiones de un cartel rectangular en una imagen.
        
        Args:
            image_data: Imagen como ruta, array numpy o bytes
            vertices: Coordenadas de los vértices [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            physical_distance: Distancia física de la cámara al cartel en metros
            focal_length: Distancia focal (fx, fy) en píxeles
            optical_center: Centro óptico (cx, cy) en píxeles
            distortion_coefs: Coeficientes de distorsión [k1, k2, p1, p2, k3]
            
        Returns:
            Diccionario JSON con resultado del cálculo de área
        """
        try:
            self._print(f"\n" + "="*60)
            self._print("📏 SISTEMA DE CÁLCULO DE ÁREA DE CARTELES")
            self._print("="*60)
            self._print(f"📍 Vértices: {vertices}")
            self._print(f"📏 Distancia física: {physical_distance} m")
            self._print(f"🔍 Focal length: {focal_length}")
            self._print(f"🎯 Centro óptico: {optical_center}")
            
            # ============================================
            # FASE 0: PROCESAMIENTO DE IMAGEN
            # ============================================
            image = self._load_image(image_data)
            if image is None:
                return {
                    "success": False,
                    "error": "No se pudo cargar la imagen"
                }
            
            self._print(f"🖼️ Imagen cargada: {image.shape}")
            
            # Convertir vértices a tuplas de enteros
            contours = [(int(v[0]), int(v[1])) for v in vertices]
            
            # ============================================
            # FASE 1: PREPROCESAMIENTO DE CONTORNOS
            # ============================================
            self._print(f"\n🔧 FASE 1: VALIDACIÓN Y ORDENAMIENTO DE CONTORNOS")
            self._print("-" * 50)
            
            # Validar y ordenar contornos
            contour_result = self._validate_and_order_contours(contours, verbose=self.verbose)
            if contour_result is None:
                return {
                    "success": False,
                    "error": "Contornos inválidos - deben formar un cuadrilátero válido"
                }
            
            ordered_corners, perspective_info = contour_result
            self._print(f"✅ Contornos validados y ordenados")
            
            # ============================================
            # FASE 2: CORRECCIÓN DE DISTORSIÓN
            # ============================================
            self._print(f"\n🔧 FASE 2: CORRECCIÓN DE DISTORSIÓN DE IMAGEN")
            self._print("-" * 45)
            
            # Crear matriz de cámara a partir de parámetros
            camera_matrix = np.array([
                [focal_length[0], 0, optical_center[0]],
                [0, focal_length[1], optical_center[1]],
                [0, 0, 1]
            ], dtype=np.float64)
            
            # Convertir coeficientes de distorsión a array numpy
            dist_coefs_array = np.array(distortion_coefs, dtype=np.float64)
            
            # Corregir distorsión de imagen
            corrected_image, corrected_contours = self._correct_image_and_contours_with_params(
                image, ordered_corners, camera_matrix, dist_coefs_array
            )
            
            self._print(f"✅ Distorsión corregida")
            self._print(f"📏 Imagen original: {image.shape[:2]}")
            self._print(f"📏 Imagen corregida: {corrected_image.shape[:2]}")
            
            # ============================================
            # FASE 3: PROYECCIÓN INVERSA 2D → 3D
            # ============================================
            self._print(f"\n📐 FASE 3: PROYECCIÓN INVERSA 2D → 3D")
            self._print("-" * 40)
            
            # Proyectar contornos corregidos a coordenadas 3D
            points_3d = self._project_pixels_to_3d(
                corrected_contours,
                camera_matrix,
                physical_distance,
                perspective_angle=perspective_info['perspective_angle'],
                verbose=self.verbose
            )
            
            self._print(f"✅ Proyección 3D completada")
            
            # ============================================
            # FASE 4: CÁLCULO GEOMÉTRICO
            # ============================================
            self._print(f"\n📊 FASE 4: CÁLCULO GEOMÉTRICO FINAL")
            self._print("-" * 40)
            
            # Calcular área final
            area_result = self._calculate_rectangle_area(points_3d, verbose=self.verbose)
            
            # ============================================
            # COMPILAR RESULTADO FINAL
            # ============================================
            result = self._compile_final_result(
                area_result, perspective_info, vertices, 
                corrected_contours, physical_distance
            )
            
            self._print_final_results(result)
            return result
            
        except Exception as e:
            error_msg = f"Error durante cálculo de área: {str(e)}"
            self._print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def _load_image(self, image_data: Union[str, np.ndarray, bytes]) -> np.ndarray:
        """
        Carga imagen desde diferentes formatos de entrada.
        
        Args:
            image_data: Imagen como ruta, array numpy o bytes
            
        Returns:
            Array numpy con la imagen o None si hay error
        """
        try:
            # Si ya es un array numpy
            if isinstance(image_data, np.ndarray):
                return image_data
            
            # Si es una ruta de archivo
            elif isinstance(image_data, str):
                if image_data.startswith('file://'):
                    image_data = image_data.replace('file://', '')
                
                image = cv2.imread(image_data, cv2.IMREAD_COLOR)
                if image is None:
                    # Intentar con PIL como fallback
                    from PIL import Image as PILImage
                    pil_img = PILImage.open(image_data)
                    if pil_img.mode != 'RGB':
                        pil_img = pil_img.convert('RGB')
                    img_array = np.array(pil_img)
                    image = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                return image
            
            # Si son bytes
            elif isinstance(image_data, bytes):
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if image is None:
                    # Intentar con PIL
                    from PIL import Image as PILImage
                    pil_img = PILImage.open(io.BytesIO(image_data))
                    if pil_img.mode != 'RGB':
                        pil_img = pil_img.convert('RGB')
                    img_array = np.array(pil_img)
                    image = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                return image
            
            return None
            
        except Exception as e:
            self._print(f"⚠️ Error cargando imagen: {e}")
            return None
    
    def _correct_image_and_contours_with_params(self, 
                                              image: np.ndarray,
                                              contours: List[Tuple[int, int]],
                                              camera_matrix: np.ndarray,
                                              dist_coefs: np.ndarray) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
        """
        Corrige distorsión de imagen y ajusta contornos usando parámetros directos.
        
        Args:
            image: Imagen original
            contours: Lista de contornos
            camera_matrix: Matriz de cámara 3x3
            dist_coefs: Coeficientes de distorsión
            
        Returns:
            Tupla con imagen corregida y contornos ajustados
        """
        # Obtener dimensiones de imagen
        h, w = image.shape[:2]
        
        # Obtener matriz de cámara optimizada
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
            camera_matrix, dist_coefs, (w, h), 1, (w, h)
        )
        
        # Corregir distorsión de imagen
        corrected_image = cv2.undistort(image, camera_matrix, dist_coefs, None, new_camera_matrix)
        
        # Convertir contornos a array numpy para undistortPoints
        contours_array = np.array([[[float(x), float(y)]] for x, y in contours], dtype=np.float32)
        
        # Corregir distorsión de los contornos usando undistortPoints
        corrected_contours_array = cv2.undistortPoints(
            contours_array, camera_matrix, dist_coefs, P=new_camera_matrix
        )
        
        # Convertir de vuelta a lista de tuplas
        adjusted_contours = [(int(pt[0][0]), int(pt[0][1])) for pt in corrected_contours_array]
        
        # Aplicar ROI si es necesario (recortar imagen)
        x_roi, y_roi, w_roi, h_roi = roi
        if w_roi > 0 and h_roi > 0:
            corrected_image = corrected_image[y_roi:y_roi+h_roi, x_roi:x_roi+w_roi]
            
            # Ajustar contornos según el recorte del ROI
            adjusted_contours = [(max(0, x - x_roi), max(0, y - y_roi)) 
                               for x, y in adjusted_contours]
        
        self._print(f"✅ Distorsión corregida - Original: {(w,h)}, Corregida: {corrected_image.shape[:2]}")
        self._print(f"📍 Contornos: Original {contours} → Corregidos {adjusted_contours}")
        
        return corrected_image, adjusted_contours
    
    def _compile_final_result(self,
                            area_result: Dict[str, Any],
                            perspective_info: Dict[str, Any],
                            original_vertices: List[List[float]],
                            corrected_contours: List[Tuple[int, int]],
                            physical_distance: float) -> Dict[str, Any]:
        """
        Compila el resultado final en el formato JSON requerido.
        
        Args:
            area_result: Resultado del cálculo geométrico
            perspective_info: Información de perspectiva
            original_vertices: Vértices originales
            corrected_contours: Contornos corregidos
            physical_distance: Distancia física
            
        Returns:
            Diccionario con resultado completo
        """
        quality = area_result['validation']['quality_assessment']
        validation = area_result['validation']
        
        # Obtener ratios y ángulos del cálculo geométrico
        h_ratio = validation.get('horizontal_ratio', area_result.get('horizontal_ratio', 1.0))
        v_ratio = validation.get('vertical_ratio', area_result.get('vertical_ratio', 1.0))
        mean_angle = validation.get('average_angle', area_result.get('average_angle', 90.0))
        angle_std = validation.get('angle_std', area_result.get('angle_std', 0.0))
        
        return {
            "success": True,
            "area_square_meters": round(area_result['area_square_meters'], 6),
            "width_meters": round(area_result['width_meters'], 4),
            "height_meters": round(area_result['height_meters'], 4),
            "parallel_sides_ratios": {
                "horizontal": round(h_ratio, 3),
                "vertical": round(v_ratio, 3)
            },
            "average_angles": {
                "mean": round(mean_angle, 1),
                "std_deviation": round(angle_std, 1)
            },
            "quality": {
                "level": quality['quality'],
                "description": quality['description'],
                "confidence_percent": round(quality['confidence'] * 100, 1)
            },
            "observations": quality.get('issues', []),
            "calculation_info": {
                "perspective_corrected": perspective_info['has_perspective'],
                "perspective_angle": round(perspective_info['perspective_angle'], 1),
                "physical_distance_meters": physical_distance,
                "original_vertices": original_vertices,
                "corrected_contours": [[int(x), int(y)] for x, y in corrected_contours]
            }
        }
    
    def _print_final_results(self, result: Dict[str, Any]):
        """Imprime resultados finales si verbose=True."""
        if not self.verbose:
            return
            
        self._print(f"\n" + "="*60)
        self._print("🎯 RESULTADO FINAL")
        self._print("="*60)
        
        self._print(f"📊 Área del cartel: {result['area_square_meters']:.4f} m²")
        self._print(f"📏 Alto: {result['height_meters']:.3f} m")
        self._print(f"📏 Ancho: {result['width_meters']:.3f} m")
        
        ratios = result['parallel_sides_ratios']
        self._print(f"📐 Ratios lados paralelos: H={ratios['horizontal']}, V={ratios['vertical']}")
        
        angles = result['average_angles']
        self._print(f"📐 Ángulos promedio: {angles['mean']:.1f}° ± {angles['std_deviation']:.1f}°")
        
        quality = result['quality']
        self._print(f"🎯 Calidad: {quality['description']}")
        self._print(f"🔬 Confianza: {quality['confidence_percent']:.1f}%")
        
        if result['observations']:
            self._print(f"\n⚠️  Observaciones:")
            for obs in result['observations']:
                self._print(f"   • {obs}")
    
    def validate_parameters(self,
                          vertices: List[List[float]],
                          physical_distance: float,
                          focal_length: Tuple[float, float],
                          optical_center: Tuple[float, float],
                          distortion_coefs: List[float]) -> Dict[str, Union[bool, str]]:
        """
        Valida los parámetros de entrada para el cálculo de área.
        
        Args:
            vertices: Lista de vértices
            physical_distance: Distancia física
            focal_length: Distancia focal
            optical_center: Centro óptico
            distortion_coefs: Coeficientes de distorsión
            
        Returns:
            Diccionario con resultado de validación
        """
        # Validar vértices
        if not vertices or not isinstance(vertices, list) or len(vertices) != 4:
            return {
                "valid": False,
                "error": "Se requieren exactamente 4 vértices [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]"
            }
        
        for i, vertex in enumerate(vertices):
            if not isinstance(vertex, list) or len(vertex) != 2:
                return {
                    "valid": False,
                    "error": f"Vértice {i+1} debe tener formato [x, y]"
                }
            if not all(isinstance(coord, (int, float)) for coord in vertex):
                return {
                    "valid": False,
                    "error": f"Vértice {i+1} debe contener coordenadas numéricas"
                }
        
        # Validar distancia física
        if not isinstance(physical_distance, (int, float)) or physical_distance <= 0:
            return {
                "valid": False,
                "error": "physical_distance debe ser un número positivo"
            }
        
        # Validar focal length
        if not isinstance(focal_length, (tuple, list)) or len(focal_length) != 2:
            return {
                "valid": False,
                "error": "focal_length debe ser una tupla (fx, fy)"
            }
        if not all(isinstance(f, (int, float)) and f > 0 for f in focal_length):
            return {
                "valid": False,
                "error": "focal_length debe contener valores positivos"
            }
        
        # Validar centro óptico
        if not isinstance(optical_center, (tuple, list)) or len(optical_center) != 2:
            return {
                "valid": False,
                "error": "optical_center debe ser una tupla (cx, cy)"
            }
        if not all(isinstance(c, (int, float)) for c in optical_center):
            return {
                "valid": False,
                "error": "optical_center debe contener valores numéricos"
            }
        
        # Validar coeficientes de distorsión
        if not distortion_coefs or len(distortion_coefs) != 5:
            return {
                "valid": False,
                "error": "distortion_coefs debe tener exactamente 5 elementos [k1, k2, p1, p2, k3]"
            }
        if not all(isinstance(coef, (int, float)) for coef in distortion_coefs):
            return {
                "valid": False,
                "error": "distortion_coefs debe contener valores numéricos"
            }
        
        return {
            "valid": True,
            "message": "Parámetros válidos"
        }
