"""
Módulo principal para calibración de cámara.

Este módulo orquesta todo el proceso de calibración:
1. Preprocesamiento de imágenes (chessboard_preprocessing)
2. Calibración de cámara (camera_calibrator)
3. Guardado de parámetros

Uso:
    python3 main.py                    # Modo verbose (por defecto)
    python3 main.py --quiet           # Modo silencioso
"""

import sys
import os
import argparse
from pathlib import Path

# Importar módulos locales
from chessboard_preprocessing import extract_calibration_parameters
from camera_calibrator import CameraCalibrator


def main(verbose: bool = True, 
         calibration_dir: str = "calibration_images",
         output_file: str = "camera_calibration.npz") -> bool:
    """
    Función principal que ejecuta todo el proceso de calibración.
    
    Args:
        verbose: Si imprimir mensajes de progreso
        calibration_dir: Directorio con imágenes del tablero
        output_file: Archivo donde guardar parámetros
        
    Returns:
        True si el proceso fue exitoso, False en caso contrario
    """
    
    def print_msg(msg: str):
        """Imprime mensaje solo si verbose=True."""
        if verbose:
            print(msg)
    
    # Header del programa
    print_msg("=" * 60)
    print_msg("🎯 CALIBRACIÓN AUTOMÁTICA DE CÁMARA")
    print_msg("=" * 60)
    
    try:
        # ============================================
        # PASO 1: PREPROCESAMIENTO DE IMÁGENES
        # ============================================
        print_msg("\n📸 PASO 1: PREPROCESAMIENTO DE IMÁGENES")
        print_msg("-" * 45)
        
        # Verificar que el directorio existe
        if not Path(calibration_dir).exists():
            print_msg(f"❌ Error: No se encontró el directorio {calibration_dir}")
            return False
        
        # Extraer y preprocesar imágenes
        calibration_data = extract_calibration_parameters(
            calibration_dir=calibration_dir,
            pattern_size=(8, 5),  # Configuración por defecto
            square_size_mm=26.5,  # Configuración por defecto
            verbose=verbose
        )
        
        print_msg(f"✅ Preprocesamiento completado:")
        print_msg(f"   - Imágenes exitosas: {calibration_data['successful_images']}")
        print_msg(f"   - Total procesadas: {calibration_data['total_images']}")
        
        # ============================================
        # PASO 2: CALIBRACIÓN DE CÁMARA
        # ============================================
        print_msg(f"\n🔧 PASO 2: CALIBRACIÓN DE CÁMARA")
        print_msg("-" * 40)
        
        # Crear calibrador
        calibrator = CameraCalibrator(verbose=verbose)
        
        # Realizar calibración
        result = calibrator.calibrate(calibration_data)
        
        if not result['success']:
            print_msg(f"❌ Error en calibración: {result.get('error', 'Error desconocido')}")
            return False
        
        # ============================================
        # PASO 3: GUARDADO DE PARÁMETROS
        # ============================================
        print_msg(f"\n💾 PASO 3: GUARDADO DE PARÁMETROS")
        print_msg("-" * 42)
        
        # Guardar parámetros
        save_success = calibrator.save_parameters(
            output_file=output_file,
            json_file=output_file.replace('.npz', '_metadata.json')
        )
        
        if not save_success:
            print_msg("❌ Error guardando parámetros")
            return False
        
        # ============================================
        # PASO 4: PRUEBA DE CORRECCIÓN (OPCIONAL)
        # ============================================
        if calibration_data['image_paths']:
            print_msg(f"\n🔍 PASO 4: PRUEBA DE CORRECCIÓN")
            print_msg("-" * 43)
            
            test_image = calibration_data['image_paths'][0]
            calibrator.test_undistortion(
                test_image_path=test_image,
                output_path="undistorted_test.jpg"
            )
        
        # ============================================
        # RESUMEN FINAL
        # ============================================
        print_msg(f"\n" + "=" * 60)
        print_msg("🎉 CALIBRACIÓN COMPLETADA EXITOSAMENTE")
        print_msg("=" * 60)
        
        print_msg(f"📊 Resultados:")
        print_msg(f"   • RMS: {result['rms']:.4f} píxeles")
        print_msg(f"   • Calidad: {result['quality']['description']}")
        print_msg(f"   • Imágenes utilizadas: {result['num_images']}")
        
        print_msg(f"\n📁 Archivos generados:")
        print_msg(f"   • camera_calibration.npz (parámetros principales)")
        print_msg(f"   • camera_calibration_metadata.json (metadatos legibles)")
        if os.path.exists("undistorted_test.jpg"):
            print_msg(f"   • undistorted_test.jpg (imagen de prueba)")
        
        print_msg(f"\n💡 Uso de parámetros:")
        print_msg(f"   import numpy as np")
        print_msg(f"   data = np.load('camera_calibration.npz')")
        print_msg(f"   camera_matrix = data['camera_matrix']")
        print_msg(f"   dist_coefs = data['dist_coefs']")
        
        return True
        
    except Exception as e:
        print_msg(f"❌ Error inesperado: {e}")
        return False


def parse_arguments():
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Calibración automática de cámara usando tablero de ajedrez",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python3 main.py                           # Modo verbose (por defecto)
  python3 main.py --quiet                   # Modo silencioso
  python3 main.py --dir mi_directorio       # Directorio personalizado
  python3 main.py --output mi_calib.npz     # Archivo de salida personalizado
        """
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Ejecutar en modo silencioso (sin mensajes de progreso)'
    )
    
    parser.add_argument(
        '--dir', '-d',
        default='calibration_images',
        help='Directorio con imágenes de calibración (default: calibration_images)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='camera_calibration.npz',
        help='Archivo de salida para parámetros (default: camera_calibration.npz)'
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    # Parsear argumentos
    args = parse_arguments()
    
    # Ejecutar calibración
    success = main(
        verbose=not args.quiet,
        calibration_dir=args.dir,
        output_file=args.output
    )
    
    # Código de salida
    sys.exit(0 if success else 1)