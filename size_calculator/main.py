"""
Sistema de medición de carteles rectangulares.

Este programa utiliza calibración de cámara y proyección inversa para medir
el área real de carteles rectangulares a partir de fotografías.

Uso:
    python3 main.py --image cartel.jpg --contours "100,50 500,60 490,300 110,290" --distance 3.0
    python3 main.py -i cartel.jpg -c "100,50 500,60 490,300 110,290" -d 3.0 --calibration ../calibration_pipeline/camera_calibration.npz
"""

import sys
import os
import argparse
import json
from typing import List, Tuple, Dict, Any

# Agregar path de calibración para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'calibration_pipeline'))

# Importar módulos del sistema
from image_preprocessing import validate_and_order_contours, correct_image_and_contours
from inverse_projection import project_pixels_to_3d
from geometric_calculation import calculate_rectangle_area


class CartelAreaMeasurer:
    """
    Medidor de área de carteles usando calibración de cámara.
    """
    
    def __init__(self, calibration_file: str, verbose: bool = True):
        """
        Inicializa el medidor con archivo de calibración.
        
        Args:
            calibration_file: Ruta al archivo .npz de calibración
            verbose: Si mostrar mensajes detallados
        """
        self.calibration_file = calibration_file
        self.verbose = verbose
        
        # Verificar que existe el archivo de calibración
        if not os.path.exists(calibration_file):
            raise FileNotFoundError(f"❌ No se encontró archivo de calibración: {calibration_file}")
        
        self._print("🚀 Sistema de medición de carteles inicializado")
        self._print(f"📁 Calibración: {calibration_file}")
    
    def _print(self, message: str):
        """Imprime mensaje solo si verbose=True."""
        if self.verbose:
            print(message)
    
    def measure_cartel_area(self, 
                           image_path: str,
                           contours: List[Tuple[int, int]],
                           distance_meters: float) -> Dict[str, Any]:
        """
        Mide el área de un cartel rectangular.
        
        Args:
            image_path: Ruta a la imagen del cartel
            contours: Lista de 4 esquinas [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
            distance_meters: Distancia de la cámara al cartel en metros
            
        Returns:
            Diccionario con resultados de medición
        """
        try:
            self._print(f"\n" + "="*60)
            self._print("📏 SISTEMA DE MEDICIÓN DE CARTELES")
            self._print("="*60)
            self._print(f"🖼️  Imagen: {os.path.basename(image_path)}")
            self._print(f"📍 Esquinas: {contours}")
            self._print(f"📏 Distancia: {distance_meters} m")
            
            # ============================================
            # FASE 1: PREPROCESAMIENTO DE IMAGEN
            # ============================================
            self._print(f"\n🔧 FASE 1: PREPROCESAMIENTO DE IMAGEN")
            self._print("-" * 45)
            
            # Validar y ordenar contornos
            contour_result = validate_and_order_contours(contours, verbose=self.verbose)
            if contour_result is None:
                return {'success': False, 'error': 'Contornos inválidos'}
            
            ordered_corners, perspective_info = contour_result
            
            # Corregir distorsión de imagen y contornos
            corrected_image, corrected_contours, camera_params = correct_image_and_contours(
                image_path, ordered_corners, self.calibration_file, verbose=self.verbose
            )
            
            # ============================================
            # FASE 2: PROYECCIÓN INVERSA 2D → 3D
            # ============================================
            self._print(f"\n📐 FASE 2: PROYECCIÓN INVERSA")
            self._print("-" * 35)
            
            # Proyectar contornos corregidos a coordenadas 3D
            points_3d = project_pixels_to_3d(
                corrected_contours,
                camera_params['camera_matrix'],
                distance_meters,
                perspective_angle=perspective_info['perspective_angle'],
                verbose=self.verbose
            )
            
            # ============================================
            # FASE 3: CÁLCULO GEOMÉTRICO
            # ============================================
            self._print(f"\n📊 FASE 3: CÁLCULO GEOMÉTRICO")
            self._print("-" * 37)
            
            # Calcular área final
            area_result = calculate_rectangle_area(points_3d, verbose=self.verbose)
            
            # ============================================
            # RESULTADO FINAL
            # ============================================
            self._print(f"\n" + "="*60)
            self._print("🎯 RESULTADO FINAL")
            self._print("="*60)
            
            area_m2 = area_result['area_square_meters']
            width_m = area_result['width_meters']
            height_m = area_result['height_meters']
            quality = area_result['validation']['quality_assessment']
            
            self._print(f"📊 Área del cartel: {area_m2:.4f} m²")
            self._print(f"📏 Dimensiones: {width_m:.3f} m × {height_m:.3f} m")
            self._print(f"🎯 Calidad: {quality['description']}")
            self._print(f"🔬 Confianza: {quality['confidence']*100:.1f}%")
            
            if perspective_info['has_perspective']:
                self._print(f"📐 Corrección aplicada: {perspective_info['perspective_angle']:.1f}°")
            
            # Mostrar issues si los hay
            if quality['issues']:
                self._print(f"\n⚠️  Observaciones:")
                for issue in quality['issues']:
                    self._print(f"   • {issue}")
            
            # Compilar resultado completo
            result = {
                'success': True,
                'area_square_meters': area_m2,
                'width_meters': width_m,
                'height_meters': height_m,
                'quality': quality,
                'perspective_info': perspective_info,
                'detailed_results': area_result,
                'input_data': {
                    'image_path': image_path,
                    'original_contours': contours,
                    'corrected_contours': corrected_contours,
                    'distance_meters': distance_meters
                }
            }
            
            return result
            
        except Exception as e:
            error_msg = f"❌ Error durante medición: {str(e)}"
            self._print(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'input_data': {
                    'image_path': image_path,
                    'contours': contours,
                    'distance_meters': distance_meters
                }
            }


