"""
Prueba integral de la API autocontenida.

Este script verifica que toda la API sea completamente independiente 
de la carpeta area/size_calculator, usando únicamente módulos internos.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path para importaciones
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_api_services_independence():
    """Verifica que todos los servicios de la API son independientes."""
    print("🧪 PRUEBA DE INDEPENDENCIA COMPLETA DE LA API")
    print("=" * 55)
    
    try:
        # Importar todos los servicios principales
        from api.services import services
        from api.services.calibration import CalibrationService
        from api.services.area import AreaCalculationService
        
        print("✅ Importación de servicios principales exitosa")
        
        # Verificar instanciación de servicios
        calibration_service = CalibrationService()
        area_service = AreaCalculationService(verbose=False)
        
        print("✅ Instanciación de servicios exitosa")
        
        # Verificar acceso a servicios desde orquestador
        assert hasattr(services, 'calibration_service'), "Servicio de calibración no disponible"
        assert hasattr(services.calibration_service, '_calibrate_func'), "Función de calibración no disponible"
        
        print("✅ Orquestador de servicios funcional")
        
        # Verificar que los servicios tienen sus métodos principales
        assert hasattr(calibration_service, 'calibrate_camera'), "Método calibrate_camera no encontrado"
        assert hasattr(area_service, 'calculate_cartel_area'), "Método calculate_cartel_area no encontrado"
        
        print("✅ Métodos principales de servicios disponibles")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def test_internal_modules_complete():
    """Verifica que todos los módulos internos están completos."""
    print("\n🧪 PRUEBA DE COMPLETITUD DE MÓDULOS INTERNOS")
    print("=" * 45)
    
    try:
        # Módulos de calibración
        from api.services.calibration.modules import (
            calibrate_from_directory,
            ChessboardPreprocessor,
            CameraCalibrator
        )
        
        print("✅ Módulos de calibración internos:")
        print("   - calibrate_from_directory")
        print("   - ChessboardPreprocessor")
        print("   - CameraCalibrator")
        
        # Módulos de área
        from api.services.area.modules import (
            image_preprocessing,
            inverse_projection,
            geometric_calculation
        )
        
        from api.services.area.modules.image_preprocessing import validate_and_order_contours
        from api.services.area.modules.inverse_projection import project_pixels_to_3d
        from api.services.area.modules.geometric_calculation import calculate_rectangle_area
        
        print("✅ Módulos de área internos:")
        print("   - image_preprocessing (validate_and_order_contours)")
        print("   - inverse_projection (project_pixels_to_3d)")
        print("   - geometric_calculation (calculate_rectangle_area)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando módulos internos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def test_no_external_dependencies():
    """Verifica que no hay dependencias externas a area/size_calculator."""
    print("\n🧪 PRUEBA DE AUSENCIA DE DEPENDENCIAS EXTERNAS")
    print("=" * 50)
    
    try:
        import importlib.util
        import os
        
        # Verificar que area/size_calculator no esté en sys.path después de importaciones
        external_paths = [path for path in sys.path if 'area/size_calculator' in path or 'size_calculator' in path]
        
        if external_paths:
            print(f"❌ Dependencias externas encontradas en sys.path: {external_paths}")
            return False
        
        print("✅ No se encontraron dependencias externas en sys.path")
        
        # Verificar que los módulos pueden importarse sin area/size_calculator en el path
        # Temporalmente remover cualquier path que contenga area/size_calculator
        original_paths = sys.path.copy()
        sys.path = [p for p in sys.path if 'area' not in p or 'api' in p]
        
        try:
            # Reimportar módulos principales para verificar independencia
            from api.services.calibration.modules.calibration_api_module import calibrate_from_directory
            from api.services.area.modules.image_preprocessing import validate_and_order_contours
            
            print("✅ Módulos internos funcionan sin dependencias externas")
            
        finally:
            # Restaurar sys.path original
            sys.path = original_paths
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando independencia: {e}")
        return False


def test_api_controllers():
    """Verifica que los controladores funcionan con servicios internos."""
    print("\n🧪 PRUEBA DE CONTROLADORES DE API")
    print("=" * 35)
    
    try:
        # Importar controladores
        from api.controllers import CalibrationController
        from api.services import services
        
        # Instanciar controlador
        controller = CalibrationController()
        
        print("✅ Controlador de calibración instanciado")
        
        # Verificar que el orquestador de servicios funciona
        assert services.calibration_service is not None, "Servicio de calibración no disponible"
        
        # Verificar validación de parámetros
        validation_result = services.validate_calibration_parameters(
            pattern_size=(8, 5),
            square_size_mm=26.5
        )
        
        assert validation_result['valid'], f"Validación falló: {validation_result}"
        
        print("✅ Validación de parámetros funcional")
        print("✅ Orquestador de servicios operacional")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando controladores: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en controladores: {e}")
        return False


def main():
    """Ejecuta todas las pruebas de independencia de la API."""
    print("🧪 PRUEBAS DE INDEPENDENCIA COMPLETA DE LA API VITACURAI")
    print("=" * 65)
    print("🎯 Objetivo: Verificar que la API no depende de area/size_calculator")
    print("=" * 65)
    
    # Ejecutar pruebas
    test_results = []
    
    test_results.append(("Independencia de Servicios", test_api_services_independence()))
    test_results.append(("Completitud de Módulos", test_internal_modules_complete()))
    test_results.append(("Ausencia de Dependencias Externas", test_no_external_dependencies()))
    test_results.append(("Funcionalidad de Controladores", test_api_controllers()))
    
    # Resumen final
    print("\n" + "=" * 65)
    print("📊 RESUMEN FINAL DE INDEPENDENCIA")
    print("=" * 65)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print("\n" + "=" * 65)
    print(f"🎯 RESULTADO FINAL: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡ÉXITO! La API es completamente autocontenida e independiente.")
        print("📦 No hay dependencias externas a area/size_calculator")
        print("🚀 Los servicios usan únicamente módulos internos de la API")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. La API aún tiene dependencias externas.")
        print("🔧 Revisar y actualizar los módulos que fallan.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)