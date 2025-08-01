"""Service for MTG card management"""

import csv
from typing import List, Optional, Dict
from pathlib import Path

from ..models.card import Card


class CardService:
    """Service for MTG card operations"""
    
    def __init__(self, data_path: str = 'data/databaseMTG.csv'):
        self.data_path = Path(data_path)
        self._cards_cache: Optional[List[Card]] = None
        self._cards_by_name: Optional[Dict[str, Card]] = None
    
    def load_cards(self, force_reload: bool = False) -> List[Card]:
        """Loads all cards from the CSV file"""
        if self._cards_cache is None or force_reload:
            self._cards_cache = self._load_cards_from_file()
            self._build_name_index()
        return self._cards_cache
    
    def _load_cards_from_file(self) -> List[Card]:
        """Loads cards from the CSV file"""
        cards = []
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        try:
            with open(self.data_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    try:
                        card = Card.from_dict(row)
                        cards.append(card)
                    except Exception as e:
                        print(f"Error processing card: {row.get('card_name', 'Unknown')} - {e}")
                        continue
        except Exception as e:
            raise Exception(f"Error reading cards file: {e}")
        
        return cards
    
    def _build_name_index(self) -> None:
        """Builds a card index by name for fast searches"""
        if self._cards_cache is None:
            return
        
        self._cards_by_name = {}
        for card in self._cards_cache:
            # Index by main name
            if card.card_name:
                self._cards_by_name[card.card_name.lower()] = card
            
            # Index by English name if it exists
            if card.english_card_name:
                self._cards_by_name[card.english_card_name.lower()] = card
    
    def find_card_by_name(self, name: str) -> Optional[Card]:
        """Searches for a card by name (case insensitive)"""
        if self._cards_by_name is None:
            self.load_cards()
        
        return self._cards_by_name.get(name.lower())
    
    def search_cards(self, query: str, limit: int = 50) -> List[Card]:
        """Searches for cards that match the query"""
        cards = self.load_cards()
        query_lower = query.lower()
        
        results = []
        for card in cards:
            if (query_lower in card.card_name.lower() or 
                (card.english_card_name and query_lower in card.english_card_name.lower())):
                results.append(card)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_cards_by_color(self, colors: List[str]) -> List[Card]:
        """Gets cards that contain the specified colors"""
        cards = self.load_cards()
        
        return [card for card in cards 
                if any(color in card.color_identity for color in colors)]
    
    def get_cards_by_type(self, card_type: str) -> List[Card]:
        """Gets cards of a specific type"""
        cards = self.load_cards()
        
        return [card for card in cards 
                if card.type_line and card_type.lower() in card.type_line.lower()]
    
    def get_cards_by_rarity(self, rarity: str) -> List[Card]:
        """Gets cards of a specific rarity"""
        cards = self.load_cards()
        
        return [card for card in cards 
                if card.rarity and card.rarity.lower() == rarity.lower()]
    
    def get_cards_by_set(self, set_code: str) -> List[Card]:
        """Gets cards of a specific set"""
        cards = self.load_cards()
        
        return [card for card in cards 
                if card.set_code and card.set_code.lower() == set_code.lower()]
    
    def get_available_sets(self) -> List[str]:
        """Gets list of available sets"""
        cards = self.load_cards()
        sets = set()
        
        for card in cards:
            if card.set_code:
                sets.add(card.set_code)
        
        return sorted(list(sets))
    
    def get_available_types(self) -> List[str]:
        """Gets list of available card types"""
        cards = self.load_cards()
        types = set()
        
        for card in cards:
            if card.type_line:
                # Extract main types
                main_types = card.type_line.split(' — ')[0].split(' ')
                for card_type in main_types:
                    if card_type and card_type not in ['Legendary', 'Basic', 'Snow']:
                        types.add(card_type)
        
        return sorted(list(types))
    
    def get_statistics(self) -> Dict[str, any]:
        """Gets collection statistics"""
        cards = self.load_cards()
        
        total_cards = len(cards)
        total_quantity = sum(card.quantity for card in cards)
        
        colors = {}
        rarities = {}
        types = {}
        
        for card in cards:
            # Count colors
            for color in card.color_identity:
                colors[color] = colors.get(color, 0) + card.quantity
            
            # Count rarities
            if card.rarity:
                rarities[card.rarity] = rarities.get(card.rarity, 0) + card.quantity
            
            # Count types
            if card.type_line:
                main_type = card.type_line.split(' — ')[0].split(' ')[-1]
                types[main_type] = types.get(main_type, 0) + card.quantity
        
        return {
            'total_unique_cards': total_cards,
            'total_quantity': total_quantity,
            'color_distribution': colors,
            'rarity_distribution': rarities,
            'type_distribution': types
        }