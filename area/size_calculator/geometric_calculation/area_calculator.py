"""
Módulo de cálculo geométrico de áreas.

Este módulo se encarga de:
1. Calcular vectores 3D entre esquinas del rectángulo
2. Determinar ancho y alto en el espacio 3D
3. Calcular el área final en metros cuadrados
4. Validar la consistencia geométrica del resultado
"""

import numpy as np
import math
from typing import List, Dict, Any, Tuple, Optional


class AreaCalculator:
    """
    Calculadora de área para rectángulos en espacio 3D.
    """
    
    def __init__(self, verbose: bool = True):
        """
        Inicializa la calculadora de área.
        
        Args:
            verbose: Si mostrar mensajes de progreso
        """
        self.verbose = verbose
    
    def _print(self, message: str):
        """Imprime mensaje solo si verbose=True."""
        if self.verbose:
            print(message)
    
    def calculate_side_vectors(self, corners_3d: List[np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Calcula vectores de los lados del rectángulo.
        
        Args:
            corners_3d: Lista de 4 esquinas 3D [top_left, top_right, bottom_right, bottom_left]
            
        Returns:
            Diccionario con vectores de cada lado
        """
        if len(corners_3d) != 4:
            raise ValueError(f"❌ Se esperan 4 esquinas, se recibieron {len(corners_3d)}")
        
        tl, tr, br, bl = corners_3d
        
        # Calcular vectores de cada lado
        vectors = {
            'top': tr - tl,        # Vector superior (izquierda → derecha)
            'right': br - tr,      # Vector derecho (arriba → abajo)
            'bottom': bl - br,     # Vector inferior (derecha → izquierda)
            'left': tl - bl        # Vector izquierdo (abajo → arriba)
        }
        
        self._print("📐 Vectores de lados calculados:")
        for side, vector in vectors.items():
            length = np.linalg.norm(vector)
            self._print(f"   {side.capitalize()}: [{vector[0]:.3f}, {vector[1]:.3f}, {vector[2]:.3f}] (L={length:.3f}m)")
        
        return vectors
    
    def calculate_dimensions(self, side_vectors: Dict[str, np.ndarray]) -> Dict[str, float]:
        """
        Calcula las dimensiones del rectángulo.
        
        Args:
            side_vectors: Diccionario con vectores de lados
            
        Returns:
            Diccionario con dimensiones calculadas
        """
        # Calcular longitudes de lados opuestos
        top_length = np.linalg.norm(side_vectors['top'])
        bottom_length = np.linalg.norm(side_vectors['bottom'])
        left_length = np.linalg.norm(side_vectors['left']) 
        right_length = np.linalg.norm(side_vectors['right'])
        
        # Promediar lados paralelos para mayor precisión
        width = (top_length + bottom_length) / 2.0
        height = (left_length + right_length) / 2.0
        
        # Área total
        area = width * height
        
        dimensions = {
            'width_meters': width,
            'height_meters': height,
            'area_square_meters': area,
            'side_lengths': {
                'top': top_length,
                'bottom': bottom_length,
                'left': left_length,
                'right': right_length
            }
        }
        
        self._print(f"📏 Dimensiones calculadas:")
        self._print(f"   Ancho: {width:.3f} m (promedio top/bottom: {top_length:.3f}/{bottom_length:.3f})")
        self._print(f"   Alto: {height:.3f} m (promedio left/right: {left_length:.3f}/{right_length:.3f})")
        self._print(f"   📊 Área: {area:.4f} m²")
        
        return dimensions
    
    def validate_rectangle_geometry(self, 
                                   side_vectors: Dict[str, np.ndarray], 
                                   corners_3d: List[np.ndarray]) -> Dict[str, Any]:
        """
        Valida la consistencia geométrica del rectángulo.
        
        Args:
            side_vectors: Diccionario con vectores de lados
            corners_3d: Lista de esquinas 3D
            
        Returns:
            Diccionario con métricas de validación
        """
        # 1. Verificar que lados opuestos sean aproximadamente iguales
        top_length = np.linalg.norm(side_vectors['top'])
        bottom_length = np.linalg.norm(side_vectors['bottom'])
        left_length = np.linalg.norm(side_vectors['left'])
        right_length = np.linalg.norm(side_vectors['right'])
        
        horizontal_ratio = min(top_length, bottom_length) / max(top_length, bottom_length)
        vertical_ratio = min(left_length, right_length) / max(left_length, right_length)
        
        # 2. Verificar que los ángulos sean aproximadamente 90°
        angles = []
        for i in range(4):
            v1 = side_vectors[['top', 'right', 'bottom', 'left'][i]]
            v2 = side_vectors[['right', 'bottom', 'left', 'top'][i]]
            
            # Calcular ángulo entre vectores consecutivos
            dot_product = np.dot(v1, v2)
            norms = np.linalg.norm(v1) * np.linalg.norm(v2)
            
            if norms > 0:
                cos_angle = np.clip(dot_product / norms, -1.0, 1.0)
                angle_rad = math.acos(cos_angle)
                angle_deg = math.degrees(angle_rad)
                angles.append(angle_deg)
        
        avg_angle = np.mean(angles)
        angle_std = np.std(angles)
        
        # 3. Calcular planaridad (todos los puntos en el mismo plano)
        # Usar 3 puntos para definir plano y calcular distancia del 4to punto
        tl, tr, br, bl = corners_3d
        
        # Vectores del plano
        v1 = tr - tl
        v2 = bl - tl
        
        # Normal del plano
        normal = np.cross(v1, v2)
        if np.linalg.norm(normal) > 0:
            normal = normal / np.linalg.norm(normal)
            
            # Distancia del 4to punto al plano
            v3 = br - tl
            distance_to_plane = abs(np.dot(v3, normal))
        else:
            distance_to_plane = float('inf')
        
        # Métricas de calidad
        validation = {
            'side_ratios': {
                'horizontal': horizontal_ratio,
                'vertical': vertical_ratio
            },
            'angles': {
                'individual': angles,
                'average': avg_angle,
                'std_deviation': angle_std
            },
            'planarity': {
                'distance_to_plane': distance_to_plane
            },
            'quality_assessment': self._assess_quality(horizontal_ratio, vertical_ratio, avg_angle, angle_std, distance_to_plane)
        }
        
        self._print(f"🔍 Validación geométrica:")
        self._print(f"   Ratios lados paralelos: H={horizontal_ratio:.3f}, V={vertical_ratio:.3f}")
        self._print(f"   Ángulos promedio: {avg_angle:.1f}° ± {angle_std:.1f}°")
        self._print(f"   Planaridad: {distance_to_plane:.4f} m")
        self._print(f"   Calidad: {validation['quality_assessment']['description']}")
        
        return validation
    
    def _assess_quality(self, 
                       h_ratio: float, 
                       v_ratio: float, 
                       avg_angle: float, 
                       angle_std: float, 
                       planarity: float) -> Dict[str, Any]:
        """
        Evalúa la calidad general de la medición.
        
        Args:
            h_ratio, v_ratio: Ratios de lados paralelos
            avg_angle: Ángulo promedio
            angle_std: Desviación estándar de ángulos
            planarity: Error de planaridad
            
        Returns:
            Diccionario con evaluación de calidad
        """
        # Criterios de calidad
        ratio_threshold = 0.95  # Lados paralelos deben ser >95% similares
        angle_threshold = 5.0   # Ángulos deben estar dentro de ±5° de 90°
        std_threshold = 3.0     # Desviación estándar < 3°
        planarity_threshold = 0.1  # Error de planaridad < 10cm
        
        issues = []
        
        if h_ratio < ratio_threshold:
            issues.append(f"Lados horizontales desiguales ({h_ratio:.3f})")
        
        if v_ratio < ratio_threshold:
            issues.append(f"Lados verticales desiguales ({v_ratio:.3f})")
        
        if abs(avg_angle - 90.0) > angle_threshold:
            issues.append(f"Ángulos no rectangulares ({avg_angle:.1f}°)")
        
        if angle_std > std_threshold:
            issues.append(f"Ángulos inconsistentes (σ={angle_std:.1f}°)")
        
        if planarity > planarity_threshold:
            issues.append(f"Baja planaridad ({planarity:.3f}m)")
        
        # Determinar calidad general
        if len(issues) == 0:
            quality = "excellent"
            description = "🎉 Excelente - Rectángulo ideal"
            confidence = 0.95
        elif len(issues) <= 2:
            quality = "good" 
            description = "✅ Buena - Medición confiable"
            confidence = 0.80
        elif len(issues) <= 3:
            quality = "acceptable"
            description = "⚠️ Aceptable - Revisar condiciones"
            confidence = 0.65
        else:
            quality = "poor"
            description = "❌ Pobre - Recalibrar o retomar foto"
            confidence = 0.40
        
        return {
            'quality': quality,
            'description': description,
            'confidence': confidence,
            'issues': issues
        }
    
    def calculate_area(self, corners_3d: List[np.ndarray]) -> Dict[str, Any]:
        """
        Función principal para calcular área completa con validación.
        
        Args:
            corners_3d: Lista de 4 esquinas 3D
            
        Returns:
            Diccionario completo con área y métricas de calidad
        """
        self._print(f"\n📏 CÁLCULO GEOMÉTRICO DE ÁREA")
        self._print("-" * 40)
        
        # Calcular vectores de lados
        side_vectors = self.calculate_side_vectors(corners_3d)
        
        # Calcular dimensiones
        dimensions = self.calculate_dimensions(side_vectors)
        
        # Validar geometría
        validation = self.validate_rectangle_geometry(side_vectors, corners_3d)
        
        # Resultado completo
        result = {
            'area_square_meters': dimensions['area_square_meters'],
            'width_meters': dimensions['width_meters'],
            'height_meters': dimensions['height_meters'],
            'side_lengths': dimensions['side_lengths'],
            'validation': validation,
            'corners_3d': [point.tolist() for point in corners_3d],
            'side_vectors': {k: v.tolist() for k, v in side_vectors.items()}
        }
        
        return result


def calculate_rectangle_area(corners_3d: List[np.ndarray], 
                           verbose: bool = True) -> Dict[str, Any]:
    """
    Función de conveniencia para calcular área de rectángulo 3D.
    
    Args:
        corners_3d: Lista de 4 esquinas 3D
        verbose: Si mostrar mensajes de progreso
        
    Returns:
        Diccionario con área y métricas de validación
    """
    calculator = AreaCalculator(verbose=verbose)
    return calculator.calculate_area(corners_3d)