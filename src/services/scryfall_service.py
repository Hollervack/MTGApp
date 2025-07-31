"""Servicio para interactuar con la API de Scryfall"""

import requests
import time
from typing import Optional, Dict, Any
from urllib.parse import quote


class ScryfallService:
    """Servicio para consultas a la API de Scryfall"""
    
    BASE_URL = "https://api.scryfall.com"
    RATE_LIMIT_DELAY = 0.1  # 100ms entre requests para respetar rate limits
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MTGDeckConstructor/1.0'
        })
        self._last_request_time = 0
    
    def _rate_limit(self) -> None:
        """Implementa rate limiting para respetar los límites de Scryfall"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - time_since_last)
        
        self._last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Realiza una petición HTTP a Scryfall con manejo de errores"""
        self._rate_limit()
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error en petición a Scryfall: {e}")
            return None
        except ValueError as e:
            print(f"Error al parsear respuesta JSON: {e}")
            return None
    
    def get_card_by_name(self, name: str, exact: bool = False) -> Optional[Dict[str, Any]]:
        """Busca una carta por nombre"""
        endpoint = "cards/named"
        params = {
            'exact' if exact else 'fuzzy': name
        }
        
        return self._make_request(endpoint, params)
    
    def get_card_by_id(self, scryfall_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una carta por su ID de Scryfall"""
        endpoint = f"cards/{scryfall_id}"
        return self._make_request(endpoint)
    
    def search_cards(self, query: str, page: int = 1) -> Optional[Dict[str, Any]]:
        """Busca cartas usando la sintaxis de búsqueda de Scryfall"""
        endpoint = "cards/search"
        params = {
            'q': query,
            'page': page
        }
        
        return self._make_request(endpoint, params)
    
    def get_card_image_url(self, card_name: str, image_type: str = 'normal') -> Optional[str]:
        """Obtiene la URL de la imagen de una carta"""
        card_data = self.get_card_by_name(card_name)
        
        if not card_data:
            return None
        
        image_uris = card_data.get('image_uris', {})
        
        # Prioridad de tipos de imagen
        image_priorities = [image_type, 'normal', 'large', 'small', 'png']
        
        for img_type in image_priorities:
            if img_type in image_uris:
                return image_uris[img_type]
        
        # Para cartas de doble cara
        if 'card_faces' in card_data:
            front_face = card_data['card_faces'][0]
            if 'image_uris' in front_face:
                for img_type in image_priorities:
                    if img_type in front_face['image_uris']:
                        return front_face['image_uris'][img_type]
        
        return None
    
    def get_random_card(self) -> Optional[Dict[str, Any]]:
        """Obtiene una carta aleatoria"""
        endpoint = "cards/random"
        return self._make_request(endpoint)
    
    def get_set_info(self, set_code: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de un set"""
        endpoint = f"sets/{set_code.lower()}"
        return self._make_request(endpoint)
    
    def get_all_sets(self) -> Optional[Dict[str, Any]]:
        """Obtiene lista de todos los sets"""
        endpoint = "sets"
        return self._make_request(endpoint)
    
    def autocomplete(self, query: str) -> Optional[Dict[str, Any]]:
        """Obtiene sugerencias de autocompletado para nombres de cartas"""
        endpoint = "cards/autocomplete"
        params = {'q': query}
        
        return self._make_request(endpoint, params)
    
    def get_card_rulings(self, scryfall_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene las reglas/aclaraciones de una carta"""
        endpoint = f"cards/{scryfall_id}/rulings"
        return self._make_request(endpoint)
    
    def get_card_prints(self, scryfall_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene todas las impresiones de una carta"""
        endpoint = f"cards/{scryfall_id}/prints"
        return self._make_request(endpoint)
    
    def validate_card_name(self, name: str) -> bool:
        """Valida si un nombre de carta existe en Scryfall"""
        card_data = self.get_card_by_name(name, exact=True)
        return card_data is not None
    
    def get_card_legalities(self, card_name: str) -> Optional[Dict[str, str]]:
        """Obtiene las legalidades de una carta en diferentes formatos"""
        card_data = self.get_card_by_name(card_name)
        
        if card_data and 'legalities' in card_data:
            return card_data['legalities']
        
        return None
    
    def search_by_color_identity(self, colors: str) -> Optional[Dict[str, Any]]:
        """Busca cartas por identidad de color"""
        query = f"id:{colors}"
        return self.search_cards(query)
    
    def search_by_type(self, card_type: str) -> Optional[Dict[str, Any]]:
        """Busca cartas por tipo"""
        query = f"type:{card_type}"
        return self.search_cards(query)
    
    def search_by_format(self, format_name: str, legality: str = "legal") -> Optional[Dict[str, Any]]:
        """Busca cartas legales en un formato específico"""
        query = f"format:{format_name} legal:{legality}"
        return self.search_cards(query)