#!/bin/bash

# Test del endpoint /calcular_area usando curl con imagen

echo "🚀 Test del endpoint de cálculo de área con imagen"
echo "=" $(printf "%.0s=" {1..60})

# Verificar que existe una imagen de prueba
if [ ! -f "test_image.jpg" ] && [ ! -f "../test_image.jpg" ]; then
    echo "⚠️  No se encontró imagen de prueba. Creando imagen sintética..."
    
    # Crear una imagen simple usando Python
    python3 -c "
import numpy as np
import cv2

# Crear imagen sintética de 640x480 con un rectángulo
img = np.zeros((480, 640, 3), dtype=np.uint8)
img.fill(200)  # Fondo gris claro

# Dibujar un rectángulo que simule un cartel
cv2.rectangle(img, (100, 100), (400, 300), (50, 50, 50), -1)
cv2.rectangle(img, (100, 100), (400, 300), (0, 0, 0), 3)

# Agregar texto
cv2.putText(img, 'CARTEL TEST', (150, 220), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# Guardar imagen
cv2.imwrite('test_cartel_image.jpg', img)
print('✅ Imagen sintética creada: test_cartel_image.jpg')
"
    
    if [ $? -ne 0 ]; then
        echo "❌ Error creando imagen sintética"
        echo "💡 Por favor coloca una imagen llamada 'test_image.jpg' en este directorio"
        exit 1
    fi
    
    IMAGE_FILE="test_cartel_image.jpg"
else
    # Usar imagen existente
    if [ -f "test_image.jpg" ]; then
        IMAGE_FILE="test_image.jpg"
    else
        IMAGE_FILE="../test_image.jpg"
    fi
fi

echo "📷 Usando imagen: $IMAGE_FILE"

# Parámetros de prueba
VERTICES='[[100, 100], [400, 120], [380, 300], [80, 280]]'
PHYSICAL_DISTANCE="2.5"
FOCAL_LENGTH='[800.0, 800.0]'
OPTICAL_CENTER='[320.0, 240.0]'
DISTORTION_COEFS='[0.1, -0.2, 0.001, 0.002, 0.05]'

echo "🧪 Parámetros de prueba:"
echo "   Vértices: $VERTICES"
echo "   Distancia física: $PHYSICAL_DISTANCE metros"
echo "   Distancia focal: $FOCAL_LENGTH"
echo "   Centro óptico: $OPTICAL_CENTER"
echo "   Coeficientes distorsión: $DISTORTION_COEFS"
echo ""

echo "📡 Enviando petición al servidor..."

# Realizar petición usando curl
curl -X POST "http://localhost:8000/calcular_area" \
     -F "image=@$IMAGE_FILE" \
     -F "vertices=$VERTICES" \
     -F "physical_distance=$PHYSICAL_DISTANCE" \
     -F "focal_length=$FOCAL_LENGTH" \
     -F "optical_center=$OPTICAL_CENTER" \
     -F "distortion_coefs=$DISTORTION_COEFS" \
     --max-time 60 \
     --silent \
     --show-error \
     | python3 -m json.tool

echo ""
echo "=" $(printf "%.0s=" {1..60})
echo "✅ Test completado"
echo ""
echo "💡 Para probar con tu propia imagen:"
echo "   1. Coloca tu imagen como 'test_image.jpg'"
echo "   2. Ajusta las coordenadas de vértices según tu imagen"
echo "   3. Ejecuta este script nuevamente"