"""Controller for MTG deck management"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..models.deck import Deck
from ..models.card import Card
from ..services.deck_service import DeckService
from ..services.card_service import CardService


class DeckController:
    """Controller for deck operations"""
    
    def __init__(self, deck_service: DeckService, card_service: CardService):
        self.deck_service = deck_service
        self.card_service = card_service
        self.logger = logging.getLogger('MTGDeckConstructor.DeckController')
        self.current_deck: Optional[Deck] = None
    
    def create_new_deck(self, name: str, format: Optional[str] = None, 
                       description: Optional[str] = None) -> bool:
        """Creates a new deck and sets it as current"""
        try:
            self.current_deck = self.deck_service.create_deck(name, format, description)
            self.logger.info(f"New deck created: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating new deck: {e}")
            return False
    
    def load_deck(self, filename: str) -> bool:
        """Loads a deck from file"""
        try:
            deck = self.deck_service.load_deck(filename)
            if deck:
                self.current_deck = deck
                self.logger.info(f"Deck loaded: {deck.name}")
                return True
            else:
                self.logger.warning(f"Could not load deck: {filename}")
                return False
        except Exception as e:
            self.logger.error(f"Error loading deck: {e}")
            return False
    
    def save_current_deck(self) -> bool:
        """Saves the current deck"""
        if not self.current_deck:
            self.logger.warning("No current deck to save")
            return False
        
        try:
            success = self.deck_service.save_deck(self.current_deck)
            if success:
                self.logger.info(f"Deck saved: {self.current_deck.name}")
            return success
        except Exception as e:
            self.logger.error(f"Error saving deck: {e}")
            return False
    
    def save_deck_as(self, new_name: str) -> bool:
        """Saves the current deck with a new name"""
        if not self.current_deck:
            self.logger.warning("No current deck to save")
            return False
        
        try:
            # Create a copy of the deck with the new name
            old_name = self.current_deck.name
            self.current_deck.name = new_name
            
            success = self.deck_service.save_deck(self.current_deck)
            
            if success:
                self.logger.info(f"Deck saved as: {new_name} (previously: {old_name})")
            else:
                # Restore original name if failed
                self.current_deck.name = old_name
            
            return success
        except Exception as e:
            self.logger.error(f"Error saving deck as {new_name}: {e}")
            return False
    
    def add_card_to_deck(self, card_name: str, quantity: int = 1) -> bool:
        """Adds a card to the current deck"""
        if not self.current_deck:
            self.logger.warning("No current deck")
            return False
        
        try:
            card = self.card_service.find_card_by_name(card_name)
            if not card:
                self.logger.warning(f"Card not found: {card_name}")
                return False
            
            self.current_deck.add_card(card, quantity)
            self.logger.info(f"Added {quantity}x {card_name} to deck {self.current_deck.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding card to deck: {e}")
            return False
    
    def remove_card_from_deck(self, card_name: str, quantity: Optional[int] = None) -> bool:
        """Removes a card from the current deck"""
        if not self.current_deck:
            self.logger.warning("No current deck")
            return False
        
        try:
            card = self.card_service.find_card_by_name(card_name)
            if not card:
                self.logger.warning(f"Card not found: {card_name}")
                return False
            
            success = self.current_deck.remove_card(card, quantity)
            if success:
                removed_qty = quantity if quantity else "all copies of"
                self.logger.info(f"Removed {removed_qty} {card_name} from deck {self.current_deck.name}")
            return success
        except Exception as e:
            self.logger.error(f"Error removing card from deck: {e}")
            return False
    
    def update_card_quantity(self, card_name: str, new_quantity: int) -> bool:
        """Updates the quantity of a card in the deck"""
        if not self.current_deck:
            self.logger.warning("No current deck")
            return False
        
        try:
            card = self.card_service.find_card_by_name(card_name)
            if not card:
                self.logger.warning(f"Card not found: {card_name}")
                return False
            
            # Find the card in the deck
            deck_card = self.current_deck.find_card(card.card_name)
            if not deck_card:
                # If not in deck, add it
                if new_quantity > 0:
                    return self.add_card_to_deck(card_name, new_quantity)
                return True
            
            # Update quantity
            if new_quantity <= 0:
                return self.remove_card_from_deck(card_name)
            else:
                deck_card.quantity = new_quantity
                self.logger.info(f"Updated quantity of {card_name} to {new_quantity} in {self.current_deck.name}")
                return True
        except Exception as e:
            self.logger.error(f"Error updating card quantity: {e}")
            return False
    
    def import_deck_from_file(self, file_path: str, deck_name: str) -> bool:
        """Imports a deck from a file"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                self.logger.error(f"File not found: {file_path}")
                return False
            
            # Determine format by extension
            if path.suffix.lower() == '.txt':
                deck = self.deck_service.import_deck_from_txt(file_path, deck_name)
            else:
                self.logger.error(f"Unsupported file format: {path.suffix}")
                return False
            
            if deck:
                self.current_deck = deck
                self.logger.info(f"Deck imported from {file_path}: {deck_name}")
                return True
            else:
                self.logger.error(f"Error importing deck from {file_path}")
                return False
        except Exception as e:
            self.logger.error(f"Error importing deck: {e}")
            return False
    
    def export_deck_to_file(self, file_path: str) -> bool:
        """Exports the current deck to a file"""
        if not self.current_deck:
            self.logger.warning("No current deck to export")
            return False
        
        try:
            path = Path(file_path)
            
            # Determine format by extension
            if path.suffix.lower() == '.txt':
                success = self.deck_service.export_deck_to_txt(self.current_deck, file_path)
            else:
                self.logger.error(f"Unsupported export format: {path.suffix}")
                return False
            
            if success:
                self.logger.info(f"Deck exported to {file_path}")
            return success
        except Exception as e:
            self.logger.error(f"Error exporting deck: {e}")
            return False
    
    def get_deck_analysis(self) -> Optional[Dict[str, Any]]:
        """Gets analysis of the current deck"""
        if not self.current_deck:
            return None
        
        try:
            return self.deck_service.analyze_deck(self.current_deck)
        except Exception as e:
            self.logger.error(f"Error analyzing deck: {e}")
            return None
    
    def compare_with_collection(self) -> Optional[Dict[str, Any]]:
        """Compares the current deck with the collection"""
        if not self.current_deck:
            return None
        
        try:
            return self.deck_service.compare_with_collection(self.current_deck)
        except Exception as e:
            self.logger.error(f"Error comparing with collection: {e}")
            return None
    
    def get_available_decks(self) -> List[Dict[str, Any]]:
        """Gets list of available decks"""
        try:
            return self.deck_service.list_decks()
        except Exception as e:
            self.logger.error(f"Error listing decks: {e}")
            return []
    
    def delete_deck(self, filename: str) -> bool:
        """Deletes a deck"""
        try:
            success = self.deck_service.delete_deck(filename)
            if success:
                self.logger.info(f"Deck deleted: {filename}")
                
                # If deleted deck is current, clear reference
                if (self.current_deck and 
                    self.deck_service._safe_filename(self.current_deck.name) + '.json' == filename):
                    self.current_deck = None
            
            return success
        except Exception as e:
            self.logger.error(f"Error deleting deck: {e}")
            return False
    
    def clear_current_deck(self):
        """Clears the current deck"""
        if self.current_deck:
            self.logger.info(f"Clearing current deck: {self.current_deck.name}")
        self.current_deck = None
    
    def get_current_deck(self) -> Optional[Deck]:
        """Gets the current deck"""
        return self.current_deck
    
    def has_current_deck(self) -> bool:
        """Checks if there is a current deck"""
        return self.current_deck is not None
    
    def get_deck_summary(self) -> Optional[Dict[str, Any]]:
        """Gets summary of the current deck"""
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
            self.logger.error(f"Error getting deck summary: {e}")
            return None
    
    def validate_deck_format(self) -> Dict[str, Any]:
        """Validates the current deck according to its format"""
        if not self.current_deck:
            return {'valid': False, 'errors': ['No current deck']}
        
        try:
            errors = []
            warnings = []
            
            # Basic validations
            if not self.current_deck.name.strip():
                errors.append("Deck must have a name")
            
            if self.current_deck.total_cards == 0:
                errors.append("Deck cannot be empty")
            
            # Format-specific validations
            if self.current_deck.format:
                format_lower = self.current_deck.format.lower()
                
                if format_lower == 'standard':
                    if self.current_deck.total_cards < 60:
                        errors.append("Standard requires minimum 60 cards")
                    elif self.current_deck.total_cards > 60:
                        warnings.append("Standard typically uses exactly 60 cards")
                
                elif format_lower == 'commander' or format_lower == 'edh':
                    if self.current_deck.total_cards != 100:
                        errors.append("Commander requires exactly 100 cards")
                    
                    # Verify no more than 1 copy of each card (except basic lands)
                    for card in self.current_deck.cards:
                        if (card.quantity > 1 and 
                            not (card.type_line and 'Basic' in card.type_line and 'Land' in card.type_line)):
                            errors.append(f"Commander allows maximum 1 copy of {card.card_name}")
                
                elif format_lower == 'modern':
                    if self.current_deck.total_cards < 60:
                        errors.append("Modern requires minimum 60 cards")
                    
                    # Verify 4-copy limit
                    for card in self.current_deck.cards:
                        if (card.quantity > 4 and 
                            not (card.type_line and 'Basic' in card.type_line and 'Land' in card.type_line)):
                            errors.append(f"Modern allows maximum 4 copies of {card.card_name}")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
        except Exception as e:
            self.logger.error(f"Error validating deck format: {e}")
            return {'valid': False, 'errors': [f'Validation error: {e}']}