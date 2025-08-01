"""Data model for MTG decks"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import Counter

from .card import Card


@dataclass
class Deck:
    """Represents a Magic: The Gathering deck"""
    
    name: str
    cards: List[Card] = field(default_factory=list)
    format: Optional[str] = None
    description: Optional[str] = None
    
    def add_card(self, card: Card, quantity: int = 1) -> None:
        """Adds a card to the deck"""
        existing_card = self.find_card(card.card_name)
        if existing_card:
            existing_card.quantity += quantity
        else:
            new_card = Card.from_dict(card.to_dict())
            new_card.quantity = quantity
            self.cards.append(new_card)
    
    def remove_card(self, card_name: str, quantity: int = 1) -> bool:
        """Removes a specific quantity of a card from the deck"""
        card = self.find_card(card_name)
        if card and card.quantity >= quantity:
            card.quantity -= quantity
            if card.quantity == 0:
                self.cards.remove(card)
            return True
        return False
    
    def find_card(self, card_name: str) -> Optional[Card]:
        """Searches for a card in the deck by name"""
        for card in self.cards:
            if card.card_name == card_name or card.english_card_name == card_name:
                return card
        return None
    
    @property
    def total_cards(self) -> int:
        """Total number of cards in the deck"""
        return sum(card.quantity for card in self.cards)
    
    @property
    def unique_cards(self) -> int:
        """Number of unique cards in the deck"""
        return len(self.cards)
    
    @property
    def color_distribution(self) -> Dict[str, int]:
        """Color distribution in the deck"""
        color_count = Counter()
        for card in self.cards:
            for color in card.color_identity:
                color_count[color] += card.quantity
        return dict(color_count)
    
    @property
    def mana_curve(self) -> Dict[int, int]:
        """Mana curve of the deck"""
        curve = Counter()
        for card in self.cards:
            cmc = card.converted_mana_cost
            curve[cmc] += card.quantity
        return dict(curve)
    
    @property
    def type_distribution(self) -> Dict[str, int]:
        """Card type distribution"""
        type_count = Counter()
        for card in self.cards:
            if card.type_line:
                # Simplified - extract main type
                main_type = card.type_line.split(' — ')[0].split(' ')[-1]
                type_count[main_type] += card.quantity
        return dict(type_count)
    
    def get_cards_by_type(self, card_type: str) -> List[Card]:
        """Gets all cards of a specific type"""
        return [card for card in self.cards 
                if card.type_line and card_type.lower() in card.type_line.lower()]
    
    def is_legal_format(self, format_name: str) -> bool:
        """Checks if the deck is legal in a specific format (simplified)"""
        # Basic implementation - in a real project it would be more complex
        format_rules = {
            'commander': {'min_cards': 100, 'max_cards': 100},
            'standard': {'min_cards': 60, 'max_cards': None},
            'modern': {'min_cards': 60, 'max_cards': None}
        }
        
        if format_name.lower() not in format_rules:
            return False
        
        rules = format_rules[format_name.lower()]
        total = self.total_cards
        
        if total < rules['min_cards']:
            return False
        if rules['max_cards'] and total > rules['max_cards']:
            return False
        
        return True
    
    def to_dict(self) -> dict:
        """Converts the deck to dictionary for serialization"""
        return {
            'name': self.name,
            'format': self.format,
            'description': self.description,
            'cards': [card.to_dict() for card in self.cards]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Deck':
        """Creates a deck from a dictionary"""
        deck = cls(
            name=data.get('name', ''),
            format=data.get('format'),
            description=data.get('description')
        )
        
        for card_data in data.get('cards', []):
            card = Card.from_dict(card_data)
            deck.cards.append(card)
        
        return deck