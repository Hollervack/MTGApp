import os
import requests
import hashlib
from PIL import Image, ImageTk
import io
from pathlib import Path

class ImageCache:
    def __init__(self, cache_dir="cache/images"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_filename(self, url):
        """Genera un nombre de archivo único basado en la URL"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.jpg"
    
    def get_image_from_cache_only(self, url, size=None):
        """Obtiene una imagen SOLO desde caché, no descarga si no existe"""
        if not url:
            return None
            
        cache_file = self._get_cache_filename(url)
        
        # Solo cargar si la imagen está en caché
        if cache_file.exists():
            try:
                image = Image.open(cache_file)
                if size:
                    image.thumbnail(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
            except Exception:
                # Si hay error al cargar, eliminar archivo corrupto
                cache_file.unlink(missing_ok=True)
        
        return None
    
    def download_and_cache_image(self, url, size=None, timeout=10):
        """Descarga y guarda una imagen en caché (solo para refrescar)"""
        if not url:
            return None
            
        cache_file = self._get_cache_filename(url)
        
        # Descargar imagen
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                # Guardar imagen original en caché
                with open(cache_file, 'wb') as f:
                    f.write(response.content)
                
                # Cargar y redimensionar si es necesario
                image = Image.open(io.BytesIO(response.content))
                if size:
                    image.thumbnail(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
        except Exception:
            pass
            
        return None
    
    def get_image(self, url, size=None, timeout=10):
        """Método de compatibilidad - ahora solo usa caché"""
        return self.get_image_from_cache_only(url, size)
    
    def clear_cache(self):
        """Limpia todo el caché de imágenes"""
        try:
            for file in self.cache_dir.glob("*.jpg"):
                file.unlink()
            return True
        except Exception:
            return False
    
    def get_cache_size(self):
        """Obtiene el tamaño del caché en MB"""
        try:
            total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.jpg"))
            return total_size / (1024 * 1024)  # Convertir a MB
        except Exception:
            return 0
    
    def get_cache_count(self):
        """Obtiene el número de imágenes en caché"""
        try:
            return len(list(self.cache_dir.glob("*.jpg")))
        except Exception:
            return 0

# Instancia global del caché
image_cache = ImageCache()