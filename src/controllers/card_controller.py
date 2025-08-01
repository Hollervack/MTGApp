"""Controller for MTG card management"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..models.card import Card
from ..services.card_service import CardService
from ..services.scryfall_service import ScryfallService
from ..services.image_service import ImageService


class CardController:
    """Controller for card operations"""
    
    def __init__(self, card_service: CardService, scryfall_service: ScryfallService, 
                 image_service: ImageService):
        self.card_service = card_service
        self.scryfall_service = scryfall_service
        self.image_service = image_service
        self.logger = logging.getLogger('MTGDeckConstructor.CardController')
        self._search_cache = {}
    
    def search_cards(self, query: str, limit: int = 50) -> List[Card]:
        """Searches for cards by name"""
        try:
            # Check cache
            cache_key = f"{query.lower()}_{limit}"
            if cache_key in self._search_cache:
                return self._search_cache[cache_key]
            
            results = self.card_service.search_cards(query)
            
            # Limit results
            if limit > 0:
                results = results[:limit]
            
            # Save to cache
            self._search_cache[cache_key] = results
            
            self.logger.info(f"Search '{query}': {len(results)} results")
            return results
        except Exception as e:
            self.logger.error(f"Error in card search: {e}")
            return []
    
    def get_card_by_name(self, name: str) -> Optional[Card]:
        """Gets a specific card by exact name"""
        try:
            return self.card_service.find_card_by_name(name)
        except Exception as e:
            self.logger.error(f"Error getting card {name}: {e}")
            return None
    
    def get_cards_by_color(self, colors: List[str]) -> List[Card]:
        """Gets cards by colors"""
        try:
            all_cards = self.card_service.load_cards()
            return self.card_service.filter_by_color(all_cards, colors)
        except Exception as e:
            self.logger.error(f"Error filtering by colors: {e}")
            return []
    
    def get_cards_by_type(self, card_type: str) -> List[Card]:
        """Gets cards by type"""
        try:
            all_cards = self.card_service.load_cards()
            return self.card_service.filter_by_type(all_cards, card_type)
        except Exception as e:
            self.logger.error(f"Error filtering by type: {e}")
            return []
    
    def get_cards_by_rarity(self, rarity: str) -> List[Card]:
        """Gets cards by rarity"""
        try:
            all_cards = self.card_service.load_cards()
            return self.card_service.filter_by_rarity(all_cards, rarity)
        except Exception as e:
            self.logger.error(f"Error filtering by rarity: {e}")
            return []
    
    def get_cards_by_set(self, set_code: str) -> List[Card]:
        """Gets cards by set"""
        try:
            all_cards = self.card_service.load_cards()
            return self.card_service.filter_by_set(all_cards, set_code)
        except Exception as e:
            self.logger.error(f"Error filtering by set: {e}")
            return []
    
    def advanced_search(self, filters: Dict[str, Any]) -> List[Card]:
        """Advanced search with multiple filters"""
        try:
            # Start with all cards or with a text search
            if 'query' in filters and filters['query']:
                results = self.search_cards(filters['query'], limit=0)
            else:
                results = self.card_service.load_cards()
            
            # Apply filters
            if 'colors' in filters and filters['colors']:
                results = self.card_service.filter_by_color(results, filters['colors'])
            
            if 'type' in filters and filters['type']:
                results = self.card_service.filter_by_type(results, filters['type'])
            
            if 'rarity' in filters and filters['rarity']:
                results = self.card_service.filter_by_rarity(results, filters['rarity'])
            
            if 'set' in filters and filters['set']:
                results = self.card_service.filter_by_set(results, filters['set'])
            
            # Additional filters
            if 'min_cmc' in filters:
                results = [card for card in results 
                          if card.get_simplified_cmc() >= filters['min_cmc']]
            
            if 'max_cmc' in filters:
                results = [card for card in results 
                          if card.get_simplified_cmc() <= filters['max_cmc']]
            
            if 'creatures_only' in filters and filters['creatures_only']:
                results = [card for card in results if card.is_creature()]
            
            # Sort results
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
            
            # Limit results
            limit = filters.get('limit', 100)
            if limit > 0:
                results = results[:limit]
            
            self.logger.info(f"Advanced search: {len(results)} results")
            return results
        except Exception as e:
            self.logger.error(f"Error in advanced search: {e}")
            return []
    
    def get_card_image(self, card: Card, size: str = 'normal') -> Optional[str]:
        """Gets the image of a card"""
        try:
            # Try to get from cache
            image_path = self.image_service.get_image(card.card_name, size)
            
            if image_path and Path(image_path).exists():
                return image_path
            
            # If not in cache, try to download
            return self._download_card_image(card, size)
        except Exception as e:
            self.logger.error(f"Error getting image of {card.card_name}: {e}")
            return None
    
    def _download_card_image(self, card: Card, size: str = 'normal') -> Optional[str]:
        """Downloads the image of a card from Scryfall"""
        try:
            # Search for card in Scryfall
            scryfall_card = self.scryfall_service.get_card_by_name(card.card_name)
            
            if not scryfall_card:
                self.logger.warning(f"Card not found in Scryfall: {card.card_name}")
                return None
            
            # Get image URL
            image_uris = scryfall_card.get('image_uris', {})
            if not image_uris:
                # Double-faced cards may have images in card_faces
                card_faces = scryfall_card.get('card_faces', [])
                if card_faces and 'image_uris' in card_faces[0]:
                    image_uris = card_faces[0]['image_uris']
            
            if not image_uris:
                self.logger.warning(f"No images found for {card.card_name}")
                return None
            
            # Select image size
            image_url = image_uris.get(size)
            if not image_url:
                # Fallback to normal size if requested is not available
                image_url = image_uris.get('normal')
            
            if not image_url:
                self.logger.warning(f"Image URL not available for {card.card_name}")
                return None
            
            # Download image
            downloaded_path = self.image_service.download_image(
                image_url, card.card_name, size
            )
            
            if downloaded_path:
                self.logger.info(f"Image downloaded: {card.card_name}")
            
            return downloaded_path
        except Exception as e:
            self.logger.error(f"Error downloading image of {card.card_name}: {e}")
            return None
    
    def preload_images(self, cards: List[Card], size: str = 'normal', 
                      max_concurrent: int = 5) -> Dict[str, bool]:
        """Preloads images of multiple cards"""
        try:
            results = {}
            
            # Filter cards that already have image in cache
            cards_to_download = []
            for card in cards:
                cached_path = self.image_service.get_image(card.card_name, size)
                if cached_path and Path(cached_path).exists():
                    results[card.card_name] = True
                else:
                    cards_to_download.append(card)
            
            # Download missing images
            for card in cards_to_download:
                try:
                    image_path = self._download_card_image(card, size)
                    results[card.card_name] = image_path is not None
                except Exception as e:
                    self.logger.error(f"Error preloading image of {card.card_name}: {e}")
                    results[card.card_name] = False
            
            successful = sum(1 for success in results.values() if success)
            self.logger.info(f"Preload completed: {successful}/{len(cards)} images")
            
            return results
        except Exception as e:
            self.logger.error(f"Error in image preload: {e}")
            return {}
    
    def get_card_details_from_scryfall(self, card_name: str) -> Optional[Dict[str, Any]]:
        """Gets complete details of a card from Scryfall"""
        try:
            return self.scryfall_service.get_card_by_name(card_name)
        except Exception as e:
            self.logger.error(f"Error getting Scryfall details for {card_name}: {e}")
            return None
    
    def get_card_rulings(self, card_name: str) -> List[Dict[str, Any]]:
        """Gets the rules/clarifications of a card"""
        try:
            return self.scryfall_service.get_card_rulings(card_name)
        except Exception as e:
            self.logger.error(f"Error getting rules for {card_name}: {e}")
            return []
    
    def get_available_sets(self) -> List[str]:
        """Gets list of available sets"""
        try:
            return self.card_service.get_available_sets()
        except Exception as e:
            self.logger.error(f"Error getting available sets: {e}")
            return []
    
    def get_available_types(self) -> List[str]:
        """Gets list of available types"""
        try:
            return self.card_service.get_available_types()
        except Exception as e:
            self.logger.error(f"Error getting available types: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Gets collection statistics"""
        try:
            return self.card_service.get_collection_stats()
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}
    
    def update_card_quantity(self, card_name: str, new_quantity: int) -> bool:
        """Updates the quantity of a card in the collection"""
        try:
            card = self.card_service.find_card_by_name(card_name)
            if not card:
                self.logger.warning(f"Card not found: {card_name}")
                return False
            
            old_quantity = card.quantity
            card.quantity = max(0, new_quantity)  # Don't allow negative quantities
            
            # Here persistence of changes could be implemented
            # For now we only update in memory
            
            self.logger.info(f"Quantity updated for {card_name}: {old_quantity} -> {new_quantity}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating quantity: {e}")
            return False
    
    def clear_search_cache(self):
        """Clears the search cache"""
        self._search_cache.clear()
        self.logger.info("Search cache cleared")
    
    def get_random_cards(self, count: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Card]:
        """Gets random cards"""
        try:
            import random
            
            # Get all cards or apply filters
            if filters:
                cards = self.advanced_search(filters)
            else:
                cards = self.card_service.load_cards()
            
            # Select randomly
            if len(cards) <= count:
                return cards
            
            return random.sample(cards, count)
        except Exception as e:
            self.logger.error(f"Error getting random cards: {e}")
            return []
    
    def get_similar_cards(self, card: Card, limit: int = 10) -> List[Card]:
        """Gets similar cards based on type and mana cost"""
        try:
            all_cards = self.card_service.load_cards()
            similar_cards = []
            
            card_cmc = card.get_simplified_cmc()
            card_types = card.type_line.lower().split() if card.type_line else []
            
            for other_card in all_cards:
                if other_card.card_name == card.card_name:
                    continue
                
                score = 0
                
                # Score for similar CMC
                other_cmc = other_card.get_simplified_cmc()
                if abs(card_cmc - other_cmc) <= 1:
                    score += 3
                elif abs(card_cmc - other_cmc) <= 2:
                    score += 1
                
                # Score for shared types
                other_types = other_card.type_line.lower().split() if other_card.type_line else []
                shared_types = set(card_types) & set(other_types)
                score += len(shared_types) * 2
                
                # Score for shared colors
                if card.colors and other_card.colors:
                    shared_colors = set(card.colors) & set(other_card.colors)
                    score += len(shared_colors)
                
                if score > 0:
                    similar_cards.append((other_card, score))
            
            # Sort by score and return the best
            similar_cards.sort(key=lambda x: x[1], reverse=True)
            return [card for card, score in similar_cards[:limit]]
        except Exception as e:
            self.logger.error(f"Error getting similar cards: {e}")
            return []