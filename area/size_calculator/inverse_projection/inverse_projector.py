"""
Módulo de proyección inversa 2D a 3D.

Este módulo se encarga de:
1. Convertir coordenadas de píxeles a coordenadas normalizadas
2. Crear rayos 3D desde el centro óptico
3. Intersectar rayos con el plano del cartel usando distancia conocida
4. Aplicar corrección por perspectiva si es necesaria
"""

import numpy as np
import math
from typing import List, Tuple, Dict, Any, Optional


class InverseProjector:
    """
    Proyector inverso que convierte coordenadas 2D en píxeles a coordenadas 3D reales.
    """
    
    def __init__(self, camera_matrix: np.ndarray, verbose: bool = True):
        """
        Inicializa el proyector con parámetros de cámara.
        
        Args:
            camera_matrix: Matriz intrínseca de la cámara (3x3)
            verbose: Si mostrar mensajes de progreso
        """
        self.verbose = verbose
        self.camera_matrix = camera_matrix
        self.fx = camera_matrix[0, 0]  # Distancia focal en x
        self.fy = camera_matrix[1, 1]  # Distancia focal en y  
        self.cx = camera_matrix[0, 2]  # Centro óptico x
        self.cy = camera_matrix[1, 2]  # Centro óptico y
        
        self._print("🎯 Proyector inverso inicializado")
        self._print(f"   📐 Parámetros focales: fx={self.fx:.1f}, fy={self.fy:.1f}")
        self._print(f"   🎯 Centro óptico: ({self.cx:.1f}, {self.cy:.1f})")
    
    def _print(self, message: str):
        """Imprime mensaje solo si verbose=True."""
        if self.verbose:
            print(message)
    
    def pixels_to_normalized_coordinates(self, pixel_coords: List[Tuple[int, int]]) -> List[Tuple[float, float]]:
        """
        Convierte coordenadas de píxeles a coordenadas normalizadas.
        
        Args:
            pixel_coords: Lista de puntos (x, y) en píxeles
            
        Returns:
            Lista de coordenadas normalizadas (x_norm, y_norm)
        """
        normalized_coords = []
        
        for u, v in pixel_coords:
            # Conversión usando matriz de cámara
            x_norm = (u - self.cx) / self.fx
            y_norm = (v - self.cy) / self.fy
            
            normalized_coords.append((x_norm, y_norm))
        
        self._print(f"📍 Convertidos {len(pixel_coords)} puntos a coordenadas normalizadas")
        if self.verbose and len(pixel_coords) <= 4:
            for i, ((u, v), (x, y)) in enumerate(zip(pixel_coords, normalized_coords)):
                self._print(f"   Punto {i+1}: ({u}, {v}) px → ({x:.4f}, {y:.4f}) norm")
        
        return normalized_coords
    
    def create_3d_rays(self, normalized_coords: List[Tuple[float, float]]) -> List[np.ndarray]:
        """
        Crea rayos 3D desde el centro óptico hacia cada punto normalizado.
        
        Args:
            normalized_coords: Lista de coordenadas normalizadas
            
        Returns:
            Lista de vectores de dirección de rayos 3D (normalizados)
        """
        rays = []
        
        for x_norm, y_norm in normalized_coords:
            # Vector de dirección del rayo: (x_norm, y_norm, 1)
            ray_direction = np.array([x_norm, y_norm, 1.0])
            
            # Normalizar el vector (opcional, para consistencia)
            ray_normalized = ray_direction / np.linalg.norm(ray_direction)
            
            rays.append(ray_normalized)
        
        self._print(f"🎯 Creados {len(rays)} rayos 3D")
        
        return rays
    
    def intersect_with_plane(self, 
                           rays: List[np.ndarray], 
                           distance_to_plane: float,
                           plane_normal: Optional[np.ndarray] = None) -> List[np.ndarray]:
        """
        Intersecta rayos con un plano a distancia conocida.
        
        Args:
            rays: Lista de rayos 3D normalizados
            distance_to_plane: Distancia al plano del cartel (metros)
            plane_normal: Normal del plano (por defecto [0,0,1] - perpendicular a cámara)
            
        Returns:
            Lista de puntos 3D de intersección
        """
        if plane_normal is None:
            plane_normal = np.array([0, 0, 1])  # Plano perpendicular a Z
        
        intersection_points = []
        
        for ray in rays:
            # Para plano perpendicular (Z = distance_to_plane):
            # Punto de intersección = origen + t * dirección_rayo
            # donde t = distance_to_plane / ray_z
            
            if abs(ray[2]) < 1e-6:  # Rayo casi paralelo al plano
                raise ValueError("❌ Rayo paralelo al plano - no hay intersección")
            
            # Calcular parámetro t para intersección
            t = distance_to_plane / ray[2]
            
            # Punto de intersección 3D
            intersection_point = t * ray
            
            intersection_points.append(intersection_point)
        
        self._print(f"✅ Calculadas {len(intersection_points)} intersecciones 3D")
        self._print(f"   📏 Distancia al plano: {distance_to_plane:.2f} m")
        
        return intersection_points
    
    def apply_perspective_correction(self, 
                                   points_3d: List[np.ndarray], 
                                   perspective_angle: float) -> List[np.ndarray]:
        """
        Aplica corrección por perspectiva a puntos 3D.
        
        Args:
            points_3d: Lista de puntos 3D sin corregir
            perspective_angle: Ángulo de perspectiva en grados
            
        Returns:
            Lista de puntos 3D corregidos por perspectiva
        """
        if abs(perspective_angle) < 1.0:  # Menos de 1 grado - no corregir
            self._print("✅ Ángulo de perspectiva mínimo - no se aplica corrección")
            return points_3d
        
        # Factor de corrección basado en el coseno del ángulo
        correction_factor = 1.0 / math.cos(math.radians(abs(perspective_angle)))
        
        corrected_points = []
        
        for point in points_3d:
            # Aplicar corrección principalmente en el plano XY
            corrected_point = point.copy()
            
            # La corrección depende de la posición relativa al centro
            # Puntos más alejados del centro se corrigen más
            distance_from_center = math.sqrt(point[0]**2 + point[1]**2)
            
            if distance_from_center > 0:
                # Aplicar corrección proporcional a la distancia del centro
                scale_factor = 1 + (correction_factor - 1) * (distance_from_center / 2.0)
                corrected_point[0] *= scale_factor
                corrected_point[1] *= scale_factor
            
            corrected_points.append(corrected_point)
        
        self._print(f"🔧 Aplicada corrección de perspectiva")
        self._print(f"   📐 Ángulo: {perspective_angle:.1f}°")
        self._print(f"   📊 Factor base: {correction_factor:.3f}")
        
        return corrected_points
    
    def project_to_3d(self, 
                     pixel_coords: List[Tuple[int, int]], 
                     distance_meters: float,
                     perspective_angle: float = 0.0) -> List[np.ndarray]:
        """
        Función completa de proyección 2D → 3D.
        
        Args:
            pixel_coords: Lista de puntos en píxeles
            distance_meters: Distancia al cartel en metros
            perspective_angle: Ángulo de perspectiva para corrección
            
        Returns:
            Lista de puntos 3D corregidos
        """
        self._print(f"\n🚀 PROYECCIÓN INVERSA 2D → 3D")
        self._print("-" * 40)
        
        # Paso 1: Coordenadas normalizadas
        normalized_coords = self.pixels_to_normalized_coordinates(pixel_coords)
        
        # Paso 2: Crear rayos 3D
        rays = self.create_3d_rays(normalized_coords)
        
        # Paso 3: Intersección con plano
        points_3d = self.intersect_with_plane(rays, distance_meters)
        
        # Paso 4: Corrección por perspectiva
        corrected_points_3d = self.apply_perspective_correction(points_3d, perspective_angle)
        
        return corrected_points_3d


def project_pixels_to_3d(pixel_coords: List[Tuple[int, int]], 
                        camera_matrix: np.ndarray,
                        distance_meters: float,
                        perspective_angle: float = 0.0,
                        verbose: bool = True) -> List[np.ndarray]:
    """
    Función de conveniencia para proyección completa 2D → 3D.
    
    Args:
        pixel_coords: Lista de puntos en píxeles
        camera_matrix: Matriz intrínseca de cámara
        distance_meters: Distancia al cartel en metros
        perspective_angle: Ángulo de perspectiva para corrección
        verbose: Si mostrar mensajes de progreso
        
    Returns:
        Lista de puntos 3D en metros
    """
    projector = InverseProjector(camera_matrix, verbose=verbose)
    return projector.project_to_3d(pixel_coords, distance_meters, perspective_angle)