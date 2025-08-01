"""Data model for MTG cards"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Card:
    """Represents a Magic: The Gathering card"""
    
    card_name: str
    english_card_name: Optional[str] = None
    quantity: int = 0
    scryfall_uuid: Optional[str] = None
    mana_cost: Optional[str] = None
    type_line: Optional[str] = None
    oracle_text: Optional[str] = None
    power: Optional[str] = None
    toughness: Optional[str] = None
    colors: Optional[List[str]] = None
    color_identity: Optional[List[str]] = None
    rarity: Optional[str] = None
    set_code: Optional[str] = None
    collector_number: Optional[str] = None
    image_url: Optional[str] = None
    
    def __post_init__(self):
        """Validation and data normalization after initialization"""
        if self.colors is None:
            self.colors = []
        if self.color_identity is None:
            self.color_identity = []
    
    @property
    def display_name(self) -> str:
        """Name to display in the interface"""
        return self.english_card_name or self.card_name
    
    @property
    def is_creature(self) -> bool:
        """Checks if the card is a creature"""
        return self.type_line and 'Creature' in self.type_line
    
    @property
    def converted_mana_cost(self) -> int:
        """Calculates the converted mana cost (simplified)"""
        if not self.mana_cost:
            return 0
        # Simplified implementation - in a real project it would be more complex
        import re
        numbers = re.findall(r'\d+', self.mana_cost)
        return sum(int(n) for n in numbers) + len(re.findall(r'[WUBRG]', self.mana_cost))
    
    def to_dict(self) -> dict:
        """Converts the card to dictionary for serialization"""
        return {
            'card_name': self.card_name,
            'english_card_name': self.english_card_name,
            'quantity': self.quantity,
            'scryfall_uuid': self.scryfall_uuid,
            'mana_cost': self.mana_cost,
            'type_line': self.type_line,
            'oracle_text': self.oracle_text,
            'power': self.power,
            'toughness': self.toughness,
            'colors': self.colors,
            'color_identity': self.color_identity,
            'rarity': self.rarity,
            'set_code': self.set_code,
            'collector_number': self.collector_number,
            'image_url': self.image_url
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Card':
        """Creates a card from a dictionary"""
        return cls(
            card_name=data.get('card_name', ''),
            english_card_name=data.get('english_card_name'),
            quantity=int(data.get('quantity', 0)),
            scryfall_uuid=data.get('scryfall_uuid'),
            mana_cost=data.get('mana_cost'),
            type_line=data.get('type_line'),
            oracle_text=data.get('oracle_text'),
            power=data.get('power'),
            toughness=data.get('toughness'),
            colors=data.get('colors', []),
            color_identity=data.get('color_identity', []),
            rarity=data.get('rarity'),
            set_code=data.get('set_code'),
            collector_number=data.get('collector_number'),
            image_url=data.get('image_url')
        )