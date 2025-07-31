"""Servicio para gestión de imágenes de cartas MTG"""

import os
import requests
import hashlib
from PIL import Image, ImageTk
import io
from pathlib import Path
from typing import Optional, Tuple


class ImageService:
    """Servicio para descarga y caché de imágenes de cartas"""
    
    def __init__(self, cache_dir: str = "cache/images"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MTGDeckConstructor/1.0'
        })
    
    def _get_cache_filename(self, url: str) -> Path:
        """Genera un nombre de archivo único basado en la URL"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.jpg"
    
    def _download_image(self, url: str, timeout: int = 10) -> Optional[bytes]:
        """Descarga una imagen desde una URL"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error al descargar imagen desde {url}: {e}")
            return None
    
    def _save_image_to_cache(self, image_data: bytes, cache_file: Path) -> bool:
        """Guarda datos de imagen en el caché"""
        try:
            with open(cache_file, 'wb') as f:
                f.write(image_data)
            return True
        except Exception as e:
            print(f"Error al guardar imagen en caché: {e}")
            return False
    
    def _load_image_from_cache(self, cache_file: Path) -> Optional[Image.Image]:
        """Carga una imagen desde el caché"""
        try:
            if cache_file.exists():
                return Image.open(cache_file)
        except Exception as e:
            print(f"Error al cargar imagen desde caché: {e}")
        return None
    
    def _resize_image(self, image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """Redimensiona una imagen manteniendo la proporción"""
        image.thumbnail(size, Image.Resampling.LANCZOS)
        return image
    
    def get_image_from_cache_only(self, url: str, size: Optional[Tuple[int, int]] = None) -> Optional[ImageTk.PhotoImage]:
        """Obtiene una imagen SOLO desde caché, no descarga si no existe"""
        if not url:
            return None
        
        cache_file = self._get_cache_filename(url)
        image = self._load_image_from_cache(cache_file)
        
        if image:
            if size:
                image = self._resize_image(image, size)
            
            try:
                return ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Error al convertir imagen a PhotoImage: {e}")
        
        return None
    
    def download_and_cache_image(self, url: str, size: Optional[Tuple[int, int]] = None, timeout: int = 10) -> Optional[ImageTk.PhotoImage]:
        """Descarga una imagen, la guarda en caché y la retorna"""
        if not url:
            return None
        
        cache_file = self._get_cache_filename(url)
        
        # Intentar cargar desde caché primero
        image = self._load_image_from_cache(cache_file)
        
        # Si no está en caché, descargar
        if not image:
            image_data = self._download_image(url, timeout)
            if image_data:
                # Guardar en caché
                self._save_image_to_cache(image_data, cache_file)
                
                # Cargar la imagen
                try:
                    image = Image.open(io.BytesIO(image_data))
                except Exception as e:
                    print(f"Error al procesar imagen descargada: {e}")
                    return None
            else:
                return None
        
        # Redimensionar si es necesario
        if size:
            image = self._resize_image(image, size)
        
        # Convertir a PhotoImage para Tkinter
        try:
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error al convertir imagen a PhotoImage: {e}")
            return None
    
    def get_image(self, url: str, size: Optional[Tuple[int, int]] = None, timeout: int = 10) -> Optional[ImageTk.PhotoImage]:
        """Obtiene una imagen (desde caché o descargando)"""
        return self.download_and_cache_image(url, size, timeout)
    
    def preload_image(self, url: str, timeout: int = 10) -> bool:
        """Precarga una imagen en el caché sin retornarla"""
        if not url:
            return False
        
        cache_file = self._get_cache_filename(url)
        
        # Si ya está en caché, no hacer nada
        if cache_file.exists():
            return True
        
        # Descargar y guardar
        image_data = self._download_image(url, timeout)
        if image_data:
            return self._save_image_to_cache(image_data, cache_file)
        
        return False
    
    def clear_cache(self) -> int:
        """Limpia el caché de imágenes y retorna el número de archivos eliminados"""
        deleted_count = 0
        
        try:
            for file_path in self.cache_dir.glob("*.jpg"):
                file_path.unlink()
                deleted_count += 1
        except Exception as e:
            print(f"Error al limpiar caché: {e}")
        
        return deleted_count
    
    def get_cache_size(self) -> int:
        """Obtiene el tamaño del caché en bytes"""
        total_size = 0
        
        try:
            for file_path in self.cache_dir.glob("*.jpg"):
                total_size += file_path.stat().st_size
        except Exception as e:
            print(f"Error al calcular tamaño del caché: {e}")
        
        return total_size
    
    def get_cache_count(self) -> int:
        """Obtiene el número de imágenes en caché"""
        try:
            return len(list(self.cache_dir.glob("*.jpg")))
        except Exception as e:
            print(f"Error al contar archivos en caché: {e}")
            return 0
    
    def get_cache_info(self) -> dict:
        """Obtiene información completa del caché"""
        return {
            'count': self.get_cache_count(),
            'size_bytes': self.get_cache_size(),
            'size_mb': round(self.get_cache_size() / (1024 * 1024), 2),
            'cache_dir': str(self.cache_dir)
        }
    
    def is_image_cached(self, url: str) -> bool:
        """Verifica si una imagen está en caché"""
        if not url:
            return False
        
        cache_file = self._get_cache_filename(url)
        return cache_file.exists()