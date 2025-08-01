"""Service for MTG deck management"""

import csv
import json
from typing import List, Dict, Optional, Any
from pathlib import Path

from ..models.deck import Deck
from ..models.card import Card
from .card_service import CardService


class DeckService:
    """Service for MTG deck operations"""
    
    def __init__(self, card_service: CardService, decks_dir: str = 'data/decks'):
        self.card_service = card_service
        self.decks_dir = Path(decks_dir)
        self.decks_dir.mkdir(parents=True, exist_ok=True)
    
    def create_deck(self, name: str, format: Optional[str] = None, description: Optional[str] = None) -> Deck:
        """Creates a new deck"""
        return Deck(name=name, format=format, description=description)
    
    def save_deck(self, deck: Deck) -> bool:
        """Saves a deck to disk"""
        try:
            # Create safe filename
            filename = self._safe_filename(deck.name) + '.json'
            file_path = self.decks_dir / filename
            
            # Convert to dictionary and save as JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(deck.to_dict(), f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving deck: {e}")
            return False
    
    def load_deck(self, filename: str) -> Optional[Deck]:
        """Loads a deck from disk"""
        try:
            file_path = self.decks_dir / filename
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                deck_data = json.load(f)
            
            return Deck.from_dict(deck_data)
        except Exception as e:
            print(f"Error loading deck: {e}")
            return None
    
    def list_decks(self) -> List[Dict[str, Any]]:
        """Lists all available decks"""
        decks = []
        
        try:
            for file_path in self.decks_dir.glob('*.json'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        deck_data = json.load(f)
                    
                    decks.append({
                        'name': deck_data.get('name', 'Unnamed'),
                        'format': deck_data.get('format'),
                        'card_count': len(deck_data.get('cards', [])),
                        'filename': file_path.name
                    })
                except Exception as e:
                    print(f"Error reading deck {file_path.name}: {e}")
                    continue
        except Exception as e:
            print(f"Error listing decks: {e}")
        
        return decks
    
    def delete_deck(self, filename: str) -> bool:
        """Deletes a deck from disk"""
        try:
            file_path = self.decks_dir / filename
            
            if file_path.exists():
                file_path.unlink()
                return True
            
            return False
        except Exception as e:
            print(f"Error deleting deck: {e}")
            return False
    
    def import_deck_from_txt(self, file_path: str, deck_name: str) -> Optional[Deck]:
        """Imports a deck from a text file (common format)"""
        try:
            deck = self.create_deck(deck_name)
            path = Path(file_path)
            
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('//'):
                    continue
                
                # Typical format: "2x Card Name" or "2 Card Name"
                parts = line.split(' ', 1)
                if len(parts) < 2:
                    continue
                
                quantity_str = parts[0].rstrip('x')
                card_name = parts[1].strip()
                
                try:
                    quantity = int(quantity_str)
                except ValueError:
                    continue
                
                # Search for the card in the collection
                card = self.card_service.find_card_by_name(card_name)
                
                if card:
                    deck.add_card(card, quantity)
            
            return deck
        except Exception as e:
            print(f"Error importing deck from TXT: {e}")
            return None
    
    def export_deck_to_txt(self, deck: Deck, file_path: str) -> bool:
        """Exports a deck to a text file (common format)"""
        try:
            path = Path(file_path)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"// {deck.name}\n")
                if deck.description:
                    f.write(f"// {deck.description}\n")
                f.write(f"// Format: {deck.format or 'Not specified'}\n\n")
                
                # Group by types
                creatures = deck.get_cards_by_type('Creature')
                instants = deck.get_cards_by_type('Instant')
                sorceries = deck.get_cards_by_type('Sorcery')
                enchantments = deck.get_cards_by_type('Enchantment')
                artifacts = deck.get_cards_by_type('Artifact')
                planeswalkers = deck.get_cards_by_type('Planeswalker')
                lands = deck.get_cards_by_type('Land')
                other = [card for card in deck.cards if not any(card in group for group in 
                         [creatures, instants, sorceries, enchantments, artifacts, planeswalkers, lands])]
                
                # Write by sections
                if creatures:
                    f.write("// Creatures\n")
                    for card in sorted(creatures, key=lambda c: c.card_name):
                        f.write(f"{card.quantity}x {card.card_name}\n")
                    f.write("\n")
                
                if instants:
                    f.write("// Instants\n")
                    for card in sorted(instants, key=lambda c: c.card_name):
                        f.write(f"{card.quantity}x {card.card_name}\n")
                    f.write("\n")
                
                if sorceries:
                    f.write("// Sorceries\n")
                    for card in sorted(sorceries, key=lambda c: c.card_name):
                        f.write(f"{card.quantity}x {card.card_name}\n")
                    f.write("\n")
                
                if enchantments:
                    f.write("// Enchantments\n")
                    for card in sorted(enchantments, key=lambda c: c.card_name):
                        f.write(f"{card.quantity}x {card.card_name}\n")
                    f.write("\n")
                
                if artifacts:
                    f.write("// Artifacts\n")
                    for card in sorted(artifacts, key=lambda c: c.card_name):
                        f.write(f"{card.quantity}x {card.card_name}\n")
                    f.write("\n")
                
                if planeswalkers:
                    f.write("// Planeswalkers\n")
                    for card in sorted(planeswalkers, key=lambda c: c.card_name):
                        f.write(f"{card.quantity}x {card.card_name}\n")
                    f.write("\n")
                
                if lands:
                    f.write("// Lands\n")
                    for card in sorted(lands, key=lambda c: c.card_name):
                        f.write(f"{card.quantity}x {card.card_name}\n")
                    f.write("\n")
                
                if other:
                    f.write("// Others\n")
                    for card in sorted(other, key=lambda c: c.card_name):
                        f.write(f"{card.quantity}x {card.card_name}\n")
            
            return True
        except Exception as e:
            print(f"Error exporting deck to TXT: {e}")
            return False
    
    def import_deck_from_edhrec(self, url: str, deck_name: str) -> Optional[Deck]:
        """Imports a deck from EDHREC (simplified)"""
        # Simplified implementation - in a real project web scraping would be used
        # or an API if available
        print(f"EDHREC import not fully implemented: {url}")
        
        # Create an empty deck as example
        deck = self.create_deck(deck_name, format="Commander")
        return deck
    
    def compare_with_collection(self, deck: Deck) -> Dict[str, Any]:
        """Compares a deck with the user's collection"""
        collection_cards = self.card_service.load_cards()
        collection_by_name = {card.card_name.lower(): card for card in collection_cards if card.card_name}
        
        missing_cards = []
        available_cards = []
        partial_cards = []
        
        for deck_card in deck.cards:
            collection_card = collection_by_name.get(deck_card.card_name.lower())
            
            if not collection_card or collection_card.quantity == 0:
                missing_cards.append({
                    'card': deck_card,
                    'needed': deck_card.quantity,
                    'available': 0
                })
            elif collection_card.quantity >= deck_card.quantity:
                available_cards.append({
                    'card': deck_card,
                    'needed': deck_card.quantity,
                    'available': collection_card.quantity
                })
            else:
                partial_cards.append({
                    'card': deck_card,
                    'needed': deck_card.quantity,
                    'available': collection_card.quantity,
                    'missing': deck_card.quantity - collection_card.quantity
                })
        
        return {
            'missing_cards': missing_cards,
            'available_cards': available_cards,
            'partial_cards': partial_cards,
            'total_cards_needed': sum(card.quantity for card in deck.cards),
            'total_cards_available': sum(item['available'] for item in available_cards) + 
                                    sum(item['available'] for item in partial_cards),
            'total_cards_missing': sum(item['needed'] for item in missing_cards) + 
                                  sum(item['missing'] for item in partial_cards),
            'completion_percentage': round(
                (sum(item['available'] for item in available_cards) + 
                 sum(item['available'] for item in partial_cards)) / 
                sum(card.quantity for card in deck.cards) * 100 
                if sum(card.quantity for card in deck.cards) > 0 else 0, 2
            )
        }
    
    def analyze_deck(self, deck: Deck) -> Dict[str, Any]:
        """Analyzes a deck and provides statistics"""
        return {
            'name': deck.name,
            'format': deck.format,
            'total_cards': deck.total_cards,
            'unique_cards': deck.unique_cards,
            'color_distribution': deck.color_distribution,
            'mana_curve': deck.mana_curve,
            'type_distribution': deck.type_distribution,
            'creatures': len(deck.get_cards_by_type('Creature')),
            'instants': len(deck.get_cards_by_type('Instant')),
            'sorceries': len(deck.get_cards_by_type('Sorcery')),
            'enchantments': len(deck.get_cards_by_type('Enchantment')),
            'artifacts': len(deck.get_cards_by_type('Artifact')),
            'planeswalkers': len(deck.get_cards_by_type('Planeswalker')),
            'lands': len(deck.get_cards_by_type('Land'))
        }
    
    def _safe_filename(self, name: str) -> str:
        """Converts a name to a safe filename"""
        # Replace unsafe characters
        safe_name = ""
        for char in name:
            if char.isalnum() or char in "_- ":
                safe_name += char
            else:
                safe_name += "_"
        
        # Remove leading and trailing spaces and replace multiple spaces
        safe_name = safe_name.strip().replace("  ", " ")
        
        # Replace spaces with hyphens
        safe_name = safe_name.replace(" ", "-")
        
        return safe_name