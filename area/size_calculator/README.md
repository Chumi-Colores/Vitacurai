# 📏 Sistema de Medición de Carteles Rectangulares

Sistema avanzado que utiliza **calibración de cámara** y **geometría 3D** para medir el área real de carteles rectangulares a partir de fotografías.

## 🎯 **Características**

✅ **Corrección de distorsión** usando calibración de cámara  
✅ **Detección automática de perspectiva** con corrección matemática  
✅ **Validación geométrica completa** del rectángulo  
✅ **Cálculo preciso de área** en metros cuadrados  
✅ **Interfaz de línea de comandos** simple  
✅ **Resultados con métricas de calidad** y confianza  

## 🏗️ **Arquitectura Modular**

```
size_calculator/
├── main.py                           # 🎯 Programa principal
├── image_preprocessing/              # 🔧 Fase 1: Preprocesamiento
│   ├── contour_detector.py          #   📐 Validación y ordenamiento de contornos
│   └── distortion_corrector.py      #   🎨 Corrección de distorsión de imagen
├── inverse_projection/               # 📐 Fase 2: Proyección Inversa
│   └── inverse_projector.py         #   🎯 Conversión 2D → 3D
└── geometric_calculation/            # 📊 Fase 3: Cálculo Geométrico
    └── area_calculator.py            #   📏 Cálculo de área y validación
```

## 🚀 **Uso Rápido**

### **Comando Básico:**
```bash
python3 main.py -i cartel.jpg -c "100,50 500,60 490,300 110,290" -d 3.0
```

### **Comando Completo:**
```bash
python3 main.py \
  --image cartel.jpg \
  --contours "100,50 500,60 490,300 110,290" \
  --distance 3.5 \
  --calibration ../calibration_pipeline/camera_calibration.npz \
  --output resultado.json \
  --verbose
```

## 📋 **Parámetros**

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `--image` | Ruta a la imagen del cartel | `cartel.jpg` |
| `--contours` | 4 esquinas en píxeles | `"100,50 500,60 490,300 110,290"` |
| `--distance` | Distancia cámara-cartel (metros) | `3.5` |
| `--calibration` | Archivo de calibración (.npz) | `camera_calibration.npz` |
| `--output` | Archivo JSON de resultados | `resultado.json` |
| `--verbose` | Mensajes detallados | - |
| `--quiet` | Modo silencioso | - |

## 📐 **Formato de Contornos**

Los contornos deben especificarse como **4 esquinas** del rectángulo en formato:
```
"x1,y1 x2,y2 x3,y3 x4,y4"
```

**Ejemplo:**
```
"100,50 500,60 490,300 110,290"
```

⚠️ **Nota:** El orden de las esquinas no importa - el sistema las ordena automáticamente.

## 📊 **Ejemplo de Salida**

### **Modo Resumido:**
```
✅ Área: 2.1456 m²
📏 Dimensiones: 1.523 × 1.408 m
🎯 Calidad: EXCELLENT
```

### **Modo Verbose:**
```
📏 SISTEMA DE MEDICIÓN DE CARTELES
============================================================
🖼️ Imagen: cartel.jpg
📍 Esquinas: [(100, 50), (500, 60), (490, 300), (110, 290)]
📏 Distancia: 3.0 m

🔧 FASE 1: PREPROCESAMIENTO DE IMAGEN
---------------------------------------------
✅ Contornos válidos
📐 Esquinas ordenadas: TL(100,50) TR(500,60) BR(490,300) BL(110,290)
✅ No se detectó perspectiva significativa
✅ Distorsión corregida

📐 FASE 2: PROYECCIÓN INVERSA
-----------------------------------
📍 Convertidos 4 puntos a coordenadas normalizadas
🎯 Creados 4 rayos 3D
✅ Calculadas 4 intersecciones 3D

📊 FASE 3: CÁLCULO GEOMÉTRICO
-------------------------------------
📐 Vectores de lados calculados
📏 Dimensiones calculadas:
   Ancho: 1.523 m
   Alto: 1.408 m
   📊 Área: 2.1456 m²
🔍 Validación geométrica:
   Calidad: 🎉 Excelente - Rectángulo ideal

🎯 RESULTADO FINAL
============================================================
📊 Área del cartel: 2.1456 m²
📏 Dimensiones: 1.523 m × 1.408 m
🎯 Calidad: 🎉 Excelente - Rectángulo ideal
🔬 Confianza: 95.0%
```

## 🎯 **Métricas de Calidad**

El sistema evalúa automáticamente la calidad de la medición:

| Calidad | Descripción | Confianza | Acción |
|---------|-------------|-----------|--------|
| 🎉 **Excelente** | Rectángulo ideal | >90% | ✅ Usar resultado |
| ✅ **Buena** | Medición confiable | >80% | ✅ Usar resultado |
| ⚠️ **Aceptable** | Revisar condiciones | >65% | 🔍 Verificar |
| ❌ **Pobre** | Recalibrar/retomar | <65% | 🔄 Repetir proceso |

## 🔧 **Detección de Perspectiva**

El sistema detecta automáticamente si el cartel está inclinado:

- **Sin perspectiva**: Cartel perpendicular a la cámara
- **Perspectiva detectada**: Aplica corrección matemática automáticamente
- **Ángulo mostrado**: Grado de inclinación estimado

## 📁 **Archivo de Resultados JSON**

```json
{
  "success": true,
  "area_square_meters": 2.1456,
  "width_meters": 1.523,
  "height_meters": 1.408,
  "quality": {
    "quality": "excellent",
    "description": "🎉 Excelente - Rectángulo ideal",
    "confidence": 0.95
  },
  "perspective_info": {
    "has_perspective": false,
    "perspective_angle": 0.0,
    "confidence": "high"
  }
}
```

## 🔧 **Requisitos**

### **Dependencias:**
- Python 3.7+
- OpenCV (`pip install opencv-python`)
- NumPy (`pip install numpy`)

### **Archivo de Calibración:**
Debe existir el archivo de calibración generado por el módulo `calibration_pipeline`:
```
../calibration_pipeline/camera_calibration.npz
```

## ⚡ **Tips de Uso**

### **Para Mejores Resultados:**
1. 📸 **Foto clara** del cartel completo
2. 📐 **Medir distancia** con precisión 
3. 🎯 **Marcar esquinas** exactamente
4. 💡 **Buena iluminación** sin sombras
5. 📱 **Usar la misma cámara** de la calibración

### **Solución de Problemas:**

| Error | Causa | Solución |
|-------|-------|----------|
| "Archivo no encontrado" | Imagen o calibración faltante | Verificar rutas |
| "Contornos inválidos" | Formato incorrecto | Revisar formato x,y |
| "Calidad pobre" | Foto borrosa o mal ángulo | Retomar foto |

## 🎯 **Casos de Uso**

- 📺 **Medición de pantallas y monitores**
- 🏪 **Carteles publicitarios**
- 🖼️ **Cuadros y marcos**
- 📋 **Pizarras y tableros**
- 🚪 **Puertas y ventanas rectangulares**

## 🔬 **Precisión Esperada**

- **Condiciones ideales**: ±2-5% de error
- **Condiciones normales**: ±5-10% de error  
- **Limitado por**: Precisión de distancia y detección de esquinas

---

**Sistema desarrollado con arquitectura modular para máxima precisión y facilidad de uso** 🎯