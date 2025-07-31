"""Servicio para gestión de cartas MTG"""

import csv
from typing import List, Optional, Dict
from pathlib import Path

from ..models.card import Card


class CardService:
    """Servicio para operaciones con cartas MTG"""
    
    def __init__(self, data_path: str = 'data/databaseMTG.csv'):
        self.data_path = Path(data_path)
        self._cards_cache: Optional[List[Card]] = None
        self._cards_by_name: Optional[Dict[str, Card]] = None
    
    def load_cards(self, force_reload: bool = False) -> List[Card]:
        """Carga todas las cartas desde el archivo CSV"""
        if self._cards_cache is None or force_reload:
            self._cards_cache = self._load_cards_from_file()
            self._build_name_index()
        return self._cards_cache
    
    def _load_cards_from_file(self) -> List[Card]:
        """Carga cartas desde el archivo CSV"""
        cards = []
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo de datos: {self.data_path}")
        
        try:
            with open(self.data_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    try:
                        card = Card.from_dict(row)
                        cards.append(card)
                    except Exception as e:
                        print(f"Error al procesar carta: {row.get('card_name', 'Desconocida')} - {e}")
                        continue
        except Exception as e:
            raise Exception(f"Error al leer el archivo de cartas: {e}")
        
        return cards
    
    def _build_name_index(self) -> None:
        """Construye un índice de cartas por nombre para búsquedas rápidas"""
        if self._cards_cache is None:
            return
        
        self._cards_by_name = {}
        for card in self._cards_cache:
            # Indexar por nombre principal
            if card.card_name:
                self._cards_by_name[card.card_name.lower()] = card
            
            # Indexar por nombre en inglés si existe
            if card.english_card_name:
                self._cards_by_name[card.english_card_name.lower()] = card
    
    def find_card_by_name(self, name: str) -> Optional[Card]:
        """Busca una carta por nombre (insensible a mayúsculas)"""
        if self._cards_by_name is None:
            self.load_cards()
        
        return self._cards_by_name.get(name.lower())
    
    def search_cards(self, query: str, limit: int = 50) -> List[Card]:
        """Busca cartas que coincidan con la consulta"""
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
        """Obtiene cartas que contengan los colores especificados"""
        cards = self.load_cards()
        
        return [card for card in cards 
                if any(color in card.color_identity for color in colors)]
    
    def get_cards_by_type(self, card_type: str) -> List[Card]:
        """Obtiene cartas de un tipo específico"""
        cards = self.load_cards()
        
        return [card for card in cards 
                if card.type_line and card_type.lower() in card.type_line.lower()]
    
    def get_cards_by_rarity(self, rarity: str) -> List[Card]:
        """Obtiene cartas de una rareza específica"""
        cards = self.load_cards()
        
        return [card for card in cards 
                if card.rarity and card.rarity.lower() == rarity.lower()]
    
    def get_cards_by_set(self, set_code: str) -> List[Card]:
        """Obtiene cartas de un set específico"""
        cards = self.load_cards()
        
        return [card for card in cards 
                if card.set_code and card.set_code.lower() == set_code.lower()]
    
    def get_available_sets(self) -> List[str]:
        """Obtiene lista de sets disponibles"""
        cards = self.load_cards()
        sets = set()
        
        for card in cards:
            if card.set_code:
                sets.add(card.set_code)
        
        return sorted(list(sets))
    
    def get_available_types(self) -> List[str]:
        """Obtiene lista de tipos de carta disponibles"""
        cards = self.load_cards()
        types = set()
        
        for card in cards:
            if card.type_line:
                # Extraer tipos principales
                main_types = card.type_line.split(' — ')[0].split(' ')
                for card_type in main_types:
                    if card_type and card_type not in ['Legendary', 'Basic', 'Snow']:
                        types.add(card_type)
        
        return sorted(list(types))
    
    def get_statistics(self) -> Dict[str, any]:
        """Obtiene estadísticas de la colección"""
        cards = self.load_cards()
        
        total_cards = len(cards)
        total_quantity = sum(card.quantity for card in cards)
        
        colors = {}
        rarities = {}
        types = {}
        
        for card in cards:
            # Contar colores
            for color in card.color_identity:
                colors[color] = colors.get(color, 0) + card.quantity
            
            # Contar rarezas
            if card.rarity:
                rarities[card.rarity] = rarities.get(card.rarity, 0) + card.quantity
            
            # Contar tipos
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