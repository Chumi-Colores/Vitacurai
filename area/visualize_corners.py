#!/usr/bin/env python3
"""
🎯 VISUALIZADOR DE ESQUINAS DETECTADAS

Este script crea una imagen con puntos marcados en las esquinas detectadas
para verificar visualmente que el sistema está seleccionando correctamente
las coordenadas del cartel/tablero.

Características:
- Marca las esquinas detectadas con colores diferentes
- Numera las esquinas en orden
- Muestra las coordenadas de cada punto
- Dibuja las líneas del rectángulo
- Guarda imagen de verificación

Uso:
    python3 visualize_corners.py
"""

import sys
import os
import cv2
import numpy as np
sys.path.append('size_calculator')

from size_calculator.image_preprocessing import validate_and_order_contours, correct_image_and_contours


def visualize_corners(image_path, corners, output_path="corners_visualization.jpg", 
                     show_corrected=True, calibration_file=None):
    """
    Crea una visualización de las esquinas detectadas.
    
    Args:
        image_path: Ruta a la imagen original
        corners: Lista de tuplas (x, y) con las coordenadas
        output_path: Ruta donde guardar la imagen visualizada
        show_corrected: Si mostrar también las coordenadas corregidas por distorsión
        calibration_file: Archivo de calibración para corrección de distorsión
        
    Returns:
        True si se creó exitosamente, False en caso contrario
    """
    try:
        # Cargar imagen original
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Error: No se pudo cargar la imagen {image_path}")
            return False
        
        print(f"✅ Imagen cargada: {image.shape}")
        
        # Crear copia para trabajar
        vis_image = image.copy()
        
        # Validar y ordenar contornos
        result = validate_and_order_contours(corners, verbose=True)
        if result is None:
            print("❌ Error: Contornos inválidos")
            return False
        
        ordered_corners, perspective_info = result
        
        # Colores para cada esquina (BGR format)
        colors = [
            (0, 255, 0),    # Verde - Top Left
            (255, 0, 0),    # Azul - Top Right  
            (0, 0, 255),    # Rojo - Bottom Right
            (0, 255, 255),  # Amarillo - Bottom Left
        ]
        
        # Etiquetas para cada esquina
        labels = ["TL", "TR", "BR", "BL"]
        
        print(f"\n🎨 DIBUJANDO VISUALIZACIÓN:")
        print(f"   📍 Esquinas originales: {corners}")
        print(f"   📐 Esquinas ordenadas: {ordered_corners}")
        
        # Dibujar líneas del rectángulo (antes de los puntos para que queden debajo)
        for i in range(4):
            pt1 = ordered_corners[i]
            pt2 = ordered_corners[(i + 1) % 4]
            cv2.line(vis_image, pt1, pt2, (255, 255, 255), 3)  # Línea blanca gruesa
            cv2.line(vis_image, pt1, pt2, (0, 0, 0), 2)        # Línea negra más fina encima
        
        # Dibujar esquinas originales
        for i, (corner, color, label) in enumerate(zip(ordered_corners, colors, labels)):
            x, y = corner
            
            # Círculo grande para la esquina
            cv2.circle(vis_image, (x, y), 15, color, -1)
            cv2.circle(vis_image, (x, y), 15, (0, 0, 0), 2)  # Borde negro
            
            # Número de la esquina
            cv2.putText(vis_image, str(i+1), (x-8, y+5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Etiqueta de posición
            label_pos = (x + 25, y - 10)
            cv2.putText(vis_image, f"{label}", label_pos,
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Coordenadas
            coord_text = f"({x},{y})"
            coord_pos = (x + 25, y + 15)
            cv2.putText(vis_image, coord_text, coord_pos,
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(vis_image, coord_text, coord_pos,
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Información de perspectiva
        if perspective_info['has_perspective']:
            angle = perspective_info['perspective_angle']
            status_text = f"Perspectiva: {angle:.1f}°"
            status_color = (0, 165, 255)  # Naranja
        else:
            status_text = "Sin perspectiva"
            status_color = (0, 255, 0)  # Verde
        
        # Dibujar información en la imagen
        cv2.putText(vis_image, status_text, (30, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, status_color, 2)
        
        # Título
        title = f"Esquinas Detectadas - {os.path.basename(image_path)}"
        cv2.putText(vis_image, title, (30, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(vis_image, title, (30, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
        
        # Si se proporciona calibración, mostrar también coordenadas corregidas
        if show_corrected and calibration_file and os.path.exists(calibration_file):
            try:
                print(f"🔧 Generando visualización con corrección de distorsión...")
                
                # Obtener coordenadas corregidas
                corrected_image, corrected_contours, camera_params = correct_image_and_contours(
                    image_path, ordered_corners, calibration_file, verbose=False
                )
                
                # Crear segunda imagen con coordenadas corregidas
                vis_corrected = corrected_image.copy()
                
                # Dibujar líneas del rectángulo corregido
                for i in range(4):
                    pt1 = corrected_contours[i]
                    pt2 = corrected_contours[(i + 1) % 4]
                    cv2.line(vis_corrected, pt1, pt2, (255, 255, 255), 3)
                    cv2.line(vis_corrected, pt1, pt2, (0, 0, 0), 2)
                
                # Dibujar esquinas corregidas
                for i, (corner, color, label) in enumerate(zip(corrected_contours, colors, labels)):
                    x, y = corner
                    
                    cv2.circle(vis_corrected, (x, y), 15, color, -1)
                    cv2.circle(vis_corrected, (x, y), 15, (0, 0, 0), 2)
                    
                    cv2.putText(vis_corrected, str(i+1), (x-8, y+5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    
                    label_pos = (x + 25, y - 10)
                    cv2.putText(vis_corrected, f"{label}", label_pos,
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    
                    coord_text = f"({x},{y})"
                    coord_pos = (x + 25, y + 15)
                    cv2.putText(vis_corrected, coord_text, coord_pos,
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    cv2.putText(vis_corrected, coord_text, coord_pos,
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                
                # Título para imagen corregida
                title_corrected = f"Coordenadas Corregidas - {os.path.basename(image_path)}"
                cv2.putText(vis_corrected, title_corrected, (30, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(vis_corrected, title_corrected, (30, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
                
                # Combinar imágenes lado a lado
                h1, w1 = vis_image.shape[:2]
                h2, w2 = vis_corrected.shape[:2]
                
                # Redimensionar para que tengan la misma altura
                if h1 != h2:
                    if h1 > h2:
                        vis_corrected = cv2.resize(vis_corrected, (int(w2 * h1 / h2), h1))
                    else:
                        vis_image = cv2.resize(vis_image, (int(w1 * h2 / h1), h2))
                
                # Concatenar horizontalmente
                combined = np.hstack([vis_image, vis_corrected])
                
                # Agregar separador
                separator = np.ones((combined.shape[0], 5, 3), dtype=np.uint8) * 255
                combined = np.hstack([vis_image, separator, vis_corrected])
                
                vis_image = combined
                
                print(f"✅ Visualización combinada creada")
                
            except Exception as e:
                print(f"⚠️ No se pudo generar visualización corregida: {e}")
                print(f"   Usando solo visualización original")
        
        # Guardar imagen
        success = cv2.imwrite(output_path, vis_image)
        
        if success:
            print(f"💾 Imagen guardada: {output_path}")
            print(f"   📏 Dimensiones: {vis_image.shape}")
            
            # Mostrar resumen
            print(f"\n📊 RESUMEN DE ESQUINAS:")
            for i, (corner, label) in enumerate(zip(ordered_corners, labels)):
                color_name = ["Verde", "Azul", "Rojo", "Amarillo"][i]
                print(f"   {i+1}. {label} {corner} - {color_name}")
            
            if perspective_info['has_perspective']:
                print(f"\n📐 PERSPECTIVA DETECTADA:")
                print(f"   Ángulo: {perspective_info['perspective_angle']:.1f}°")
                print(f"   Ratio horizontal: {perspective_info['horizontal_ratio']:.3f}")
                print(f"   Ratio vertical: {perspective_info['vertical_ratio']:.3f}")
            else:
                print(f"\n✅ SIN PERSPECTIVA SIGNIFICATIVA")
            
            return True
        else:
            print(f"❌ Error guardando imagen")
            return False
            
    except Exception as e:
        print(f"❌ Error en visualización: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal del visualizador."""
    
    print("🎯 VISUALIZADOR DE ESQUINAS DETECTADAS")
    print("=" * 50)
    
    # Configuración de la prueba (usando los mismos datos del test)
    image_path = "size_calculator/calibration_pipeline/calibration_images/0.jpg"
    calibration_file = "size_calculator/calibration_pipeline/camera_calibration.npz"
    output_path = "corners_visualization.jpg"
    
    # Coordenadas detectadas automáticamente (las mejores del test)
    corners = [(1847, 947), (1864, 2610), (834, 2604), (927, 973)]
    
    print(f"📋 CONFIGURACIÓN:")
    print(f"   🖼️ Imagen: {os.path.basename(image_path)}")
    print(f"   📍 Esquinas: {corners}")
    print(f"   💾 Salida: {output_path}")
    
    # Verificar archivos
    if not os.path.exists(image_path):
        print(f"❌ Error: No se encontró {image_path}")
        return False
    
    print(f"✅ Archivos verificados")
    
    # Crear visualización
    success = visualize_corners(
        image_path=image_path,
        corners=corners,
        output_path=output_path,
        show_corrected=True,
        calibration_file=calibration_file
    )
    
    if success:
        print(f"\n🎉 VISUALIZACIÓN CREADA EXITOSAMENTE")
        print(f"📂 Revisa el archivo: {output_path}")
        print(f"")
        print(f"💡 CÓMO INTERPRETAR LA IMAGEN:")
        print(f"   🟢 Punto 1 (Verde) = Top Left (TL)")
        print(f"   🔵 Punto 2 (Azul) = Top Right (TR)")  
        print(f"   🔴 Punto 3 (Rojo) = Bottom Right (BR)")
        print(f"   🟡 Punto 4 (Amarillo) = Bottom Left (BL)")
        print(f"   ⬜ Líneas blancas = Contorno del rectángulo")
        print(f"   📐 Texto = Información de perspectiva")
    else:
        print(f"\n❌ ERROR CREANDO VISUALIZACIÓN")
    
    return success


if __name__ == "__main__":
    print("📂 Directorio actual:", os.getcwd())
    print("💡 Asegúrate de estar en el directorio padre de 'size_calculator'")
    print()
    
    success = main()
    
    if success:
        print(f"\n✅ Proceso completado - Revisa la imagen generada!")
    else:
        print(f"\n❌ Proceso falló - Revisar configuración")
    
    sys.exit(0 if success else 1)