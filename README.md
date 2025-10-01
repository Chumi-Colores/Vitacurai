# Vitacurai

Sistema de medición de carteles con IA que incluye:
- Estimación de profundidad con Depth-Anything-V2
- Cálculo de área de carteles rectangulares
- API REST autocontenida para cálculo de áreas

## 🔧 Configuración del Modelo de Profundidad

Para descargar el modelo, ejecutar:
```bash
git submodule init
git submodule update
```

Para instalar requerimientos del modelo ejecutar:
```bash
cd Depth-Anything-V2/metric_depth
pip install -r requirements.txt
```

Para instalar los parámetros (weights) del modelo, descargar desde este link:
https://huggingface.co/depth-anything/Depth-Anything-V2-Metric-VKITTI-Large/resolve/main/depth_anything_v2_metric_vkitti_vitl.pth?download=true

Colocar esto en la carpeta `checkpoints/`.

## 📊 API de Cálculo de Área

### Estructura Autocontenida

El sistema incluye una API completamente autocontenida en `api/` que no depende de módulos externos:

```
api/
├── controllers.py          # Controladores REST
├── models.py              # Modelos de datos
└── services/
    └── area/
        ├── area_calculation_service.py  # Servicio principal
        └── modules/                     # Módulos internos copiados
            ├── image_preprocessing/
            ├── inverse_projection/
            └── geometric_calculation/
```

### Uso del Servicio

```python
from api.services.area.area_calculation_service import AreaCalculationService

# Crear servicio
service = AreaCalculationService(verbose=True)

# Calcular área
result = service.calculate_cartel_area(
    image_data=image_array,
    vertices=[[200, 150], [600, 180], [580, 420], [180, 390]],
    physical_distance=1.5,
    focal_length=(3074.1, 3080.8),
    optical_center=(1511.8, 2007.4),
    distortion_coefs=[0.1, -0.2, 0.001, 0.002, 0.1]
)

print(f"Área: {result['area_square_meters']:.4f} m²")
```

### Prueba del Sistema

Para probar el API de cálculo de área:
```bash
python3 test_area_service.py
```