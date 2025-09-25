#!/usr/bin/env python3
"""
Script de prueba del Sistema de Medición de Carteles.

Este script prueba el sistema usando la imagen 0 de calibración,
midiendo el área completa del tablero de ajedrez como caso de prueba.

Datos de prueba:
- Imagen: calibration_images/0.jpg
- Objeto: Tablero de ajedrez completo (8x8 cuadrados)
- Distancia: 50 cm (0.5 metros)
- Dimensiones reales: 212 mm × 212 mm = 0.044944 m²
- Esquinas detectadas automáticamente
"""

import sys
import os
import json
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


def main():
    """Función principal del script de prueba."""
    
    print("🧪 SCRIPT DE PRUEBA - SISTEMA DE MEDICIÓN DE CARTELES")
    print("=" * 65)
    
    # ===========================================
    # CONFIGURACIÓN DE LA PRUEBA
    # ===========================================
    
    # Rutas de archivos
    test_image = "size_calculator/calibration_pipeline/calibration_images/0.jpg"
    calibration_file = "size_calculator/calibration_pipeline/camera_calibration.npz"
    output_file = "test_results.json"
    
    # Parámetros del tablero
    square_size_mm = 26.5
    squares_per_side = 8
    board_size_mm = squares_per_side * square_size_mm
    board_size_m = board_size_mm / 1000.0
    expected_area_m2 = board_size_m ** 2
    
    # Distancia de la prueba
    distance_meters = 0.5  # 50 cm
    
    # Coordenadas del tablero completo (detectadas automáticamente)
    contours_str = "2079,733 704,976 815,2870 1845,2612"
    
    print(f"📋 PARÁMETROS DE PRUEBA:")
    print(f"   🖼️  Imagen: {test_image}")
    print(f"   📏 Distancia: {distance_meters} m")
    print(f"   📐 Esquinas: {contours_str}")
    print(f"   🎯 Área esperada: {expected_area_m2:.6f} m²")
    print(f"   📊 Dimensiones esperadas: {board_size_m:.4f} × {board_size_m:.4f} m")
    
    # ===========================================
    # VERIFICACIÓN DE ARCHIVOS
    # ===========================================
    
    print(f"\n🔍 VERIFICACIÓN DE ARCHIVOS:")
    
    if not os.path.exists(test_image):
        print(f"❌ Error: No se encontró la imagen de prueba: {test_image}")
        return False
    print(f"✅ Imagen de prueba encontrada")
    
    if not os.path.exists(calibration_file):
        print(f"❌ Error: No se encontró el archivo de calibración: {calibration_file}")
        return False
    print(f"✅ Archivo de calibración encontrado")
    
    # ===========================================
    # PARSEAR CONTORNOS
    # ===========================================
    
    try:
        contours = []
        pairs = contours_str.strip().split()
        for pair in pairs:
            x, y = map(int, pair.split(','))
            contours.append((x, y))
        
        print(f"✅ Contornos parseados: {contours}")
        
    except Exception as e:
        print(f"❌ Error parseando contornos: {e}")
        return False
    
    # ===========================================
    # EJECUTAR MEDICIÓN
    # ===========================================
    
    print(f"\n🚀 EJECUTANDO MEDICIÓN...")
    print("-" * 40)
    
    try:
        # Crear medidor
        measurer = CartelAreaMeasurer(calibration_file, verbose=True)
        
        # Realizar medición
        result = measurer.measure_cartel_area(
            image_path=test_image,
            contours=contours,
            distance_meters=distance_meters
        )
        
        # ===========================================
        # ANÁLISIS DE RESULTADOS
        # ===========================================
        
        print(f"\n📊 ANÁLISIS DE RESULTADOS")
        print("=" * 40)
        
        if result['success']:
            measured_area = result['area_square_meters']
            measured_width = result['width_meters']
            measured_height = result['height_meters']
            quality = result['quality']
            
            # Calcular errores
            area_error = abs(measured_area - expected_area_m2)
            area_error_percent = (area_error / expected_area_m2) * 100
            
            width_error = abs(measured_width - board_size_m)
            width_error_percent = (width_error / board_size_m) * 100
            
            height_error = abs(measured_height - board_size_m)
            height_error_percent = (height_error / board_size_m) * 100
            
            print(f"✅ MEDICIÓN EXITOSA")
            print(f"")
            print(f"📏 COMPARACIÓN DE RESULTADOS:")
            print(f"   Área medida:    {measured_area:.6f} m²")
            print(f"   Área esperada:  {expected_area_m2:.6f} m²")
            print(f"   Error área:     {area_error:.6f} m² ({area_error_percent:.2f}%)")
            print(f"")
            print(f"   Ancho medido:   {measured_width:.4f} m")
            print(f"   Ancho esperado: {board_size_m:.4f} m")
            print(f"   Error ancho:    {width_error:.4f} m ({width_error_percent:.2f}%)")
            print(f"")
            print(f"   Alto medido:    {measured_height:.4f} m")
            print(f"   Alto esperado:  {board_size_m:.4f} m")
            print(f"   Error alto:     {height_error:.4f} m ({height_error_percent:.2f}%)")
            print(f"")
            print(f"🎯 CALIDAD: {quality['description']}")
            print(f"🔬 CONFIANZA: {quality['confidence']*100:.1f}%")
            
            # Evaluar precisión de la prueba
            print(f"\n🎯 EVALUACIÓN DE LA PRUEBA:")
            
            if area_error_percent < 5:
                print(f"🎉 EXCELENTE: Error de área < 5%")
            elif area_error_percent < 10:
                print(f"✅ BUENO: Error de área < 10%")
            elif area_error_percent < 20:
                print(f"⚠️  ACEPTABLE: Error de área < 20%")
            else:
                print(f"❌ ALTO ERROR: Error de área > 20%")
            
            if result.get('perspective_info', {}).get('has_perspective'):
                angle = result['perspective_info']['perspective_angle']
                print(f"📐 Perspectiva detectada y corregida: {angle:.1f}°")
            
        else:
            print(f"❌ ERROR EN LA MEDICIÓN: {result.get('error', 'Error desconocido')}")
            return False
        
        # ===========================================
        # GUARDAR RESULTADOS
        # ===========================================
        
        # Agregar información de la prueba al resultado
        result['test_info'] = {
            'test_type': 'chessboard_calibration_image',
            'expected_area_m2': expected_area_m2,
            'expected_dimensions_m': [board_size_m, board_size_m],
            'distance_meters': distance_meters,
            'square_size_mm': square_size_mm,
            'squares_per_side': squares_per_side,
            'area_error_m2': area_error,
            'area_error_percent': area_error_percent,
            'width_error_m': width_error,
            'width_error_percent': width_error_percent,
            'height_error_m': height_error,
            'height_error_percent': height_error_percent
        }
        
        # Guardar resultados detallados
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\n💾 Resultados detallados guardados en: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la medición: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Asegúrate de estar en el directorio padre de 'size_calculator'")
    print("Directorio actual:", os.getcwd())
    print()
    
    success = main()
    
    if success:
        print(f"\n🎉 PRUEBA COMPLETADA EXITOSAMENTE")
    else:
        print(f"\n❌ PRUEBA FALLÓ")
    
    sys.exit(0 if success else 1)