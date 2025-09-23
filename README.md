# Vitacurai

Para descargar el modelo, ejecutar:
git submodule init
git submodule update

Para instalar requerimientos del modelo ejecutar:
cd Depth-Anything-V2/metric_depth
pip install -r requirements.txt

Para instalar los parámetros (weights) del modelo, descargar desde este link:
https://huggingface.co/depth-anything/Depth-Anything-V2-Metric-VKITTI-Large/resolve/main/depth_anything_v2_metric_vkitti_vitl.pth?download=true

Para ejecutar una predicción correr:
python .\Depth-Anything-V2\metric_depth\run.py --encoder vitl --load-from checkpoints/depth_anything_v2_metric_vkitti_vitl.pth --max-depth 80 --img-path ./{nombre_imagen}.jpg --outdir ./outdir --input-size 518 --save-numpy