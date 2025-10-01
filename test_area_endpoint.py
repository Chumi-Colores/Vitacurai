#!/usr/bin/env python3
"""
Test del endpoint de cálculo de área integrado en la API.

Este script prueba el endpoint /calcular_area usando datos de prueba.
"""

import requests
import json
from typing import Dict, Any


def test_area_calculation_endpoint():
    """
    Test del endpoint /calcular_area con datos de prueba.
    """
    # URL base del servidor (ajustar según configuración)
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/calcular_area"
    
    # Datos de prueba - coordenadas de un cartel rectangular
    test_data = {
        "vertices": [
            [100, 100],   # Esquina superior izquierda
            [400, 120],   # Esquina superior derecha
            [380, 300],   # Esquina inferior derecha
            [80, 280]     # Esquina inferior izquierda
        ],
        "physical_distance": 2.5,  # 2.5 metros de distancia
        "focal_length": [800.0, 800.0],  # fx, fy
        "optical_center": [320.0, 240.0],  # cx, cy
        "distortion_coefs": [0.1, -0.2, 0.001, 0.002, 0.05]  # k1, k2, p1, p2, k3
    }
    
    print("🧪 Iniciando test del endpoint /calcular_area")
    print(f"📊 Datos de prueba:")
    print(f"   - Vértices: {test_data['vertices']}")
    print(f"   - Distancia física: {test_data['physical_distance']} metros")
    print(f"   - Distancia focal: {test_data['focal_length']}")
    print(f"   - Centro óptico: {test_data['optical_center']}")
    print()
    
    try:
        # Realizar petición POST al endpoint
        print("📡 Enviando petición al servidor...")
        response = requests.post(
            endpoint,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📈 Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            # Procesar respuesta exitosa
            result = response.json()
            
            print("✅ Respuesta exitosa del endpoint")
            print("📋 Resultados del cálculo de área:")
            
            if result.get("success", False):
                print(f"   ✅ Cálculo exitoso")
                print(f"   📏 Área: {result.get('area_square_meters', 'N/A'):.4f} m²")
                print(f"   📐 Ancho: {result.get('width_meters', 'N/A'):.4f} metros")
                print(f"   📏 Alto: {result.get('height_meters', 'N/A'):.4f} metros")
                
                # Información de calidad
                if "quality" in result:
                    quality = result["quality"]
                    print(f"   🎯 Calidad: {quality.get('overall_quality', 'N/A')}")
                
                # Observaciones
                if "observations" in result and result["observations"]:
                    print(f"   📝 Observaciones:")
                    for obs in result["observations"]:
                        print(f"      - {obs}")
                
                return True
            else:
                print(f"   ❌ Error en el cálculo: {result.get('error', 'Error desconocido')}")
                return False
        
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Detalle: {error_detail}")
            except:
                print(f"   Contenido: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Error de timeout: El servidor tardó demasiado en responder")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False


def test_validation_errors():
    """
    Test de validación de errores del endpoint.
    """
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/calcular_area"
    
    print("\n🧪 Probando validación de errores...")
    
    # Test 1: Número incorrecto de vértices
    invalid_data_1 = {
        "vertices": [[100, 100], [400, 120]],  # Solo 2 vértices
        "physical_distance": 2.5,
        "focal_length": [800.0, 800.0],
        "optical_center": [320.0, 240.0],
        "distortion_coefs": [0.1, -0.2, 0.001, 0.002, 0.05]
    }
    
    try:
        response = requests.post(endpoint, json=invalid_data_1, timeout=10)
        if response.status_code == 422:  # Validation error
            print("✅ Test 1 pasó: Error de validación por número incorrecto de vértices")
        else:
            print(f"⚠️  Test 1: Respuesta inesperada {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor para tests de validación")
        return False
        
    return True


if __name__ == "__main__":
    print("🚀 Test del endpoint de cálculo de área")
    print("=" * 50)
    
    # Ejecutar tests
    success = test_area_calculation_endpoint()
    test_validation_errors()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test completado exitosamente")
    else:
        print("⚠️  Test tuvo problemas - revisar configuración del servidor")
    
    print("\n💡 Para ejecutar el servidor manualmente:")
    print("   python3 api_server.py")
    print("   o")
    print("   uvicorn api_server:app --reload --host 0.0.0.0 --port 8000")