#!/usr/bin/env python3
"""
Script de prueba mejorado del Sistema de Medición de Carteles.

Esta versión incluye:
1. Prueba con detección automática del tablero más precisa
2. Análisis de múltiples imágenes de calibración
3. Comparación de resultados con y sin corrección de perspectiva
4. Recomendaciones para mejorar la precisión
"""

import sys
import os
import json
import cv2
import numpy as np
from pathlib import Path

# Agregar el path del sistema de medición
sys.path.append('size_calculator')

try:
    from size_calculator.main import CartelAreaMeasurer
    print("✅ Módulos del sistema cargados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("Asegúrate de estar ejecutando desde el directorio correcto")
    sys.exit(1)


def detect_chessboard_corners(image_path, pattern_size=(8, 5)):
    """
    Detecta automáticamente las esquinas del tablero de ajedrez.
    
    Args:
        image_path: Ruta a la imagen
        pattern_size: Tamaño del patrón interno (esquinas)
        
    Returns:
        Lista de 4 esquinas del tablero completo o None
    """
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detectar esquinas internas del tablero
    ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)
    
    if ret:
        # Refinar esquinas
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        
        # Obtener esquinas del tablero completo
        corners = corners.reshape(-1, 2)
        
        # Las esquinas internas detectadas forman un grid de (pattern_size)
        # Necesitamos extrapolar a las esquinas externas del tablero
        
        # Esquinas de las cuatro esquinas del grid interno
        top_left = corners[0]
        top_right = corners[pattern_size[0] - 1]
        bottom_left = corners[-pattern_size[0]]
        bottom_right = corners[-1]
        
        # Estimar el tamaño de medio cuadrado para extrapolar
        square_size_x = abs(top_right[0] - top_left[0]) / (pattern_size[0] - 1)
        square_size_y = abs(bottom_left[1] - top_left[1]) / (pattern_size[1] - 1)
        
        # Extrapolar a las esquinas externas
        external_tl = (top_left[0] - square_size_x/2, top_left[1] - square_size_y/2)
        external_tr = (top_right[0] + square_size_x/2, top_right[1] - square_size_y/2)
        external_br = (bottom_right[0] + square_size_x/2, bottom_right[1] + square_size_y/2)
        external_bl = (bottom_left[0] - square_size_x/2, bottom_left[1] + square_size_y/2)
        
        # Convertir a enteros
        external_corners = [
            (int(external_tl[0]), int(external_tl[1])),
            (int(external_tr[0]), int(external_tr[1])),
            (int(external_br[0]), int(external_br[1])),
            (int(external_bl[0]), int(external_bl[1]))
        ]
        
        return external_corners
    
    return None


def test_single_image(image_path, measurer, expected_area, board_size_m, distance_m, image_name):
    """
    Prueba el sistema con una sola imagen.
    
    Returns:
        Diccionario con resultados de la prueba
    """
    print(f"\n🧪 PROBANDO IMAGEN: {image_name}")
    print("-" * 50)
    
    # Detectar automáticamente las esquinas del tablero
    corners = detect_chessboard_corners(image_path)
    
    if corners is None:
        print(f"❌ No se pudo detectar el tablero automáticamente en {image_name}")
        return None
    
    print(f"✅ Tablero detectado automáticamente")
    print(f"   Esquinas: {corners}")
    
    # Convertir esquinas a string
    corners_str = " ".join([f"{x},{y}" for x, y in corners])
    
    try:
        # Realizar medición
        result = measurer.measure_cartel_area(
            image_path=image_path,
            contours=corners,
            distance_meters=distance_m
        )
        
        if result['success']:
            measured_area = result['area_square_meters']
            area_error = abs(measured_area - expected_area)
            area_error_percent = (area_error / expected_area) * 100
            
            perspective_angle = result.get('perspective_info', {}).get('perspective_angle', 0)
            has_perspective = result.get('perspective_info', {}).get('has_perspective', False)
            
            test_result = {
                'image_name': image_name,
                'success': True,
                'measured_area': measured_area,
                'expected_area': expected_area,
                'area_error_percent': area_error_percent,
                'perspective_angle': perspective_angle,
                'has_perspective': has_perspective,
                'quality': result['quality']['quality'],
                'confidence': result['quality']['confidence'],
                'corners_detected': corners,
                'full_result': result
            }
            
            print(f"✅ Medición exitosa:")
            print(f"   Área medida: {measured_area:.6f} m²")
            print(f"   Error: {area_error_percent:.2f}%")
            print(f"   Calidad: {result['quality']['quality'].upper()}")
            if has_perspective:
                print(f"   Perspectiva: {perspective_angle:.1f}° (corregida)")
            
            return test_result
            
        else:
            print(f"❌ Error en medición: {result.get('error')}")
            return {
                'image_name': image_name,
                'success': False,
                'error': result.get('error')
            }
            
    except Exception as e:
        print(f"❌ Excepción durante prueba: {e}")
        return {
            'image_name': image_name,
            'success': False,
            'error': str(e)
        }


