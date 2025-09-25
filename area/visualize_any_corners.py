#!/usr/bin/env python3
"""
🎯 VISUALIZADOR GENERAL DE ESQUINAS

Script versátil para visualizar esquinas detectadas en cualquier imagen.
Útil para verificar que las coordenadas están correctas antes de hacer mediciones.

Uso:
    python3 visualize_any_corners.py -i imagen.jpg -c "x1,y1 x2,y2 x3,y3 x4,y4"
    python3 visualize_any_corners.py --image cartel.jpg --corners "100,50 500,60 490,300 110,290"
    python3 visualize_any_corners.py -i foto.jpg -c "100,50 500,60 490,300 110,290" --output mi_verificacion.jpg

Funciones:
- Marca esquinas con colores diferentes y números
- Dibuja el contorno del rectángulo
- Muestra información de perspectiva
- Opcionalmente aplica corrección de distorsión
- Guarda imagen de verificación
"""

import sys
import os
import argparse
import cv2
import numpy as np

# Agregar path del sistema
sys.path.append('size_calculator')

try:
    from size_calculator.image_preprocessing import validate_and_order_contours, correct_image_and_contours
except ImportError as e:
    print(f"❌ Error: No se pueden importar los módulos del sistema")
    print(f"   Asegúrate de estar en el directorio correcto")
    sys.exit(1)


def parse_corners(corners_str):
    """
    Parsea string de coordenadas a lista de tuplas.
    
    Args:
        corners_str: String como "100,50 500,60 490,300 110,290"
        
    Returns:
        Lista de tuplas [(x1,y1), (x2,y2), ...]
    """
    try:
        corners = []
        pairs = corners_str.strip().split()
        
        if len(pairs) != 4:
            raise ValueError(f"Se esperan 4 puntos, se recibieron {len(pairs)}")
        
        for pair in pairs:
            x, y = map(int, pair.split(','))
            corners.append((x, y))
        
        return corners
        
    except Exception as e:
        raise ValueError(f"Formato de coordenadas inválido: {e}")


