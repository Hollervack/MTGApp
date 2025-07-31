"""Controlador para gestión de mazos MTG"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..models.deck import Deck
from ..models.card import Card
from ..services.deck_service import DeckService
from ..services.card_service import CardService


class DeckController:
    """Controlador para operaciones con mazos"""
    
    def __init__(self, deck_service: DeckService, card_service: CardService):
        self.deck_service = deck_service
        self.card_service = card_service
        self.logger = logging.getLogger('MTGDeckConstructor.DeckController')
        self.current_deck: Optional[Deck] = None
    
    def create_new_deck(self, name: str, format: Optional[str] = None, 
                       description: Optional[str] = None) -> bool:
        """Crea un nuevo mazo y lo establece como actual"""
        try:
            self.current_deck = self.deck_service.create_deck(name, format, description)
            self.logger.info(f"Nuevo mazo creado: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Error al crear nuevo mazo: {e}")
            return False
    
    def load_deck(self, filename: str) -> bool:
        """Carga un mazo desde archivo"""
        try:
            deck = self.deck_service.load_deck(filename)
            if deck:
                self.current_deck = deck
                self.logger.info(f"Mazo cargado: {deck.name}")
                return True
            else:
                self.logger.warning(f"No se pudo cargar el mazo: {filename}")
                return False
        except Exception as e:
            self.logger.error(f"Error al cargar mazo: {e}")
            return False
    
    def save_current_deck(self) -> bool:
        """Guarda el mazo actual"""
        if not self.current_deck:
            self.logger.warning("No hay mazo actual para guardar")
            return False
        
        try:
            success = self.deck_service.save_deck(self.current_deck)
            if success:
                self.logger.info(f"Mazo guardado: {self.current_deck.name}")
            return success
        except Exception as e:
            self.logger.error(f"Error al guardar mazo: {e}")
            return False
    
    def save_deck_as(self, new_name: str) -> bool:
        """Guarda el mazo actual con un nuevo nombre"""
        if not self.current_deck:
            self.logger.warning("No hay mazo actual para guardar")
            return False
        
        try:
            # Crear una copia del mazo con el nuevo nombre
            old_name = self.current_deck.name
            self.current_deck.name = new_name
            
            success = self.deck_service.save_deck(self.current_deck)
            
            if success:
                self.logger.info(f"Mazo guardado como: {new_name} (antes: {old_name})")
            else:
                # Restaurar el nombre original si falló
                self.current_deck.name = old_name
            
            return success
        except Exception as e:
            self.logger.error(f"Error al guardar mazo como {new_name}: {e}")
            return False
    
    def add_card_to_deck(self, card_name: str, quantity: int = 1) -> bool:
        """Añade una carta al mazo actual"""
        if not self.current_deck:
            self.logger.warning("No hay mazo actual")
            return False
        
        try:
            card = self.card_service.find_card_by_name(card_name)
            if not card:
                self.logger.warning(f"Carta no encontrada: {card_name}")
                return False
            
            self.current_deck.add_card(card, quantity)
            self.logger.info(f"Añadida {quantity}x {card_name} al mazo {self.current_deck.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error al añadir carta al mazo: {e}")
            return False
    
    def remove_card_from_deck(self, card_name: str, quantity: Optional[int] = None) -> bool:
        """Elimina una carta del mazo actual"""
        if not self.current_deck:
            self.logger.warning("No hay mazo actual")
            return False
        
        try:
            card = self.card_service.find_card_by_name(card_name)
            if not card:
                self.logger.warning(f"Carta no encontrada: {card_name}")
                return False
            
            success = self.current_deck.remove_card(card, quantity)
            if success:
                removed_qty = quantity if quantity else "todas las copias de"
                self.logger.info(f"Eliminada {removed_qty} {card_name} del mazo {self.current_deck.name}")
            return success
        except Exception as e:
            self.logger.error(f"Error al eliminar carta del mazo: {e}")
            return False
    
    def update_card_quantity(self, card_name: str, new_quantity: int) -> bool:
        """Actualiza la cantidad de una carta en el mazo"""
        if not self.current_deck:
            self.logger.warning("No hay mazo actual")
            return False
        
        try:
            card = self.card_service.find_card_by_name(card_name)
            if not card:
                self.logger.warning(f"Carta no encontrada: {card_name}")
                return False
            
            # Encontrar la carta en el mazo
            deck_card = self.current_deck.find_card(card.card_name)
            if not deck_card:
                # Si no está en el mazo, añadirla
                if new_quantity > 0:
                    return self.add_card_to_deck(card_name, new_quantity)
                return True
            
            # Actualizar cantidad
            if new_quantity <= 0:
                return self.remove_card_from_deck(card_name)
            else:
                deck_card.quantity = new_quantity
                self.logger.info(f"Actualizada cantidad de {card_name} a {new_quantity} en {self.current_deck.name}")
                return True
        except Exception as e:
            self.logger.error(f"Error al actualizar cantidad de carta: {e}")
            return False
    
    def import_deck_from_file(self, file_path: str, deck_name: str) -> bool:
        """Importa un mazo desde un archivo"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                self.logger.error(f"Archivo no encontrado: {file_path}")
                return False
            
            # Determinar formato por extensión
            if path.suffix.lower() == '.txt':
                deck = self.deck_service.import_deck_from_txt(file_path, deck_name)
            else:
                self.logger.error(f"Formato de archivo no soportado: {path.suffix}")
                return False
            
            if deck:
                self.current_deck = deck
                self.logger.info(f"Mazo importado desde {file_path}: {deck_name}")
                return True
            else:
                self.logger.error(f"Error al importar mazo desde {file_path}")
                return False
        except Exception as e:
            self.logger.error(f"Error al importar mazo: {e}")
            return False
    
    def export_deck_to_file(self, file_path: str) -> bool:
        """Exporta el mazo actual a un archivo"""
        if not self.current_deck:
            self.logger.warning("No hay mazo actual para exportar")
            return False
        
        try:
            path = Path(file_path)
            
            # Determinar formato por extensión
            if path.suffix.lower() == '.txt':
                success = self.deck_service.export_deck_to_txt(self.current_deck, file_path)
            else:
                self.logger.error(f"Formato de exportación no soportado: {path.suffix}")
                return False
            
            if success:
                self.logger.info(f"Mazo exportado a {file_path}")
            return success
        except Exception as e:
            self.logger.error(f"Error al exportar mazo: {e}")
            return False
    
    def get_deck_analysis(self) -> Optional[Dict[str, Any]]:
        """Obtiene análisis del mazo actual"""
        if not self.current_deck:
            return None
        
        try:
            return self.deck_service.analyze_deck(self.current_deck)
        except Exception as e:
            self.logger.error(f"Error al analizar mazo: {e}")
            return None
    
    def compare_with_collection(self) -> Optional[Dict[str, Any]]:
        """Compara el mazo actual con la colección"""
        if not self.current_deck:
            return None
        
        try:
            return self.deck_service.compare_with_collection(self.current_deck)
        except Exception as e:
            self.logger.error(f"Error al comparar con colección: {e}")
            return None
    
    def get_available_decks(self) -> List[Dict[str, Any]]:
        """Obtiene lista de mazos disponibles"""
        try:
            return self.deck_service.list_decks()
        except Exception as e:
            self.logger.error(f"Error al listar mazos: {e}")
            return []
    
    def delete_deck(self, filename: str) -> bool:
        """Elimina un mazo"""
        try:
            success = self.deck_service.delete_deck(filename)
            if success:
                self.logger.info(f"Mazo eliminado: {filename}")
                
                # Si el mazo eliminado es el actual, limpiar referencia
                if (self.current_deck and 
                    self.deck_service._safe_filename(self.current_deck.name) + '.json' == filename):
                    self.current_deck = None
            
            return success
        except Exception as e:
            self.logger.error(f"Error al eliminar mazo: {e}")
            return False
    
    def clear_current_deck(self):
        """Limpia el mazo actual"""
        if self.current_deck:
            self.logger.info(f"Limpiando mazo actual: {self.current_deck.name}")
        self.current_deck = None
    
    def get_current_deck(self) -> Optional[Deck]:
        """Obtiene el mazo actual"""
        return self.current_deck
    
    def has_current_deck(self) -> bool:
        """Verifica si hay un mazo actual"""
        return self.current_deck is not None
    
    def get_deck_summary(self) -> Optional[Dict[str, Any]]:
        """Obtiene resumen del mazo actual"""
        if not self.current_deck:
            return None
        
        try:
            return {
                'name': self.current_deck.name,
                'format': self.current_deck.format,
                'description': self.current_deck.description,
                'total_cards': self.current_deck.total_cards,
                'unique_cards': self.current_deck.unique_cards,
                'colors': list(self.current_deck.color_distribution.keys()),
                'types': list(self.current_deck.type_distribution.keys()),
                'is_legal': self.current_deck.is_format_legal() if self.current_deck.format else None
            }
        except Exception as e:
            self.logger.error(f"Error al obtener resumen del mazo: {e}")
            return None
    
    def validate_deck_format(self) -> Dict[str, Any]:
        """Valida el mazo actual según su formato"""
        if not self.current_deck:
            return {'valid': False, 'errors': ['No hay mazo actual']}
        
        try:
            errors = []
            warnings = []
            
            # Validaciones básicas
            if not self.current_deck.name.strip():
                errors.append("El mazo debe tener un nombre")
            
            if self.current_deck.total_cards == 0:
                errors.append("El mazo no puede estar vacío")
            
            # Validaciones específicas por formato
            if self.current_deck.format:
                format_lower = self.current_deck.format.lower()
                
                if format_lower == 'standard':
                    if self.current_deck.total_cards < 60:
                        errors.append("Standard requiere mínimo 60 cartas")
                    elif self.current_deck.total_cards > 60:
                        warnings.append("Standard típicamente usa exactamente 60 cartas")
                
                elif format_lower == 'commander' or format_lower == 'edh':
                    if self.current_deck.total_cards != 100:
                        errors.append("Commander requiere exactamente 100 cartas")
                    
                    # Verificar que no hay más de 1 copia de cada carta (excepto tierras básicas)
                    for card in self.current_deck.cards:
                        if (card.quantity > 1 and 
                            not (card.type_line and 'Basic' in card.type_line and 'Land' in card.type_line)):
                            errors.append(f"Commander permite máximo 1 copia de {card.card_name}")
                
                elif format_lower == 'modern':
                    if self.current_deck.total_cards < 60:
                        errors.append("Modern requiere mínimo 60 cartas")
                    
                    # Verificar límite de 4 copias
                    for card in self.current_deck.cards:
                        if (card.quantity > 4 and 
                            not (card.type_line and 'Basic' in card.type_line and 'Land' in card.type_line)):
                            errors.append(f"Modern permite máximo 4 copias de {card.card_name}")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
        except Exception as e:
            self.logger.error(f"Error al validar formato del mazo: {e}")
            return {'valid': False, 'errors': [f'Error de validación: {e}']}