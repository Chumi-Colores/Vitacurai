"""
Servicio especializado de calibración de cámara.

Este servicio actúa como wrapper del módulo de calibración existente,
proporcionando una interfaz limpia para la API.
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Union
import cv2
import numpy as np
from fastapi import UploadFile
import io


class CalibrationService:
    """
    Servicio especializado en calibración de cámara.
    
    Utiliza el módulo calibration_api_module existente para realizar
    la calibración y proporciona una interfaz adaptada para la API.
    """
    
    def __init__(self):
        """Inicializa el servicio y configura las rutas de importación."""
        self._setup_calibration_module()
    
    def _setup_calibration_module(self):
        """Configura los módulos de calibración internos de la API."""
        # Importar módulos internos de la API
        try:
            from .modules.calibration_api_module import calibrate_from_directory
            self._calibrate_func = calibrate_from_directory
        except ImportError as e:
            raise ImportError(f"No se pudieron importar los módulos internos de calibración: {e}")
    
    async def calibrate_camera(self, 
                             image_files: List[UploadFile],
                             pattern_size: tuple = (8, 5),
                             square_size_mm: float = 26.5) -> Dict[str, Any]:
        """
        Ejecuta calibración de cámara usando imágenes subidas.
        
        Args:
            image_files: Lista de archivos de imagen subidos
            pattern_size: Tamaño del patrón del tablero (cols, rows)
            square_size_mm: Tamaño real de cada cuadrado en milímetros
            
        Returns:
            Diccionario JSON con resultado completo de calibración
        """
        import tempfile
        import shutil
        import os
        
        temp_dir = None
        
        try:
            # Validar entrada
            if not image_files:
                return {
                    "success": False,
                    "error": "No se proporcionaron archivos de imagen"
                }
            
            if len(image_files) < 5:
                return {
                    "success": False,
                    "error": f"Se requieren al menos 5 imágenes, se proporcionaron {len(image_files)}"
                }
            
            # Crear directorio temporal
            temp_dir = tempfile.mkdtemp(prefix="vitacurai_calibration_")
            print(f"📁 Directorio temporal creado: {temp_dir}")
            
            # Guardar imágenes en directorio temporal
            saved_count = await self._save_images_to_temp_directory(image_files, temp_dir)
            
            if saved_count < 5:
                return {
                    "success": False,
                    "error": f"Solo se pudieron guardar {saved_count} imágenes válidas (mínimo 5 requeridas). Verifica que los archivos sean imágenes válidas (JPG, PNG)."
                }
            
            print(f"🔧 Iniciando calibración con {saved_count} imágenes guardadas...")
            
            # Usar calibrate_from_directory que funciona con archivos en disco
            result = self._calibrate_func(
                directory_path=temp_dir,
                pattern_size=pattern_size,
                square_size=square_size_mm,
                verbose=False  # Sin logs detallados para API
            )
            
            print(f"✅ Calibración completada. Éxito: {result.get('success', False)}")
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error durante calibración: {str(e)}"
            }
        
        finally:
            # Limpiar directorio temporal
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    print(f"🗑️ Directorio temporal eliminado: {temp_dir}")
                except Exception as e:
                    print(f"⚠️ No se pudo eliminar directorio temporal: {e}")
    
    async def _convert_uploaded_files_to_images(self, 
                                             uploaded_files: List[UploadFile]) -> List[np.ndarray]:
        """
        Convierte archivos subidos a arrays numpy para OpenCV.
        
        Args:
            uploaded_files: Lista de archivos subidos
            
        Returns:
            Lista de arrays numpy representando las imágenes
        """
        images = []
        
        for i, file in enumerate(uploaded_files):
            try:
                # Leer contenido del archivo
                content = await file.read()
                
                if len(content) == 0:
                    print(f"⚠️ Archivo {i+1} ({file.filename}) está vacío")
                    continue
                
                # Método 1: Intentar con OpenCV directamente
                img = None
                try:
                    nparr = np.frombuffer(content, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                except Exception as e:
                    print(f"⚠️ Error OpenCV en archivo {i+1}: {e}")
                
                # Método 2: Si OpenCV falla, intentar con PIL
                if img is None:
                    try:
                        from PIL import Image as PILImage
                        pil_img = PILImage.open(io.BytesIO(content))
                        
                        # Convertir a RGB si es necesario
                        if pil_img.mode in ('RGBA', 'LA'):
                            background = PILImage.new('RGB', pil_img.size, (255, 255, 255))
                            if pil_img.mode == 'RGBA':
                                background.paste(pil_img, mask=pil_img.split()[-1])
                            else:
                                background.paste(pil_img)
                            pil_img = background
                        elif pil_img.mode != 'RGB':
                            pil_img = pil_img.convert('RGB')
                        
                        # Convertir PIL a OpenCV (RGB -> BGR)
                        img_array = np.array(pil_img)
                        img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                        
                    except Exception as e:
                        print(f"⚠️ Error PIL en archivo {i+1}: {e}")
                        continue
                
                # Validar que la imagen se procesó correctamente
                if img is None:
                    print(f"⚠️ No se pudo decodificar archivo {i+1} ({file.filename})")
                    continue
                
                # Verificar dimensiones mínimas
                if len(img.shape) != 3 or img.shape[0] < 100 or img.shape[1] < 100:
                    print(f"⚠️ Imagen {i+1} muy pequeña o formato incorrecto: {img.shape if img is not None else 'None'}")
                    continue
                
                # Verificar que la imagen tiene contenido válido
                if img.dtype != np.uint8:
                    img = img.astype(np.uint8)
                
                images.append(img)
                print(f"✅ Imagen {i+1} procesada correctamente: {img.shape}")
                
                # Reset file pointer para posibles usos futuros
                await file.seek(0)
                
            except Exception as e:
                print(f"⚠️ Error general procesando archivo {i+1} ({file.filename}): {e}")
                continue
        
        print(f"📊 Resumen: {len(images)} imágenes válidas de {len(uploaded_files)} archivos subidos")
        return images
    
    async def _save_images_to_temp_directory(self, 
                                           uploaded_files: List[UploadFile],
                                           temp_dir: str) -> int:
        """
        Guarda archivos subidos como imágenes en un directorio temporal.
        
        Args:
            uploaded_files: Lista de archivos subidos
            temp_dir: Directorio temporal donde guardar
            
        Returns:
            Número de imágenes guardadas exitosamente
        """
        import os
        saved_count = 0
        
        for i, file in enumerate(uploaded_files):
            try:
                # Leer contenido del archivo
                content = await file.read()
                
                if len(content) == 0:
                    print(f"⚠️ Archivo {i+1} ({file.filename}) está vacío")
                    continue
                
                # Intentar decodificar y guardar la imagen
                img = None
                try:
                    # Método 1: OpenCV
                    nparr = np.frombuffer(content, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                except Exception as e:
                    print(f"⚠️ Error OpenCV en archivo {i+1}: {e}")
                
                # Método 2: PIL si OpenCV falla
                if img is None:
                    try:
                        from PIL import Image as PILImage
                        pil_img = PILImage.open(io.BytesIO(content))
                        
                        # Convertir a RGB si es necesario
                        if pil_img.mode in ('RGBA', 'LA'):
                            background = PILImage.new('RGB', pil_img.size, (255, 255, 255))
                            if pil_img.mode == 'RGBA':
                                background.paste(pil_img, mask=pil_img.split()[-1])
                            else:
                                background.paste(pil_img)
                            pil_img = background
                        elif pil_img.mode != 'RGB':
                            pil_img = pil_img.convert('RGB')
                        
                        # Convertir PIL a OpenCV
                        img_array = np.array(pil_img)
                        img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                        
                    except Exception as e:
                        print(f"⚠️ Error PIL en archivo {i+1}: {e}")
                        continue
                
                # Validar imagen
                if img is None or len(img.shape) != 3 or img.shape[0] < 100 or img.shape[1] < 100:
                    print(f"⚠️ Imagen {i+1} inválida o muy pequeña")
                    continue
                
                # Guardar imagen en directorio temporal
                filename = f"calibration_image_{i:03d}.jpg"
                filepath = os.path.join(temp_dir, filename)
                
                success = cv2.imwrite(filepath, img)
                if success:
                    saved_count += 1
                    print(f"✅ Imagen {i+1} guardada: {filename} ({img.shape})")
                else:
                    print(f"⚠️ No se pudo guardar imagen {i+1}")
                
                # Reset file pointer
                await file.seek(0)
                
            except Exception as e:
                print(f"⚠️ Error procesando archivo {i+1} ({file.filename}): {e}")
                continue
        
        print(f"💾 Guardadas {saved_count} imágenes de {len(uploaded_files)} archivos en {temp_dir}")
        return saved_count
    
    def validate_calibration_parameters(self, 
                                      pattern_size: tuple,
                                      square_size_mm: float) -> Dict[str, Union[bool, str]]:
        """
        Valida los parámetros de calibración.
        
        Args:
            pattern_size: Tamaño del patrón (cols, rows)
            square_size_mm: Tamaño del cuadrado en mm
            
        Returns:
            Diccionario con resultado de validación
        """
        # Validar pattern_size
        if not isinstance(pattern_size, (tuple, list)) or len(pattern_size) != 2:
            return {
                "valid": False,
                "error": "pattern_size debe ser una tupla de 2 elementos [cols, rows]"
            }
        
        if any(not isinstance(x, int) or x < 3 for x in pattern_size):
            return {
                "valid": False,
                "error": "pattern_size debe contener enteros mayores o iguales a 3"
            }
        
        # Validar square_size_mm
        if not isinstance(square_size_mm, (int, float)) or square_size_mm <= 0:
            return {
                "valid": False,
                "error": "square_size_mm debe ser un número positivo"
            }
        
        return {
            "valid": True,
            "message": "Parámetros válidos"
        }