def create_corners_visualization(image_path, corners, output_path="verification.jpg", 
                               show_corrected=False, calibration_file=None, verbose=True):
    """
    Crea visualización de esquinas detectadas con opciones flexibles.
    
    Args:
        image_path: Ruta a la imagen
        corners: Lista de coordenadas [(x,y), ...]
        output_path: Archivo de salida
        show_corrected: Si mostrar corrección de distorsión
        calibration_file: Archivo de calibración (opcional)
        verbose: Si mostrar mensajes detallados
        
    Returns:
        True si exitoso, False en caso contrario
    """
    def _print(msg):
        if verbose:
            print(msg)
    
    try:
        # Cargar imagen
        image = cv2.imread(image_path)
        if image is None:
            _print(f"❌ Error: No se pudo cargar {image_path}")
            return False
        
        _print(f"✅ Imagen cargada: {image.shape[1]}×{image.shape[0]} píxeles")
        
        # Validar coordenadas
        result = validate_and_order_contours(corners, verbose=verbose)
        if result is None:
            return False
        
        ordered_corners, perspective_info = result
        
        # Crear visualización
        vis_image = image.copy()
        
        # Configuración visual
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (0, 255, 255)]  # Verde, Azul, Rojo, Amarillo
        labels = ["TL", "TR", "BR", "BL"]
        
        # Calcular tamaño de elementos basado en el tamaño de imagen
        scale = min(image.shape[:2]) / 1000.0
        circle_radius = max(8, int(15 * scale))
        line_thickness = max(2, int(3 * scale))
        font_scale = max(0.5, 0.8 * scale)
        
        # Dibujar contorno del rectángulo
        for i in range(4):
            pt1 = ordered_corners[i]
            pt2 = ordered_corners[(i + 1) % 4]
            cv2.line(vis_image, pt1, pt2, (255, 255, 255), line_thickness + 1)  # Blanco
            cv2.line(vis_image, pt1, pt2, (0, 0, 0), line_thickness)          # Negro encima
        
        # Dibujar esquinas
        for i, (corner, color, label) in enumerate(zip(ordered_corners, colors, labels)):
            x, y = corner
            
            # Círculo para la esquina
            cv2.circle(vis_image, (x, y), circle_radius, color, -1)
            cv2.circle(vis_image, (x, y), circle_radius, (0, 0, 0), 2)
            
            # Número
            text_size = cv2.getTextSize(str(i+1), cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
            text_x = x - text_size[0] // 2
            text_y = y + text_size[1] // 2
            cv2.putText(vis_image, str(i+1), (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)
            
            # Etiqueta y coordenadas
            label_offset = circle_radius + 10
            cv2.putText(vis_image, f"{label} ({x},{y})", (x + label_offset, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.7, color, 2)
        
        # Información de perspectiva
        info_y = 40
        if perspective_info['has_perspective']:
            angle = perspective_info['perspective_angle']
            text = f"Perspectiva: {angle:.1f}° (DETECTADA)"
            color = (0, 165, 255)  # Naranja
        else:
            text = "Perspectiva: No detectada"
            color = (0, 255, 0)    # Verde
        
        cv2.putText(vis_image, text, (20, info_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 2)
        
        # Título
        title = f"Verificación - {os.path.basename(image_path)}"
        cv2.putText(vis_image, title, (20, info_y - 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)
        cv2.putText(vis_image, title, (20, info_y - 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), 1)
        
        # Mostrar corrección si se solicita
        final_image = vis_image
        
        if show_corrected and calibration_file and os.path.exists(calibration_file):
            try:
                _print("🔧 Aplicando corrección de distorsión...")
                
                corrected_image, corrected_contours, _ = correct_image_and_contours(
                    image_path, ordered_corners, calibration_file, verbose=False
                )
                
                vis_corrected = corrected_image.copy()
                
                # Misma visualización para imagen corregida
                for i in range(4):
                    pt1 = corrected_contours[i]
                    pt2 = corrected_contours[(i + 1) % 4]
                    cv2.line(vis_corrected, pt1, pt2, (255, 255, 255), line_thickness + 1)
                    cv2.line(vis_corrected, pt1, pt2, (0, 0, 0), line_thickness)
                
                for i, (corner, color, label) in enumerate(zip(corrected_contours, colors, labels)):
                    x, y = corner
                    cv2.circle(vis_corrected, (x, y), circle_radius, color, -1)
                    cv2.circle(vis_corrected, (x, y), circle_radius, (0, 0, 0), 2)
                    
                    text_size = cv2.getTextSize(str(i+1), cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
                    text_x = x - text_size[0] // 2
                    text_y = y + text_size[1] // 2
                    cv2.putText(vis_corrected, str(i+1), (text_x, text_y), 
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)
                    
                    cv2.putText(vis_corrected, f"{label} ({x},{y})", (x + label_offset, y), 
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.7, color, 2)
                
                # Título para corrección
                title_corr = f"Corregida - {os.path.basename(image_path)}"
                cv2.putText(vis_corrected, title_corr, (20, info_y - 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)
                cv2.putText(vis_corrected, title_corr, (20, info_y - 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), 1)
                
                # Combinar imágenes
                h1, w1 = vis_image.shape[:2]
                h2, w2 = vis_corrected.shape[:2]
                
                # Redimensionar para altura similar
                target_height = min(h1, h2, 1200)  # Limitar altura máxima
                
                if h1 != target_height:
                    vis_image = cv2.resize(vis_image, (int(w1 * target_height / h1), target_height))
                if h2 != target_height:
                    vis_corrected = cv2.resize(vis_corrected, (int(w2 * target_height / h2), target_height))
                
                # Separador
                separator = np.ones((target_height, 5, 3), dtype=np.uint8) * 128
                
                # Combinar
                final_image = np.hstack([vis_image, separator, vis_corrected])
                
                _print("✅ Visualización con corrección creada")
                
            except Exception as e:
                _print(f"⚠️ No se pudo aplicar corrección: {e}")
                final_image = vis_image
        
        # Guardar resultado
        success = cv2.imwrite(output_path, final_image)
        
        if success:
            _print(f"💾 Imagen guardada: {output_path}")
            _print(f"   📏 Dimensiones finales: {final_image.shape[1]}×{final_image.shape[0]}")
            
            if verbose:
                _print(f"\n📊 RESUMEN:")
                for i, (corner, label) in enumerate(zip(ordered_corners, labels)):
                    color_name = ["🟢 Verde", "🔵 Azul", "🔴 Rojo", "🟡 Amarillo"][i]
                    _print(f"   {i+1}. {label} {corner} - {color_name}")
            
            return True
        else:
            _print(f"❌ Error guardando imagen")
            return False
            
    except Exception as e:
        _print(f"❌ Error en visualización: {e}")
        return False


def main():
    """Función principal con argumentos de línea de comandos."""
    
    parser = argparse.ArgumentParser(
        description="Visualizador de esquinas detectadas para verificación",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 visualize_any_corners.py -i foto.jpg -c "100,50 500,60 490,300 110,290"
  python3 visualize_any_corners.py --image cartel.jpg --corners "100,50 500,60 490,300 110,290" --output verificacion.jpg
  python3 visualize_any_corners.py -i foto.jpg -c "100,50 500,60 490,300 110,290" --corrected --calibration calibration.npz

Formato de coordenadas: "x1,y1 x2,y2 x3,y3 x4,y4"
        """
    )
    
    # Argumentos requeridos
    parser.add_argument('--image', '-i', required=True, 
                       help='Ruta a la imagen')
    parser.add_argument('--corners', '-c', required=True,
                       help='4 esquinas: "x1,y1 x2,y2 x3,y3 x4,y4"')
    
    # Argumentos opcionales
    parser.add_argument('--output', '-o', default='verification.jpg',
                       help='Archivo de salida (default: verification.jpg)')
    parser.add_argument('--corrected', action='store_true',
                       help='Mostrar también coordenadas corregidas por distorsión')
    parser.add_argument('--calibration', default='size_calculator/calibration_pipeline/camera_calibration.npz',
                       help='Archivo de calibración para corrección')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Modo silencioso')
    
    args = parser.parse_args()
    
    # Configuración
    verbose = not args.quiet
    
    if verbose:
        print("🎯 VISUALIZADOR DE ESQUINAS")
        print("=" * 40)
        print(f"📁 Imagen: {args.image}")
        print(f"📍 Coordenadas: {args.corners}")
        print(f"💾 Salida: {args.output}")
        if args.corrected:
            print(f"🔧 Corrección: {args.calibration}")
    
    # Verificar imagen
    if not os.path.exists(args.image):
        print(f"❌ Error: No se encontró {args.image}")
        return False
    
    # Parsear coordenadas
    try:
        corners = parse_corners(args.corners)
        if verbose:
            print(f"✅ Coordenadas parseadas: {corners}")
    except Exception as e:
        print(f"❌ Error en coordenadas: {e}")
        return False
    
    # Crear visualización
    success = create_corners_visualization(
        image_path=args.image,
        corners=corners,
        output_path=args.output,
        show_corrected=args.corrected,
        calibration_file=args.calibration if args.corrected else None,
        verbose=verbose
    )
    
    if success and verbose:
        print(f"\n🎉 VISUALIZACIÓN CREADA")
        print(f"📂 Revisa: {args.output}")
        print(f"\n💡 INTERPRETACIÓN:")
        print(f"   🟢 Verde (1) = Esquina Superior Izquierda")
        print(f"   🔵 Azul (2) = Esquina Superior Derecha") 
        print(f"   🔴 Rojo (3) = Esquina Inferior Derecha")
        print(f"   🟡 Amarillo (4) = Esquina Inferior Izquierda")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)