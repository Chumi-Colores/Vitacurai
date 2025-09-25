# 📷 Calibration Pipeline

Sistema modular para calibración automática de cámaras usando tablero de ajedrez.

## 🎯 ¿Qué hace este programa?

Este programa toma múltiples fotos de un tablero de ajedrez y calcula automáticamente los **parámetros intrínsecos** de tu cámara (matriz K y coeficientes de distorsión), que son esenciales para aplicaciones de visión por computadora.

## 📁 Estructura del Proyecto

```
calibration_pipeline/
├── main.py                     # 🎮 Programa principal
├── chessboard_preprocessing.py # 📸 Preprocesamiento de imágenes
├── camera_calibrator.py        # 🔧 Calibración de cámara
├── __init__.py                 # 📦 Configuración del paquete
├── README.md                   # 📚 Esta documentación
└── calibration_images/         # 🖼️  Directorio de imágenes
    ├── 0.jpg
    ├── 1.jpg
    └── ...
```

## ⚡ Instalación Rápida

```bash
pip install opencv-python numpy
```

## 🚀 Uso Ultra Simple

### Opción 1: Modo Automático (Recomendado)

```bash
# Cambiar al directorio
cd calibration_pipeline

# Ejecutar calibración completa (con mensajes)
python3 main.py

# O en modo silencioso (sin mensajes)
python3 main.py --quiet
```

### Opción 2: Personalizado

```bash
# Directorio personalizado de imágenes
python3 main.py --dir mi_directorio

# Archivo de salida personalizado
python3 main.py --output mi_calibracion.npz

# Modo silencioso con configuración personalizada
python3 main.py --quiet --dir mis_fotos --output resultado.npz
```

## 📋 Pasos del Proceso Automático

El programa ejecuta automáticamente:

1. **📸 Preprocesamiento**: Detecta esquinas del tablero en todas las imágenes
2. **🔧 Calibración**: Calcula matriz de cámara y coeficientes de distorsión  
3. **💾 Guardado**: Almacena parámetros en archivo `.npz`
4. **🔍 Prueba**: Genera imagen corregida de ejemplo

## 🎯 ¿Qué Obtienes?

Después de ejecutar el programa:

```
📁 Archivos generados:
├── camera_calibration.npz          # ⭐ Parámetros de cámara
├── camera_calibration_metadata.json # 📊 Información adicional
└── undistorted_test.jpg             # 🖼️ Ejemplo de corrección
```

## 💻 Usar los Parámetros en tu Código

```python
import numpy as np
import cv2

# Cargar parámetros
data = np.load('camera_calibration.npz')
camera_matrix = data['camera_matrix']
dist_coefs = data['dist_coefs']

# Corregir distorsión en cualquier imagen
img = cv2.imread('mi_imagen.jpg')
img_corregida = cv2.undistort(img, camera_matrix, dist_coefs)
```

## 📝 Configuración del Tablero

Por defecto, el programa está configurado para:
- **Patrón**: 8x5 esquinas internas (tablero de 9x6 cuadrados)
- **Tamaño**: 26.5mm por cuadrado

Si tu tablero es diferente, puedes modificar estas líneas en `main.py`:
```python
# Línea ~62 en main.py
calibration_data = extract_calibration_parameters(
    calibration_dir=calibration_dir,
    pattern_size=(8, 5),      # ← Cambiar aquí
    square_size_mm=26.5,      # ← Y aquí
    verbose=verbose
)
```

## 📂 Preparar Imágenes

1. **Toma 10-15 fotos** del tablero desde diferentes ángulos
2. **Guárdalas** en la carpeta `calibration_images/`
3. **Formatos soportados**: `.jpg`, `.jpeg`, `.png`

```
calibration_images/
├── 0.jpg    # Tablero frontal
├── 1.jpg    # Tablero inclinado izquierda
├── 2.jpg    # Tablero inclinado derecha
├── 3.jpg    # Tablero desde arriba
└── ...      # Más ángulos
```

## 📊 Interpretación de Resultados

El programa te mostrará la **calidad** de tu calibración:

- 🎉 **Excelente (RMS < 0.5)**: ¡Perfecta calibración!
- ✅ **Buena (RMS < 1.0)**: Calibración confiable
- ⚠️ **Aceptable (RMS < 2.0)**: Funcional, pero mejorable
- ❌ **Pobre (RMS ≥ 2.0)**: Necesita recalibración

## 🛠️ Solución de Problemas

| Problema | Solución |
|----------|----------|
| "No se encontraron imágenes" | Verificar que `calibration_images/` tenga archivos `.jpg` |
| "No se detectó el tablero" | Mejorar iluminación, tablero completo visible |
| "RMS muy alto (>2.0)" | Tomar nuevas fotos con mejor calidad |
| Error al ejecutar | Verificar que tienes OpenCV instalado: `pip install opencv-python` |

## 💡 Consejos para Mejores Fotos

1. 📸 **10-15 imágenes** desde diferentes ángulos
2. 💡 **Iluminación uniforme** sin sombras
3. 📐 **Tablero completamente plano**
4. 🔍 **Tablero completo visible** en cada foto
5. 📏 **Medir con precisión** el tamaño de cuadrados

## 🔧 Arquitectura Modular

```python
main.py
├── chessboard_preprocessing.py  # Detecta esquinas del tablero
└── camera_calibrator.py         # Calcula parámetros de cámara
```

**Cada módulo tiene una responsabilidad específica:**
- ✅ **Fácil mantenimiento**
- ✅ **Código reutilizable** 
- ✅ **Fácil testing**
- ✅ **Extensible**

## 📚 Compatibilidad

- **Python**: 3.7+
- **OpenCV**: 4.x
- **NumPy**: 1.19+
- **SO**: Windows, macOS, Linux

---

**¿Necesitas ayuda?** El programa está diseñado para ser **plug-and-play**: pon tus imágenes y ejecuta `python3 main.py` 🚀