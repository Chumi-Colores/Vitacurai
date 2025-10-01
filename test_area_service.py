#!/usr/bin/env python3
"""
Script de prueba para el servicio de cálculo de área.

Este script permite probar el AreaCalculationService con datos de ejemplo.
"""

import sys
import os
from pathlib import Path
import json

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Importar el servicio
from api.services.area.area_calculation_service import AreaCalculationService


def test_area_calculation():
    """Prueba el servicio de cálculo de área con datos de ejemplo."""
    
    print("🧪 PRUEBA DEL SERVICIO DE CÁLCULO DE ÁREA")
    print("=" * 50)
    
    # Crear instancia del servicio
    service = AreaCalculationService(verbose=True)
    
    # Parámetros de prueba (similares a los obtenidos del sistema de calibración)
    test_data = {
        "image_data": "area/size_calculator/calibration_pipeline/calibration_images/0.jpg",
        "vertices": [
            [200, 150],    # Esquina superior izquierda
            [600, 180],    # Esquina superior derecha  
            [580, 420],    # Esquina inferior derecha
            [180, 390]     # Esquina inferior izquierda
        ],
        "physical_distance": 1.5,  # 1.5 metros
        "focal_length": (3074.1, 3080.8),  # fx, fy del ejemplo anterior
        "optical_center": (1511.8, 2007.4),  # cx, cy del ejemplo anterior
        "distortion_coefs": [-0.123, 0.045, -0.001, 0.002, -0.012]  # Ejemplo
    }
    
    print(f"🔧 Parámetros de prueba:")
    print(f"   📍 Vértices: {test_data['vertices']}")
    print(f"   📏 Distancia: {test_data['physical_distance']} m")
    print(f"   🔍 Focal length: {test_data['focal_length']}")
    print(f"   🎯 Centro óptico: {test_data['optical_center']}")
    
    # Validar parámetros
    validation = service.validate_parameters(
        vertices=test_data['vertices'],
        physical_distance=test_data['physical_distance'],
        focal_length=test_data['focal_length'],
        optical_center=test_data['optical_center'],
        distortion_coefs=test_data['distortion_coefs']
    )
    
    if not validation['valid']:
        print(f"❌ Error en validación: {validation['error']}")
        return
    
    print(f"✅ Validación exitosa: {validation['message']}")
    
    # Ejecutar cálculo de área
    result = service.calculate_cartel_area(**test_data)
    
    # Mostrar resultado
    print(f"\n🎯 RESULTADO FINAL:")
    print("=" * 30)
    
    if result['success']:
        print(f"✅ Cálculo exitoso!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Formato específico solicitado
        print(f"\n📋 FORMATO SOLICITADO:")
        print(f"📊 Área del cartel: {result['area_square_meters']:.4f} m²")
        print(f"📏 Alto: {result['height_meters']:.3f} m")  
        print(f"📏 Ancho: {result['width_meters']:.3f} m")
        
        ratios = result['parallel_sides_ratios']
        print(f"📐 Ratios lados paralelos: H={ratios['horizontal']}, V={ratios['vertical']}")
        
        angles = result['average_angles']
        print(f"📐 Ángulos promedio: {angles['mean']:.1f}° ± {angles['std_deviation']:.1f}°")
        
        quality = result['quality']
        print(f"🎯 Calidad: {quality['description']}")
        print(f"🔬 Confianza: {quality['confidence_percent']:.1f}%")
        
    else:
        print(f"❌ Error en cálculo: {result['error']}")


def test_with_different_parameters():
    """Prueba con diferentes parámetros para validar robustez."""
    
    print(f"\n🧪 PRUEBA CON PARÁMETROS ALTERNATIVOS")
    print("=" * 45)
    
    service = AreaCalculationService(verbose=False)
    
    # Parámetros alternativos
    alt_data = {
        "image_data": "area/size_calculator/calibration_pipeline/calibration_images/1.jpg",
        "vertices": [
            [100, 100],    # Rectángulo más simple
            [400, 100],      
            [400, 300],    
            [100, 300]     
        ],
        "physical_distance": 2.0,  
        "focal_length": (800, 800),  # Focal length más típica
        "optical_center": (320, 240),  # Centro típico para 640x480
        "distortion_coefs": [0.0, 0.0, 0.0, 0.0, 0.0]  # Sin distorsión
    }
    
    result = service.calculate_cartel_area(**alt_data)
    
    if result['success']:
        print(f"✅ Segunda prueba exitosa!")
        print(f"📊 Área: {result['area_square_meters']:.4f} m²")
        print(f"📏 Dimensiones: {result['width_meters']:.3f} × {result['height_meters']:.3f} m")
        print(f"🎯 Calidad: {result['quality']['description']}")
    else:
        print(f"❌ Error en segunda prueba: {result['error']}")


if __name__ == "__main__":
    try:
        test_area_calculation()
        test_with_different_parameters()
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
