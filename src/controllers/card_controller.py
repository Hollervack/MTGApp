"""Controlador para gestión de cartas MTG"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..models.card import Card
from ..services.card_service import CardService
from ..services.scryfall_service import ScryfallService
from ..services.image_service import ImageService


class CardController:
    """Controlador para operaciones con cartas"""
    
    def __init__(self, card_service: CardService, scryfall_service: ScryfallService, 
                 image_service: ImageService):
        self.card_service = card_service
        self.scryfall_service = scryfall_service
        self.image_service = image_service
        self.logger = logging.getLogger('MTGDeckConstructor.CardController')
        self._search_cache = {}
    
    def search_cards(self, query: str, limit: int = 50) -> List[Card]:
        """Busca cartas por nombre"""
        try:
            # Verificar caché
            cache_key = f"{query.lower()}_{limit}"
            if cache_key in self._search_cache:
                return self._search_cache[cache_key]
            
            results = self.card_service.search_cards(query)
            
            # Limitar resultados
            if limit > 0:
                results = results[:limit]
            
            # Guardar en caché
            self._search_cache[cache_key] = results
            
            self.logger.info(f"Búsqueda '{query}': {len(results)} resultados")
            return results
        except Exception as e:
            self.logger.error(f"Error en búsqueda de cartas: {e}")
            return []
    
    def get_card_by_name(self, name: str) -> Optional[Card]:
        """Obtiene una carta específica por nombre exacto"""
        try:
            return self.card_service.find_card_by_name(name)
        except Exception as e:
            self.logger.error(f"Error al obtener carta {name}: {e}")
            return None
    
    def get_cards_by_color(self, colors: List[str]) -> List[Card]:
        """Obtiene cartas por colores"""
        try:
            all_cards = self.card_service.load_cards()
            return self.card_service.filter_by_color(all_cards, colors)
        except Exception as e:
            self.logger.error(f"Error al filtrar por colores: {e}")
            return []
    
    def get_cards_by_type(self, card_type: str) -> List[Card]:
        """Obtiene cartas por tipo"""
        try:
            all_cards = self.card_service.load_cards()
            return self.card_service.filter_by_type(all_cards, card_type)
        except Exception as e:
            self.logger.error(f"Error al filtrar por tipo: {e}")
            return []
    
    def get_cards_by_rarity(self, rarity: str) -> List[Card]:
        """Obtiene cartas por rareza"""
        try:
            all_cards = self.card_service.load_cards()
            return self.card_service.filter_by_rarity(all_cards, rarity)
        except Exception as e:
            self.logger.error(f"Error al filtrar por rareza: {e}")
            return []
    
    def get_cards_by_set(self, set_code: str) -> List[Card]:
        """Obtiene cartas por set"""
        try:
            all_cards = self.card_service.load_cards()
            return self.card_service.filter_by_set(all_cards, set_code)
        except Exception as e:
            self.logger.error(f"Error al filtrar por set: {e}")
            return []
    
    def advanced_search(self, filters: Dict[str, Any]) -> List[Card]:
        """Búsqueda avanzada con múltiples filtros"""
        try:
            # Comenzar con todas las cartas o con una búsqueda de texto
            if 'query' in filters and filters['query']:
                results = self.search_cards(filters['query'], limit=0)
            else:
                results = self.card_service.load_cards()
            
            # Aplicar filtros
            if 'colors' in filters and filters['colors']:
                results = self.card_service.filter_by_color(results, filters['colors'])
            
            if 'type' in filters and filters['type']:
                results = self.card_service.filter_by_type(results, filters['type'])
            
            if 'rarity' in filters and filters['rarity']:
                results = self.card_service.filter_by_rarity(results, filters['rarity'])
            
            if 'set' in filters and filters['set']:
                results = self.card_service.filter_by_set(results, filters['set'])
            
            # Filtros adicionales
            if 'min_cmc' in filters:
                results = [card for card in results 
                          if card.get_simplified_cmc() >= filters['min_cmc']]
            
            if 'max_cmc' in filters:
                results = [card for card in results 
                          if card.get_simplified_cmc() <= filters['max_cmc']]
            
            if 'creatures_only' in filters and filters['creatures_only']:
                results = [card for card in results if card.is_creature()]
            
            # Ordenar resultados
            sort_by = filters.get('sort_by', 'name')
            reverse = filters.get('sort_desc', False)
            
            if sort_by == 'name':
                results.sort(key=lambda c: c.card_name or '', reverse=reverse)
            elif sort_by == 'cmc':
                results.sort(key=lambda c: c.get_simplified_cmc(), reverse=reverse)
            elif sort_by == 'rarity':
                rarity_order = {'common': 1, 'uncommon': 2, 'rare': 3, 'mythic': 4}
                results.sort(key=lambda c: rarity_order.get(c.rarity.lower() if c.rarity else '', 0), 
                           reverse=reverse)
            
            # Limitar resultados
            limit = filters.get('limit', 100)
            if limit > 0:
                results = results[:limit]
            
            self.logger.info(f"Búsqueda avanzada: {len(results)} resultados")
            return results
        except Exception as e:
            self.logger.error(f"Error en búsqueda avanzada: {e}")
            return []
    
    def get_card_image(self, card: Card, size: str = 'normal') -> Optional[str]:
        """Obtiene la imagen de una carta"""
        try:
            # Intentar obtener desde caché
            image_path = self.image_service.get_image(card.card_name, size)
            
            if image_path and Path(image_path).exists():
                return image_path
            
            # Si no está en caché, intentar descargar
            return self._download_card_image(card, size)
        except Exception as e:
            self.logger.error(f"Error al obtener imagen de {card.card_name}: {e}")
            return None
    
    def _download_card_image(self, card: Card, size: str = 'normal') -> Optional[str]:
        """Descarga la imagen de una carta desde Scryfall"""
        try:
            # Buscar carta en Scryfall
            scryfall_card = self.scryfall_service.get_card_by_name(card.card_name)
            
            if not scryfall_card:
                self.logger.warning(f"Carta no encontrada en Scryfall: {card.card_name}")
                return None
            
            # Obtener URL de imagen
            image_uris = scryfall_card.get('image_uris', {})
            if not image_uris:
                # Cartas de doble cara pueden tener imágenes en card_faces
                card_faces = scryfall_card.get('card_faces', [])
                if card_faces and 'image_uris' in card_faces[0]:
                    image_uris = card_faces[0]['image_uris']
            
            if not image_uris:
                self.logger.warning(f"No se encontraron imágenes para {card.card_name}")
                return None
            
            # Seleccionar tamaño de imagen
            image_url = image_uris.get(size)
            if not image_url:
                # Fallback a tamaño normal si el solicitado no está disponible
                image_url = image_uris.get('normal')
            
            if not image_url:
                self.logger.warning(f"URL de imagen no disponible para {card.card_name}")
                return None
            
            # Descargar imagen
            downloaded_path = self.image_service.download_image(
                image_url, card.card_name, size
            )
            
            if downloaded_path:
                self.logger.info(f"Imagen descargada: {card.card_name}")
            
            return downloaded_path
        except Exception as e:
            self.logger.error(f"Error al descargar imagen de {card.card_name}: {e}")
            return None
    
    def preload_images(self, cards: List[Card], size: str = 'normal', 
                      max_concurrent: int = 5) -> Dict[str, bool]:
        """Precarga imágenes de múltiples cartas"""
        try:
            results = {}
            
            # Filtrar cartas que ya tienen imagen en caché
            cards_to_download = []
            for card in cards:
                cached_path = self.image_service.get_image(card.card_name, size)
                if cached_path and Path(cached_path).exists():
                    results[card.card_name] = True
                else:
                    cards_to_download.append(card)
            
            # Descargar imágenes faltantes
            for card in cards_to_download:
                try:
                    image_path = self._download_card_image(card, size)
                    results[card.card_name] = image_path is not None
                except Exception as e:
                    self.logger.error(f"Error al precargar imagen de {card.card_name}: {e}")
                    results[card.card_name] = False
            
            successful = sum(1 for success in results.values() if success)
            self.logger.info(f"Precarga completada: {successful}/{len(cards)} imágenes")
            
            return results
        except Exception as e:
            self.logger.error(f"Error en precarga de imágenes: {e}")
            return {}
    
    def get_card_details_from_scryfall(self, card_name: str) -> Optional[Dict[str, Any]]:
        """Obtiene detalles completos de una carta desde Scryfall"""
        try:
            return self.scryfall_service.get_card_by_name(card_name)
        except Exception as e:
            self.logger.error(f"Error al obtener detalles de Scryfall para {card_name}: {e}")
            return None
    
    def get_card_rulings(self, card_name: str) -> List[Dict[str, Any]]:
        """Obtiene las reglas/aclaraciones de una carta"""
        try:
            return self.scryfall_service.get_card_rulings(card_name)
        except Exception as e:
            self.logger.error(f"Error al obtener reglas para {card_name}: {e}")
            return []
    
    def get_available_sets(self) -> List[str]:
        """Obtiene lista de sets disponibles"""
        try:
            return self.card_service.get_available_sets()
        except Exception as e:
            self.logger.error(f"Error al obtener sets disponibles: {e}")
            return []
    
    def get_available_types(self) -> List[str]:
        """Obtiene lista de tipos disponibles"""
        try:
            return self.card_service.get_available_types()
        except Exception as e:
            self.logger.error(f"Error al obtener tipos disponibles: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la colección"""
        try:
            return self.card_service.get_collection_stats()
        except Exception as e:
            self.logger.error(f"Error al obtener estadísticas: {e}")
            return {}
    
    def update_card_quantity(self, card_name: str, new_quantity: int) -> bool:
        """Actualiza la cantidad de una carta en la colección"""
        try:
            card = self.card_service.find_card_by_name(card_name)
            if not card:
                self.logger.warning(f"Carta no encontrada: {card_name}")
                return False
            
            old_quantity = card.quantity
            card.quantity = max(0, new_quantity)  # No permitir cantidades negativas
            
            # Aquí se podría implementar la persistencia de cambios
            # Por ahora solo actualizamos en memoria
            
            self.logger.info(f"Cantidad actualizada para {card_name}: {old_quantity} -> {new_quantity}")
            return True
        except Exception as e:
            self.logger.error(f"Error al actualizar cantidad: {e}")
            return False
    
    def clear_search_cache(self):
        """Limpia la caché de búsquedas"""
        self._search_cache.clear()
        self.logger.info("Caché de búsquedas limpiada")
    
    def get_random_cards(self, count: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Card]:
        """Obtiene cartas aleatorias"""
        try:
            import random
            
            # Obtener todas las cartas o aplicar filtros
            if filters:
                cards = self.advanced_search(filters)
            else:
                cards = self.card_service.load_cards()
            
            # Seleccionar aleatoriamente
            if len(cards) <= count:
                return cards
            
            return random.sample(cards, count)
        except Exception as e:
            self.logger.error(f"Error al obtener cartas aleatorias: {e}")
            return []
    
    def get_similar_cards(self, card: Card, limit: int = 10) -> List[Card]:
        """Obtiene cartas similares basadas en tipo y coste de maná"""
        try:
            all_cards = self.card_service.load_cards()
            similar_cards = []
            
            card_cmc = card.get_simplified_cmc()
            card_types = card.type_line.lower().split() if card.type_line else []
            
            for other_card in all_cards:
                if other_card.card_name == card.card_name:
                    continue
                
                score = 0
                
                # Puntuación por CMC similar
                other_cmc = other_card.get_simplified_cmc()
                if abs(card_cmc - other_cmc) <= 1:
                    score += 3
                elif abs(card_cmc - other_cmc) <= 2:
                    score += 1
                
                # Puntuación por tipos compartidos
                other_types = other_card.type_line.lower().split() if other_card.type_line else []
                shared_types = set(card_types) & set(other_types)
                score += len(shared_types) * 2
                
                # Puntuación por colores compartidos
                if card.colors and other_card.colors:
                    shared_colors = set(card.colors) & set(other_card.colors)
                    score += len(shared_colors)
                
                if score > 0:
                    similar_cards.append((other_card, score))
            
            # Ordenar por puntuación y devolver los mejores
            similar_cards.sort(key=lambda x: x[1], reverse=True)
            return [card for card, score in similar_cards[:limit]]
        except Exception as e:
            self.logger.error(f"Error al obtener cartas similares: {e}")
            return []