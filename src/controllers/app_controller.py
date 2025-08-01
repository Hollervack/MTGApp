"""Main controller for the MTG Deck Constructor application"""

import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

from ..config.settings import get_settings
from ..services.card_service import CardService
from ..services.deck_service import DeckService
from ..services.image_service import ImageService
from ..services.scryfall_service import ScryfallService
from ..models.deck import Deck
from ..models.card import Card


class AppController:
    """Main controller that coordinates all application services"""
    
    def __init__(self):
        self.settings = get_settings()
        self._setup_logging()
        self._initialize_services()
        self._ensure_directories()
    
    def _setup_logging(self):
        """Configures the logging system"""
        log_level = getattr(logging, self.settings.get('logging.level', 'INFO'))
        
        # Configure format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Main logger
        self.logger = logging.getLogger('MTGDeckConstructor')
        self.logger.setLevel(log_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        if self.settings.get('logging.console_enabled', True):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if self.settings.get('logging.file_enabled', True):
            log_file = Path(self.settings.get('logging.file_path', 'logs/app.log'))
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        self.logger.info(f"Starting {self.settings.app_name} v{self.settings.app_version}")
    
    def _initialize_services(self):
        """Initializes all services"""
        try:
            # Card service
            self.card_service = CardService(
                data_path=self.settings.cards_file
            )
            
            # Image service
            self.image_service = ImageService(
                cache_dir=self.settings.images_directory
            )
            
            # Scryfall service
            self.scryfall_service = ScryfallService()
            
            # Deck service
            self.deck_service = DeckService(
                card_service=self.card_service,
                decks_dir=self.settings.decks_directory
            )
            
            self.logger.info("Services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing services: {e}")
            raise
    
    def _ensure_directories(self):
        """Ensures all necessary directories exist"""
        directories = [
            self.settings.decks_directory,
            self.settings.cache_directory,
            self.settings.images_directory,
            self.settings.get('data.backup_directory', 'data/backups'),
            Path(self.settings.get('logging.file_path', 'logs/app.log')).parent
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def initialize_application(self) -> bool:
        """Initializes the application and loads initial data"""
        try:
            self.logger.info("Initializing application...")
            
            # Load cards
            cards = self.card_service.load_cards()
            self.logger.info(f"Loaded {len(cards)} cards")
            
            # Verify Scryfall connectivity (optional)
            if self.settings.get('api.test_connection', False):
                try:
                    test_card = self.scryfall_service.get_card_by_name("Lightning Bolt")
                    if test_card:
                        self.logger.info("Scryfall API connection verified")
                except Exception as e:
                    self.logger.warning(f"Could not connect to Scryfall API: {e}")
            
            self.logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing application: {e}")
            return False
    
    def shutdown(self):
        """Closes the application cleanly"""
        try:
            self.logger.info("Closing application...")
            
            # Save configurations
            self.settings.save()
            
            # Clear cache if necessary
            if self.settings.get('images.clear_cache_on_exit', False):
                self.image_service.clear_cache()
            
            self.logger.info("Application closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error closing application: {e}")
    
    # Service access methods
    def get_card_service(self) -> CardService:
        """Gets the card service"""
        return self.card_service
    
    def get_deck_service(self) -> DeckService:
        """Gets the deck service"""
        return self.deck_service
    
    def get_image_service(self) -> ImageService:
        """Gets the image service"""
        return self.image_service
    
    def get_scryfall_service(self) -> ScryfallService:
        """Gets the Scryfall service"""
        return self.scryfall_service
    
    def get_settings(self):
        """Gets the configurations"""
        return self.settings
    
    # Convenience methods for common operations
    def search_cards(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Card]:
        """Searches for cards with optional filters"""
        try:
            results = self.card_service.search_cards(query)
            
            if filters:
                # Apply additional filters
                if 'color' in filters:
                    results = self.card_service.filter_by_color(results, filters['color'])
                
                if 'type' in filters:
                    results = self.card_service.filter_by_type(results, filters['type'])
                
                if 'rarity' in filters:
                    results = self.card_service.filter_by_rarity(results, filters['rarity'])
                
                if 'set' in filters:
                    results = self.card_service.filter_by_set(results, filters['set'])
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching cards: {e}")
            return []
    
    def get_card_image(self, card: Card, size: str = 'normal') -> Optional[str]:
        """Gets the image of a card"""
        try:
            # Try to get from cache first
            image_path = self.image_service.get_image(card.card_name, size)
            
            if image_path and Path(image_path).exists():
                return image_path
            
            # If not in cache, try to download from Scryfall
            if self.settings.auto_download_images:
                scryfall_card = self.scryfall_service.get_card_by_name(card.card_name)
                
                if scryfall_card and 'image_uris' in scryfall_card:
                    image_url = scryfall_card['image_uris'].get(size, 
                                scryfall_card['image_uris'].get('normal'))
                    
                    if image_url:
                        downloaded_path = self.image_service.download_image(
                            image_url, card.card_name, size
                        )
                        return downloaded_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting card image {card.card_name}: {e}")
            return None
    
    def create_deck_from_list(self, deck_name: str, card_list: List[str], 
                             format: Optional[str] = None) -> Optional[Deck]:
        """Creates a deck from a list of card names"""
        try:
            deck = self.deck_service.create_deck(deck_name, format)
            
            for card_entry in card_list:
                # Parse entry (e.g.: "4x Lightning Bolt" or "Lightning Bolt")
                parts = card_entry.strip().split(' ', 1)
                
                if len(parts) == 1:
                    quantity = 1
                    card_name = parts[0]
                else:
                    try:
                        quantity_str = parts[0].rstrip('x')
                        quantity = int(quantity_str)
                        card_name = parts[1]
                    except ValueError:
                        quantity = 1
                        card_name = card_entry.strip()
                
                # Search for card
                card = self.card_service.find_card_by_name(card_name)
                
                if card:
                    deck.add_card(card, quantity)
                else:
                    self.logger.warning(f"Card not found: {card_name}")
            
            return deck
            
        except Exception as e:
            self.logger.error(f"Error creating deck from list: {e}")
            return None
    
    def get_application_stats(self) -> Dict[str, Any]:
        """Gets application statistics"""
        try:
            stats = {
                'app_info': {
                    'name': self.settings.app_name,
                    'version': self.settings.app_version,
                    'debug_mode': self.settings.debug_mode
                },
                'collection_stats': self.card_service.get_collection_stats(),
                'deck_stats': {
                    'total_decks': len(self.deck_service.list_decks())
                },
                'cache_stats': self.image_service.get_cache_info()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}