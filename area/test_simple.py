#!/usr/bin/env python3
"""
🧪 SCRIPT DE PRUEBA SIMPLE - Sistema de Medición de Carteles

Script básico que prueba el sistema con la imagen 0 de calibración.
Mide el tablero de ajedrez completo y compara con dimensiones reales.

Uso:
    python3 test_simple.py

Datos de prueba:
- Imagen: imagen 0 de calibration_images
- Objeto: Tablero de ajedrez 8x8 cuadrados
- Tamaño cuadrado: 26.5 mm
- Distancia: 50 cm
- Área esperada: 0.044944 m² (21.2 cm × 21.2 cm)
"""

import sys
import os
sys.path.append('size_calculator')

from size_calculator.main import CartelAreaMeasurer

def main():
    print("🧪 PRUEBA SIMPLE DEL SISTEMA DE MEDICIÓN DE CARTELES")
    print("=" * 60)
    
    # ==========================================
    # CONFIGURACIÓN DE LA PRUEBA
    # ==========================================
    
    # Archivos
    image_path = "size_calculator/calibration_pipeline/calibration_images/0.jpg"
    calibration_file = "size_calculator/calibration_pipeline/camera_calibration.npz"
    
    # Parámetros del tablero
    distance_meters = 0.50  # 50 cm
    expected_area = 0.044944  # m² (21.2cm × 21.2cm)
    
    # Coordenadas detectadas automáticamente (esquinas externas del tablero)
    corners_str = "1847,947 1864,2610 834,2604 927,973"
    
    print(f"📋 PARÁMETROS:")
    print(f"   🖼️ Imagen: {os.path.basename(image_path)}")
    print(f"   📏 Distancia: {distance_meters} m")
    print(f"   🎯 Área esperada: {expected_area:.6f} m²")
    print(f"   📐 Esquinas: {corners_str}")
    
    # ==========================================
    # VERIFICACIÓN DE ARCHIVOS
    # ==========================================
    
    if not os.path.exists(image_path):
        print(f"❌ Error: No se encontró {image_path}")
        return False
    
    if not os.path.exists(calibration_file):
        print(f"❌ Error: No se encontró {calibration_file}")
        return False
    
    print(f"✅ Archivos verificados")
    
    # ==========================================
    # PARSEAR COORDENADAS
    # ==========================================
    
    try:
        corners = []
        for pair in corners_str.split():
            x, y = map(int, pair.split(','))
            corners.append((x, y))
        print(f"✅ Coordenadas parseadas: {len(corners)} puntos")
    except Exception as e:
        print(f"❌ Error en coordenadas: {e}")
        return False
    
    # ==========================================
    # EJECUTAR MEDICIÓN
    # ==========================================
    
    print(f"\n🚀 EJECUTANDO MEDICIÓN...")
    print("-" * 30)
    
    try:
        # Crear medidor (modo verbose para ver todos los detalles)
        measurer = CartelAreaMeasurer(calibration_file, verbose=True)
        
        # Medir área
        result = measurer.measure_cartel_area(
            image_path=image_path,
            contours=corners,
            distance_meters=distance_meters
        )
        
        # ==========================================
        # MOSTRAR RESULTADOS
        # ==========================================
        
        if result['success']:
            measured_area = result['area_square_meters']
            error = abs(measured_area - expected_area)
            error_percent = (error / expected_area) * 100
            
            print(f"\n🎯 COMPARACIÓN DE RESULTADOS:")
            print(f"   Área medida:   {measured_area:.6f} m²")
            print(f"   Área esperada: {expected_area:.6f} m²")
            print(f"   Error:         {error:.6f} m² ({error_percent:.2f}%)")
            print(f"   Calidad:       {result['quality']['description']}")
            print(f"   Confianza:     {result['quality']['confidence']*100:.1f}%")
            
            # Mostrar corrección de perspectiva si aplica
            if result.get('perspective_info', {}).get('has_perspective'):
                angle = result['perspective_info']['perspective_angle']
                print(f"   Perspectiva:   {angle:.1f}° (corregida automáticamente)")
            
            # Evaluación del resultado
            if error_percent < 10:
                print(f"\n✅ RESULTADO EXCELENTE: Error < 10%")
            elif error_percent < 20:
                print(f"\n✅ RESULTADO BUENO: Error < 20%")
            else:
                print(f"\n⚠️ RESULTADO ACEPTABLE: Error = {error_percent:.1f}%")
            
            return True
        else:
            print(f"❌ Error en medición: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False


if __name__ == "__main__":
    print("📂 Directorio actual:", os.getcwd())
    print("💡 Asegúrate de estar en el directorio padre de 'size_calculator'")
    print()
    
    success = main()
    
    if success:
        print(f"\n🎉 PRUEBA EXITOSA - El sistema funciona correctamente!")
        print(f"💡 Ahora puedes usar el sistema con tus propias imágenes:")
        print(f"   python3 size_calculator/main.py -i tu_imagen.jpg -c \"x1,y1 x2,y2 x3,y3 x4,y4\" -d distancia")
    else:
        print(f"\n❌ PRUEBA FALLÓ - Revisar configuración")