def main():
    """Función principal del script de prueba mejorado."""
    
    print("🧪 SCRIPT DE PRUEBA MEJORADO - SISTEMA DE MEDICIÓN DE CARTELES")
    print("=" * 70)
    
    # Configuración
    calibration_file = "size_calculator/calibration_pipeline/camera_calibration.npz"
    images_dir = "size_calculator/calibration_pipeline/calibration_images"
    output_file = "test_results_improved.json"
    
    # Parámetros del tablero
    square_size_mm = 26.5
    squares_per_side = 8
    board_size_m = (squares_per_side * square_size_mm) / 1000.0
    expected_area_m2 = board_size_m ** 2
    distance_meters = 0.5  # 50 cm
    
    print(f"📋 CONFIGURACIÓN:")
    print(f"   📁 Directorio imágenes: {images_dir}")
    print(f"   📏 Distancia: {distance_meters} m")
    print(f"   🎯 Área esperada: {expected_area_m2:.6f} m²")
    print(f"   📊 Dimensiones esperadas: {board_size_m:.4f} × {board_size_m:.4f} m")
    
    # Verificar archivos
    if not os.path.exists(calibration_file):
        print(f"❌ Error: No se encontró el archivo de calibración: {calibration_file}")
        return False
    
    if not os.path.exists(images_dir):
        print(f"❌ Error: No se encontró el directorio de imágenes: {images_dir}")
        return False
    
    # Crear medidor
    try:
        measurer = CartelAreaMeasurer(calibration_file, verbose=False)  # Modo silencioso para pruebas múltiples
    except Exception as e:
        print(f"❌ Error creando medidor: {e}")
        return False
    
    # Buscar imágenes de prueba
    test_images = []
    for i in range(5):  # Probar primeras 5 imágenes
        img_path = os.path.join(images_dir, f"{i}.jpg")
        if os.path.exists(img_path):
            test_images.append((img_path, f"imagen_{i}.jpg"))
    
    if not test_images:
        print("❌ No se encontraron imágenes de prueba")
        return False
    
    print(f"\n🔍 ENCONTRADAS {len(test_images)} IMÁGENES PARA PROBAR")
    
    # Ejecutar pruebas
    all_results = []
    successful_tests = []
    
    for img_path, img_name in test_images:
        result = test_single_image(
            img_path, measurer, expected_area_m2, 
            board_size_m, distance_meters, img_name
        )
        
        if result:
            all_results.append(result)
            if result['success']:
                successful_tests.append(result)
    
    # Análisis de resultados
    print(f"\n📊 ANÁLISIS GENERAL DE RESULTADOS")
    print("=" * 50)
    
    if successful_tests:
        errors = [test['area_error_percent'] for test in successful_tests]
        angles = [test['perspective_angle'] for test in successful_tests if test['has_perspective']]
        
        avg_error = np.mean(errors)
        min_error = np.min(errors)
        max_error = np.max(errors)
        std_error = np.std(errors)
        
        print(f"✅ Pruebas exitosas: {len(successful_tests)}/{len(all_results)}")
        print(f"")
        print(f"📊 ESTADÍSTICAS DE ERROR:")
        print(f"   Error promedio: {avg_error:.2f}%")
        print(f"   Error mínimo:   {min_error:.2f}%")
        print(f"   Error máximo:   {max_error:.2f}%")
        print(f"   Desv. estándar: {std_error:.2f}%")
        
        if angles:
            avg_angle = np.mean(angles)
            print(f"\n📐 PERSPECTIVA:")
            print(f"   Imágenes con perspectiva: {len(angles)}/{len(successful_tests)}")
            print(f"   Ángulo promedio: {avg_angle:.1f}°")
        
        # Categorizar resultados
        excellent = [t for t in successful_tests if t['area_error_percent'] < 5]
        good = [t for t in successful_tests if 5 <= t['area_error_percent'] < 15]
        acceptable = [t for t in successful_tests if 15 <= t['area_error_percent'] < 30]
        poor = [t for t in successful_tests if t['area_error_percent'] >= 30]
        
        print(f"\n🎯 CLASIFICACIÓN DE CALIDAD:")
        print(f"   🎉 Excelente (<5% error):    {len(excellent)} pruebas")
        print(f"   ✅ Buena (5-15% error):      {len(good)} pruebas")
        print(f"   ⚠️  Aceptable (15-30% error): {len(acceptable)} pruebas")
        print(f"   ❌ Pobre (>30% error):       {len(poor)} pruebas")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        if avg_error > 20:
            print(f"   📐 Alta variabilidad en perspectiva - usar imágenes más frontales")
            print(f"   📏 Verificar precisión de la distancia medida")
        if std_error > 10:
            print(f"   🎯 Alta variabilidad - mejorar detección de esquinas")
        if len(angles) / len(successful_tests) > 0.7:
            print(f"   📷 Muchas imágenes con perspectiva - tomar fotos más perpendiculares")
        
        if avg_error < 10:
            print(f"   ✅ Sistema funcionando bien - precisión aceptable")
    
    else:
        print(f"❌ No se completaron pruebas exitosas")
    
    # Guardar resultados
    summary = {
        'test_config': {
            'expected_area_m2': expected_area_m2,
            'board_size_m': board_size_m,
            'distance_meters': distance_meters,
            'images_tested': len(all_results),
            'successful_tests': len(successful_tests)
        },
        'statistics': {
            'avg_error_percent': avg_error if successful_tests else None,
            'min_error_percent': min_error if successful_tests else None,
            'max_error_percent': max_error if successful_tests else None,
            'std_error_percent': std_error if successful_tests else None,
            'avg_perspective_angle': np.mean(angles) if angles else None
        },
        'individual_results': all_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\n💾 Resultados completos guardados en: {output_file}")
    
    return len(successful_tests) > 0


if __name__ == "__main__":
    print("Asegúrate de estar en el directorio padre de 'size_calculator'")
    print("Directorio actual:", os.getcwd())
    print()
    
    success = main()
    
    if success:
        print(f"\n🎉 PRUEBAS COMPLETADAS - Revisar resultados detallados")
    else:
        print(f"\n❌ PRUEBAS FALLARON")
    
    sys.exit(0 if success else 1)