def parse_contours(contours_str: str) -> List[Tuple[int, int]]:
    """
    Parsea string de contornos a lista de tuplas.
    
    Args:
        contours_str: String como "100,50 500,60 490,300 110,290"
        
    Returns:
        Lista de tuplas [(x1,y1), (x2,y2), ...]
    """
    try:
        points = []
        pairs = contours_str.strip().split()
        
        if len(pairs) != 4:
            raise ValueError(f"Se esperan 4 puntos, se recibieron {len(pairs)}")
        
        for pair in pairs:
            x, y = map(int, pair.split(','))
            points.append((x, y))
        
        return points
        
    except Exception as e:
        raise ValueError(f"Formato de contornos inválido: {e}")


def main():
    """Función principal del programa."""
    parser = argparse.ArgumentParser(
        description="Medición de área de carteles rectangulares usando calibración de cámara",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python3 main.py -i cartel.jpg -c "100,50 500,60 490,300 110,290" -d 3.0
  python3 main.py --image cartel.jpg --contours "100,50 500,60 490,300 110,290" --distance 3.5 --calibration ../calibration_pipeline/camera_calibration.npz --verbose
  python3 main.py -i cartel.jpg -c "100,50 500,60 490,300 110,290" -d 2.8 --output resultado.json --quiet

Formato de contornos: "x1,y1 x2,y2 x3,y3 x4,y4" (4 esquinas del rectángulo en píxeles)
        """
    )
    
    # Argumentos requeridos
    parser.add_argument(
        '--image', '-i',
        required=True,
        help='Ruta a la imagen del cartel'
    )
    
    parser.add_argument(
        '--contours', '-c',
        required=True,
        help='4 esquinas del cartel: "x1,y1 x2,y2 x3,y3 x4,y4"'
    )
    
    parser.add_argument(
        '--distance', '-d',
        type=float,
        required=True,
        help='Distancia de la cámara al cartel en metros'
    )
    
    # Argumentos opcionales
    parser.add_argument(
        '--calibration',
        default='../calibration_pipeline/camera_calibration.npz',
        help='Ruta al archivo de calibración (default: ../calibration_pipeline/camera_calibration.npz)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Archivo JSON para guardar resultados detallados'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=True,
        help='Mostrar mensajes detallados (default: True)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Modo silencioso (anula --verbose)'
    )
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Determinar verbosidad
    verbose = args.verbose and not args.quiet
    
    try:
        # Parsear contornos
        contours = parse_contours(args.contours)
        
        # Verificar que la imagen existe
        if not os.path.exists(args.image):
            print(f"❌ Error: No se encontró la imagen: {args.image}")
            return 1
        
        # Crear medidor
        measurer = CartelAreaMeasurer(args.calibration, verbose=verbose)
        
        # Realizar medición
        result = measurer.measure_cartel_area(
            image_path=args.image,
            contours=contours,
            distance_meters=args.distance
        )
        
        # Mostrar resultado resumido si no es verbose
        if not verbose:
            if result['success']:
                print(f"✅ Área: {result['area_square_meters']:.4f} m²")
                print(f"📏 Dimensiones: {result['width_meters']:.3f} × {result['height_meters']:.3f} m")
                print(f"🎯 Calidad: {result['quality']['quality'].upper()}")
            else:
                print(f"❌ Error: {result['error']}")
        
        # Guardar resultados detallados si se especifica
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"💾 Resultados guardados en: {args.output}")
        
        # Código de salida
        return 0 if result['success'] else 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())