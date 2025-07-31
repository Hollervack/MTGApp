"""Controlador principal de la aplicación MTG Deck Constructor"""

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
    """Controlador principal que coordina todos los servicios de la aplicación"""
    
    def __init__(self):
        self.settings = get_settings()
        self._setup_logging()
        self._initialize_services()
        self._ensure_directories()
    
    def _setup_logging(self):
        """Configura el sistema de logging"""
        log_level = getattr(logging, self.settings.get('logging.level', 'INFO'))
        
        # Configurar formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Logger principal
        self.logger = logging.getLogger('MTGDeckConstructor')
        self.logger.setLevel(log_level)
        
        # Limpiar handlers existentes
        self.logger.handlers.clear()
        
        # Handler para consola
        if self.settings.get('logging.console_enabled', True):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Handler para archivo
        if self.settings.get('logging.file_enabled', True):
            log_file = Path(self.settings.get('logging.file_path', 'logs/app.log'))
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        self.logger.info(f"Iniciando {self.settings.app_name} v{self.settings.app_version}")
    
    def _initialize_services(self):
        """Inicializa todos los servicios"""
        try:
            # Servicio de cartas
            self.card_service = CardService(
                data_path=self.settings.cards_file
            )
            
            # Servicio de imágenes
            self.image_service = ImageService(
                cache_dir=self.settings.images_directory
            )
            
            # Servicio de Scryfall
            self.scryfall_service = ScryfallService()
            
            # Servicio de mazos
            self.deck_service = DeckService(
                card_service=self.card_service,
                decks_dir=self.settings.decks_directory
            )
            
            self.logger.info("Servicios inicializados correctamente")
            
        except Exception as e:
            self.logger.error(f"Error al inicializar servicios: {e}")
            raise
    
    def _ensure_directories(self):
        """Asegura que existan todos los directorios necesarios"""
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
        """Inicializa la aplicación y carga datos iniciales"""
        try:
            self.logger.info("Inicializando aplicación...")
            
            # Cargar cartas
            cards = self.card_service.load_cards()
            self.logger.info(f"Cargadas {len(cards)} cartas")
            
            # Verificar conectividad con Scryfall (opcional)
            if self.settings.get('api.test_connection', False):
                try:
                    test_card = self.scryfall_service.get_card_by_name("Lightning Bolt")
                    if test_card:
                        self.logger.info("Conexión con Scryfall API verificada")
                except Exception as e:
                    self.logger.warning(f"No se pudo conectar con Scryfall API: {e}")
            
            self.logger.info("Aplicación inicializada correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al inicializar aplicación: {e}")
            return False
    
    def shutdown(self):
        """Cierra la aplicación limpiamente"""
        try:
            self.logger.info("Cerrando aplicación...")
            
            # Guardar configuraciones
            self.settings.save()
            
            # Limpiar caché si es necesario
            if self.settings.get('images.clear_cache_on_exit', False):
                self.image_service.clear_cache()
            
            self.logger.info("Aplicación cerrada correctamente")
            
        except Exception as e:
            self.logger.error(f"Error al cerrar aplicación: {e}")
    
    # Métodos de acceso a servicios
    def get_card_service(self) -> CardService:
        """Obtiene el servicio de cartas"""
        return self.card_service
    
    def get_deck_service(self) -> DeckService:
        """Obtiene el servicio de mazos"""
        return self.deck_service
    
    def get_image_service(self) -> ImageService:
        """Obtiene el servicio de imágenes"""
        return self.image_service
    
    def get_scryfall_service(self) -> ScryfallService:
        """Obtiene el servicio de Scryfall"""
        return self.scryfall_service
    
    def get_settings(self):
        """Obtiene las configuraciones"""
        return self.settings
    
    # Métodos de conveniencia para operaciones comunes
    def search_cards(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Card]:
        """Busca cartas con filtros opcionales"""
        try:
            results = self.card_service.search_cards(query)
            
            if filters:
                # Aplicar filtros adicionales
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
            self.logger.error(f"Error al buscar cartas: {e}")
            return []
    
    def get_card_image(self, card: Card, size: str = 'normal') -> Optional[str]:
        """Obtiene la imagen de una carta"""
        try:
            # Intentar obtener desde caché primero
            image_path = self.image_service.get_image(card.card_name, size)
            
            if image_path and Path(image_path).exists():
                return image_path
            
            # Si no está en caché, intentar descargar desde Scryfall
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
            self.logger.error(f"Error al obtener imagen de carta {card.card_name}: {e}")
            return None
    
    def create_deck_from_list(self, deck_name: str, card_list: List[str], 
                             format: Optional[str] = None) -> Optional[Deck]:
        """Crea un mazo desde una lista de nombres de cartas"""
        try:
            deck = self.deck_service.create_deck(deck_name, format)
            
            for card_entry in card_list:
                # Parsear entrada (ej: "4x Lightning Bolt" o "Lightning Bolt")
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
                
                # Buscar carta
                card = self.card_service.find_card_by_name(card_name)
                
                if card:
                    deck.add_card(card, quantity)
                else:
                    self.logger.warning(f"Carta no encontrada: {card_name}")
            
            return deck
            
        except Exception as e:
            self.logger.error(f"Error al crear mazo desde lista: {e}")
            return None
    
    def get_application_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la aplicación"""
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
            self.logger.error(f"Error al obtener estadísticas: {e}")
            return {}