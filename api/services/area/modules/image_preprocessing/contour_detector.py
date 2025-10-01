"""
Módulo de detección y validación de contornos rectangulares.

Este módulo se encarga de:
1. Validar que los contornos formen un rectángulo (4 puntos)
2. Ordenar las esquinas en orden consistente
3. Detectar formas trapeciales causadas por perspectiva
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import math


class ContourDetector:
    """
    Detector y validador de contornos rectangulares.
    """
    
    def __init__(self, verbose: bool = True):
        """
        Inicializa el detector de contornos.
        
        Args:
            verbose: Si mostrar mensajes de progreso
        """
        self.verbose = verbose
    
    def _print(self, message: str):
        """Imprime mensaje solo si verbose=True."""
        if self.verbose:
            print(message)
    
    def validate_contours(self, contours: List[Tuple[int, int]]) -> bool:
        """
        Valida que los contornos sean válidos para un rectángulo.
        
        Args:
            contours: Lista de 4 puntos (x, y) del rectángulo
            
        Returns:
            True si son válidos, False en caso contrario
        """
        if len(contours) != 4:
            self._print(f"❌ Error: Se esperan 4 esquinas, se recibieron {len(contours)}")
            return False
        
        # Verificar que todos los puntos sean diferentes
        unique_points = set(contours)
        if len(unique_points) != 4:
            self._print("❌ Error: Hay puntos duplicados en los contornos")
            return False
        
        # Verificar que los puntos formen un cuadrilátero válido
        if not self._is_valid_quadrilateral(contours):
            self._print("❌ Error: Los puntos no forman un cuadrilátero válido")
            return False
        
        self._print("✅ Contornos válidos")
        return True
    
    def _is_valid_quadrilateral(self, points: List[Tuple[int, int]]) -> bool:
        """
        Verifica que 4 puntos formen un cuadrilátero válido.
        
        Args:
            points: Lista de 4 puntos
            
        Returns:
            True si es válido
        """
        # Convertir a numpy array para cálculos
        pts = np.array(points, dtype=np.float32)
        
        # Calcular área usando la fórmula de Shoelace
        area = cv2.contourArea(pts)
        
        # El área debe ser positiva y significativa
        if area < 100:  # Área mínima de 100 píxeles
            return False
        
        return True
    
    def order_corners(self, contours: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Ordena las esquinas en orden: top-left, top-right, bottom-right, bottom-left.
        
        Args:
            contours: Lista de 4 puntos desordenados
            
        Returns:
            Lista de 4 puntos ordenados
        """
        # Convertir a numpy array
        pts = np.array(contours, dtype=np.float32)
        
        # Ordenar puntos
        # Suma: top-left tendrá la suma más pequeña, bottom-right la más grande
        sum_coords = pts.sum(axis=1)
        top_left = pts[np.argmin(sum_coords)]
        bottom_right = pts[np.argmax(sum_coords)]
        
        # Diferencia: top-right tendrá diferencia negativa mínima, bottom-left positiva máxima  
        diff_coords = np.diff(pts, axis=1)
        top_right = pts[np.argmin(diff_coords)]
        bottom_left = pts[np.argmax(diff_coords)]
        
        ordered = [
            tuple(map(int, top_left)),
            tuple(map(int, top_right)), 
            tuple(map(int, bottom_right)),
            tuple(map(int, bottom_left))
        ]
        
        self._print(f"📐 Esquinas ordenadas: TL{ordered[0]} TR{ordered[1]} BR{ordered[2]} BL{ordered[3]}")
        
        return ordered
    
    def detect_perspective_distortion(self, corners: List[Tuple[int, int]]) -> Dict[str, Any]:
        """
        Detecta distorsión perspectiva analizando la forma trapecial.
        
        Args:
            corners: Lista ordenada de 4 esquinas [TL, TR, BR, BL]
            
        Returns:
            Diccionario con información de perspectiva
        """
        tl, tr, br, bl = corners
        
        # Calcular longitudes de lados opuestos
        top_length = self._distance(tl, tr)
        bottom_length = self._distance(bl, br) 
        left_length = self._distance(tl, bl)
        right_length = self._distance(tr, br)
        
        # Calcular ratios de lados paralelos
        horizontal_ratio = min(top_length, bottom_length) / max(top_length, bottom_length)
        vertical_ratio = min(left_length, right_length) / max(left_length, right_length)
        
        # Detectar perspectiva significativa (umbral: ratio < 0.9)
        has_perspective = horizontal_ratio < 0.9 or vertical_ratio < 0.9
        
        # Estimar ángulo de inclinación
        perspective_angle = 0.0
        if has_perspective:
            # Usar el ratio más distorsionado para estimar el ángulo
            min_ratio = min(horizontal_ratio, vertical_ratio)
            # Aproximación: angle ≈ arccos(ratio)
            perspective_angle = math.degrees(math.acos(min_ratio))
        
        result = {
            'has_perspective': has_perspective,
            'horizontal_ratio': horizontal_ratio,
            'vertical_ratio': vertical_ratio, 
            'perspective_angle': perspective_angle,
            'confidence': 'high' if not has_perspective else 'medium',
            'side_lengths': {
                'top': top_length,
                'bottom': bottom_length,
                'left': left_length, 
                'right': right_length
            }
        }
        
        if has_perspective:
            self._print(f"⚠️  Perspectiva detectada: {perspective_angle:.1f}° (ratio: {min_ratio:.3f})")
        else:
            self._print("✅ No se detectó perspectiva significativa")
            
        return result
    
    def _distance(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        """
        Calcula distancia euclidiana entre dos puntos.
        
        Args:
            p1, p2: Puntos (x, y)
            
        Returns:
            Distancia en píxeles
        """
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def validate_and_order_contours(contours: List[Tuple[int, int]], 
                               verbose: bool = True) -> Optional[Tuple[List[Tuple[int, int]], Dict[str, Any]]]:
    """
    Función de conveniencia para validar, ordenar y analizar contornos.
    
    Args:
        contours: Lista de puntos del rectángulo
        verbose: Si mostrar mensajes de progreso
        
    Returns:
        Tupla de (esquinas_ordenadas, info_perspectiva) o None si inválido
    """
    detector = ContourDetector(verbose=verbose)
    
    # Validar contornos
    if not detector.validate_contours(contours):
        return None
    
    # Ordenar esquinas
    ordered_corners = detector.order_corners(contours)
    
    # Detectar perspectiva
    perspective_info = detector.detect_perspective_distortion(ordered_corners)
    
    return ordered_corners, perspective_info