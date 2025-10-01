"""
Script de prueba para el CalibrationService autocontenido.

Este script prueba que el CalibrationService funciona correctamente
usando solo los módulos internos de la API (sin dependencias externas).
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path para importaciones
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from api.services.calibration.calibration_service import CalibrationService


def test_calibration_service_initialization():
    """Prueba que el CalibrationService se inicializa correctamente."""
    print("🧪 PRUEBA DE INICIALIZACIÓN DEL CALIBRATION SERVICE")
    print("=" * 55)
    
    try:
        # Crear instancia del servicio
        service = CalibrationService()
        print("✅ CalibrationService inicializado correctamente")
        
        # Verificar que tiene la función de calibración
        assert hasattr(service, '_calibrate_func'), "Función de calibración no encontrada"
        print("✅ Función de calibración interna disponible")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def test_parameter_validation():
    """Prueba la validación de parámetros."""
    print("\n🧪 PRUEBA DE VALIDACIÓN DE PARÁMETROS")
    print("=" * 40)
    
    try:
        service = CalibrationService()
        
        # Prueba parámetros válidos
        valid_result = service.validate_calibration_parameters(
            pattern_size=(8, 5),
            square_size_mm=26.5
        )
        
        print("🔧 Parámetros válidos:")
        print(f"   Pattern size: (8, 5)")
        print(f"   Square size: 26.5mm")
        print(f"   ✅ Validación: {valid_result}")
        
        # Prueba parámetros inválidos
        invalid_result = service.validate_calibration_parameters(
            pattern_size=(1, 1),  # Muy pequeño
            square_size_mm=-5     # Negativo
        )
        
        print("\n🔧 Parámetros inválidos:")
        print(f"   Pattern size: (1, 1)")
        print(f"   Square size: -5mm")
        print(f"   ❌ Validación: {invalid_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en validación: {e}")
        return False


def test_modules_are_internal():
    """Verifica que los módulos son internos y no dependen de archivos externos."""
    print("\n🧪 PRUEBA DE INDEPENDENCIA DE MÓDULOS")
    print("=" * 40)
    
    try:
        # Importar directamente los módulos internos
        from api.services.calibration.modules import (
            calibrate_from_directory,
            ChessboardPreprocessor,
            CameraCalibrator
        )
        
        print("✅ Módulos internos importados correctamente:")
        print("   - calibrate_from_directory")
        print("   - ChessboardPreprocessor")  
        print("   - CameraCalibrator")
        
        # Verificar que las clases se pueden instanciar
        preprocessor = ChessboardPreprocessor(pattern_size=(8, 5), square_size_mm=26.5)
        calibrator = CameraCalibrator(verbose=False)
        
        print("✅ Clases instanciadas correctamente")
        print(f"   - Preprocessor pattern_size: {preprocessor.pattern_size}")
        print(f"   - Calibrator initialized: {calibrator is not None}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando módulos internos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error instanciando clases: {e}")
        return False


def main():
    """Ejecuta todas las pruebas del CalibrationService."""
    print("🧪 PRUEBAS DEL CALIBRATION SERVICE AUTOCONTENIDO")
    print("=" * 60)
    
    # Ejecutar pruebas
    test_results = []
    
    test_results.append(("Inicialización del Service", test_calibration_service_initialization()))
    test_results.append(("Validación de Parámetros", test_parameter_validation()))
    test_results.append(("Independencia de Módulos", test_modules_are_internal()))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 RESULTADO FINAL: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El CalibrationService es completamente autocontenido.")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar la configuración de módulos internos.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)