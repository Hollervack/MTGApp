"""Service for managing MTG card images"""

import os
import requests
import hashlib
from PIL import Image, ImageTk
import io
from pathlib import Path
from typing import Optional, Tuple


class ImageService:
    """Service for downloading and caching card images"""
    
    def __init__(self, cache_dir: str = "cache/images"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MTGDeckConstructor/1.0'
        })
    
    def _get_cache_filename(self, url: str) -> Path:
        """Generates a unique filename based on the URL"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.jpg"
    
    def _download_image(self, url: str, timeout: int = 10) -> Optional[bytes]:
        """Downloads an image from a URL"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image from {url}: {e}")
            return None
    
    def _save_image_to_cache(self, image_data: bytes, cache_file: Path) -> bool:
        """Saves image data to cache"""
        try:
            with open(cache_file, 'wb') as f:
                f.write(image_data)
            return True
        except Exception as e:
            print(f"Error saving image to cache: {e}")
            return False
    
    def _load_image_from_cache(self, cache_file: Path) -> Optional[Image.Image]:
        """Loads an image from cache"""
        try:
            if cache_file.exists():
                return Image.open(cache_file)
        except Exception as e:
            print(f"Error loading image from cache: {e}")
        return None
    
    def _resize_image(self, image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """Resizes an image maintaining aspect ratio"""
        image.thumbnail(size, Image.Resampling.LANCZOS)
        return image
    
    def get_image_from_cache_only(self, url: str, size: Optional[Tuple[int, int]] = None) -> Optional[ImageTk.PhotoImage]:
        """Gets an image ONLY from cache, does not download if it doesn't exist"""
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
                print(f"Error converting image to PhotoImage: {e}")
        
        return None
    
    def download_and_cache_image(self, url: str, size: Optional[Tuple[int, int]] = None, timeout: int = 10) -> Optional[ImageTk.PhotoImage]:
        """Downloads an image, saves it to cache and returns it"""
        if not url:
            return None
        
        cache_file = self._get_cache_filename(url)
        
        # Try loading from cache first
        image = self._load_image_from_cache(cache_file)
        
        # If not in cache, download
        if not image:
            image_data = self._download_image(url, timeout)
            if image_data:
                # Save to cache
                self._save_image_to_cache(image_data, cache_file)
                
                # Load the image
                try:
                    image = Image.open(io.BytesIO(image_data))
                except Exception as e:
                    print(f"Error processing downloaded image: {e}")
                    return None
            else:
                return None
        
        # Resize if necessary
        if size:
            image = self._resize_image(image, size)
        
        # Convert to PhotoImage for Tkinter
        try:
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error converting image to PhotoImage: {e}")
            return None
    
    def get_image(self, url: str, size: Optional[Tuple[int, int]] = None, timeout: int = 10) -> Optional[ImageTk.PhotoImage]:
        """Gets an image (from cache or by downloading)"""
        return self.download_and_cache_image(url, size, timeout)
    
    def preload_image(self, url: str, timeout: int = 10) -> bool:
        """Preloads an image to cache without returning it"""
        if not url:
            return False
        
        cache_file = self._get_cache_filename(url)
        
        # If already in cache, do nothing
        if cache_file.exists():
            return True
        
        # Download and save
        image_data = self._download_image(url, timeout)
        if image_data:
            return self._save_image_to_cache(image_data, cache_file)
        
        return False
    
    def clear_cache(self) -> int:
        """Clears the image cache and returns the number of deleted files"""
        deleted_count = 0
        
        try:
            for file_path in self.cache_dir.glob("*.jpg"):
                file_path.unlink()
                deleted_count += 1
        except Exception as e:
            print(f"Error clearing cache: {e}")
        
        return deleted_count
    
    def get_cache_size(self) -> int:
        """Gets the cache size in bytes"""
        total_size = 0
        
        try:
            for file_path in self.cache_dir.glob("*.jpg"):
                total_size += file_path.stat().st_size
        except Exception as e:
            print(f"Error calculating cache size: {e}")
        
        return total_size
    
    def get_cache_count(self) -> int:
        """Gets the number of images in cache"""
        try:
            return len(list(self.cache_dir.glob("*.jpg")))
        except Exception as e:
            print(f"Error counting files in cache: {e}")
            return 0
    
    def get_cache_info(self) -> dict:
        """Gets complete cache information"""
        return {
            'count': self.get_cache_count(),
            'size_bytes': self.get_cache_size(),
            'size_mb': round(self.get_cache_size() / (1024 * 1024), 2),
            'cache_dir': str(self.cache_dir)
        }
    
    def is_image_cached(self, url: str) -> bool:
        """Checks if an image is in cache"""
        if not url:
            return False
        
        cache_file = self._get_cache_filename(url)
        return cache_file.exists()