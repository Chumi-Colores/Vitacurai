# 🎯 Guía Rápida - Sistema de Medición de Carteles

## 🚀 Inicio Rápido

### 1️⃣ Medición Básica
```bash
python3 size_calculator/main.py -i cartel.jpg -c "100,50 500,60 490,300 110,290" -d 2.0
```

### 2️⃣ Verificar Esquinas (RECOMENDADO)
```bash
python3 visualize_any_corners.py -i cartel.jpg -c "100,50 500,60 490,300 110,290"
```

### 3️⃣ Test con Imagen de Calibración
```bash
python3 test_simple.py
```

---

## 📏 Cómo Obtener Coordenadas

### Opción A: GIMP (Recomendado)
1. Abrir imagen en GIMP
2. Ver → Info (mantener abierto)
3. Mover cursor sobre cada esquina
4. Anotar coordenadas X,Y

### Opción B: Cualquier Visor de Imágenes
- La mayoría muestran coordenadas del cursor
- Anotar posición de cada esquina

### Opción C: Código Python Simple
```python
import cv2

def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Coordenada: {x},{y}")

img = cv2.imread('cartel.jpg')
cv2.setMouseCallback('image', click_event)
cv2.imshow('image', img)
cv2.waitKey(0)
```

---

## 📐 Orden de las Esquinas

**SIEMPRE en este orden:**
1. **Superior Izquierda** (TL)
2. **Superior Derecha** (TR)  
3. **Inferior Derecha** (BR)
4. **Inferior Izquierda** (BL)

```
TL ────── TR
│          │
│  CARTEL  │
│          │
BL ────── BR
```

---

## 🎨 Verificación Visual

### Colores en la Visualización:
- 🟢 **Verde** = Esquina Superior Izquierda (1)
- 🔵 **Azul** = Esquina Superior Derecha (2)
- 🔴 **Rojo** = Esquina Inferior Derecha (3)  
- 🟡 **Amarillo** = Esquina Inferior Izquierda (4)

### ¿Están Bien las Esquinas?
✅ **Correcto**: Los círculos están exactamente en las esquinas del cartel
❌ **Incorrecto**: Los círculos están desplazados o en orden incorrecto

---

## 🔧 Comandos Completos

### Medición Simple
```bash
python3 size_calculator/main.py \
  --image cartel.jpg \
  --corners "100,50 500,60 490,300 110,290" \
  --distance 2.0 \
  --output resultados.json
```

### Verificación con Corrección de Distorsión
```bash
python3 visualize_any_corners.py \
  --image cartel.jpg \
  --corners "100,50 500,60 490,300 110,290" \
  --corrected \
  --output verificacion.jpg
```

### Test del Sistema
```bash
# Test básico
python3 test_simple.py

# Test completo con múltiples imágenes
python3 test_system_improved.py
```

---

## 📊 Interpretación de Resultados

### Archivo JSON de Resultados:
```json
{
  "input_info": {
    "image_file": "cartel.jpg",
    "distance_meters": 2.0
  },
  "measurements": {
    "area_m2": 0.15234,
    "width_m": 0.42,
    "height_m": 0.36
  },
  "validation": {
    "error_percentage": 5.2,
    "perspective_corrected": true,
    "perspective_angle": 12.3
  }
}
```

### Valores Importantes:
- **area_m2**: Área real en metros cuadrados
- **error_percentage**: Precisión estimada (< 10% es excelente)
- **perspective_corrected**: Si se corrigió perspectiva automáticamente
- **perspective_angle**: Ángulo de inclinación detectado

---

## ⚠️ Consejos y Errores Comunes

### ✅ Buenas Prácticas:
- Siempre verificar esquinas con `visualize_any_corners.py`
- Tomar foto desde distancia conocida con precisión
- Asegurar que el cartel esté completamente visible
- Buena iluminación, evitar sombras fuertes

### ❌ Errores Comunes:
- **Orden incorrecto de esquinas** → Resultado erróneo
- **Distancia mal medida** → Error proporcional
- **Esquinas en bordes borrosos** → Imprecisión
- **Cartel parcialmente oculto** → Cálculo imposible

### 🔧 Solución de Problemas:
```bash
# Si falla la importación de módulos
cd "directorio/del/proyecto"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Si error de calibración
ls size_calculator/calibration_pipeline/camera_calibration.npz

# Test de funcionamiento
python3 -c "import cv2; print('OpenCV:', cv2.__version__)"
```

---

## 📈 Precisión Esperada

| Condiciones | Precisión Típica |
|-------------|------------------|
| **Ideal**: Sin perspectiva, buena luz | 2-5% error |
| **Normal**: Ligera perspectiva | 5-10% error |
| **Difícil**: Perspectiva marcada | 10-15% error |
| **Problemático**: >30° perspectiva | >15% error |

---

## 🆘 Ayuda Rápida

### Ver Ayuda Detallada:
```bash
python3 size_calculator/main.py --help
python3 visualize_any_corners.py --help
```

### Estructura del Proyecto:
```
size_calculator/
├── main.py                    # Sistema principal
├── image_preprocessing/       # Validación y corrección
├── inverse_projection/        # Conversión 2D→3D  
├── geometric_calculation/     # Cálculo de área
└── calibration_pipeline/      # Calibración cámara
```

### Scripts de Test:
- `test_simple.py` - Test básico rápido
- `test_system.py` - Test sistema completo
- `visualize_any_corners.py` - Verificación visual