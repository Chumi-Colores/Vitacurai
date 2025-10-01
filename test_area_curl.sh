#!/bin/bash

# Test del endpoint /calcular_area usando curl

echo "🚀 Test del endpoint de cálculo de área"
echo "=" $(printf "%.0s=" {1..50})

# Datos de prueba en formato JSON
TEST_DATA='{
  "vertices": [
    [100, 100],
    [400, 120],
    [380, 300],
    [80, 280]
  ],
  "physical_distance": 2.5,
  "focal_length": [800.0, 800.0],
  "optical_center": [320.0, 240.0],
  "distortion_coefs": [0.1, -0.2, 0.001, 0.002, 0.05]
}'

echo "🧪 Enviando datos de prueba al endpoint /calcular_area..."
echo "📊 Datos de prueba:"
echo "$TEST_DATA" | python3 -m json.tool

echo ""
echo "📡 Respuesta del servidor:"

# Realizar petición usando curl
curl -X POST "http://localhost:8000/calcular_area" \
     -H "Content-Type: application/json" \
     -d "$TEST_DATA" \
     --max-time 30 \
     --silent \
     --show-error \
     | python3 -m json.tool

echo ""
echo "=" $(printf "%.0s=" {1..50})
echo "✅ Test completado"