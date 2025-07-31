import unittest
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.card import Card
from models.deck import Deck


class TestCard(unittest.TestCase):
    """Tests para el modelo Card"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.card_data = {
            'card_name': 'Lightning Bolt',
            'mana_cost': '{R}',
            'type_line': 'Instant',
            'oracle_text': 'Lightning Bolt deals 3 damage to any target.',
            'power': None,
            'toughness': None,
            'colors': ['R'],
            'color_identity': ['R'],
            'rarity': 'common',
            'set_code': 'LEA',
            'collector_number': '161'
        }
    
    def test_card_creation(self):
        """Test creación básica de carta"""
        card = Card(**self.card_data)
        self.assertEqual(card.card_name, 'Lightning Bolt')
        self.assertEqual(card.mana_cost, '{R}')
        self.assertEqual(card.type_line, 'Instant')
        self.assertEqual(card.colors, ['R'])
    
    def test_card_is_creature(self):
        """Test identificación de criaturas"""
        # Carta que no es criatura
        card = Card(**self.card_data)
        self.assertFalse(card.is_creature)
        
        # Carta que es criatura
        creature_data = self.card_data.copy()
        creature_data.update({
            'type_line': 'Creature — Human Wizard',
            'power': '2',
            'toughness': '1'
        })
        creature = Card(**creature_data)
        self.assertTrue(creature.is_creature)
    
    def test_card_colors(self):
        """Test manejo de colores"""
        card = Card(**self.card_data)
        self.assertEqual(card.colors, ['R'])
        self.assertIn('R', card.colors)
        self.assertNotIn('U', card.colors)
    
    def test_card_multicolor(self):
        """Test carta multicolor"""
        multicolor_data = self.card_data.copy()
        multicolor_data.update({
            'colors': ['R', 'U'],
            'color_identity': ['R', 'U']
        })
        card = Card(**multicolor_data)
        self.assertIn('R', card.colors)
        self.assertIn('U', card.colors)
    
    def test_card_string_representation(self):
        """Test representación en string"""
        card = Card(**self.card_data)
        self.assertEqual(card.display_name, 'Lightning Bolt')
        self.assertIn('Lightning Bolt', str(card))


class TestDeck(unittest.TestCase):
    """Tests para el modelo Deck"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.deck = Deck(name="Test Deck")
        
        # Crear cartas de prueba
        self.lightning_bolt = Card(
            card_name='Lightning Bolt',
            mana_cost='{R}',
            type_line='Instant',
            colors=['R'],
            rarity='common'
        )
        
        self.counterspell = Card(
            card_name='Counterspell',
            mana_cost='{U}{U}',
            type_line='Instant',
            colors=['U'],
            rarity='common'
        )
    
    def test_deck_creation(self):
        """Test creación básica de mazo"""
        self.assertEqual(self.deck.name, "Test Deck")
        self.assertEqual(len(self.deck.cards), 0)
        self.assertEqual(self.deck.total_cards, 0)
    
    def test_add_card(self):
        """Test agregar cartas al mazo"""
        self.deck.add_card(self.lightning_bolt, 4)
        self.assertEqual(len(self.deck.cards), 1)
        self.assertEqual(self.deck.total_cards, 4)
        found_card = self.deck.find_card(self.lightning_bolt.card_name)
        self.assertEqual(found_card.quantity, 4)
    
    def test_remove_card(self):
        """Test remover cartas del mazo"""
        self.deck.add_card(self.lightning_bolt, 4)
        self.deck.remove_card(self.lightning_bolt.card_name, 2)
        found_card = self.deck.find_card(self.lightning_bolt.card_name)
        self.assertEqual(found_card.quantity, 2)
        self.assertEqual(self.deck.total_cards, 2)
        
        # Remover todas las cartas
        self.deck.remove_card(self.lightning_bolt.card_name, 2)
        found_card = self.deck.find_card(self.lightning_bolt.card_name)
        self.assertIsNone(found_card)
        self.assertEqual(self.deck.total_cards, 0)
    
    def test_deck_colors(self):
        """Test identificación de colores del mazo"""
        self.deck.add_card(self.lightning_bolt, 4)
        self.deck.add_card(self.counterspell, 4)
        
        colors = self.deck.color_distribution
        self.assertIn('R', colors)
        self.assertIn('U', colors)
    
    def test_mana_curve(self):
        """Test curva de maná"""
        self.deck.add_card(self.lightning_bolt, 4)
        self.deck.add_card(self.counterspell, 4)
        
        curve = self.deck.mana_curve
        # Verificar que la curva contiene las cartas agregadas
        self.assertGreater(sum(curve.values()), 0)
    
    def test_deck_validation(self):
        """Test validación de mazo"""
        # Mazo vacío no es válido para formatos que requieren mínimo de cartas
        self.assertEqual(self.deck.total_cards, 0)
        
        # Agregar suficientes cartas
        for i in range(60):
            self.deck.add_card(self.lightning_bolt, 1)
        
        # Ahora debería tener 60 cartas
        self.assertTrue(self.deck.total_cards >= 60)
        
        # Test format validation if available
        if hasattr(self.deck, 'is_legal_format'):
            self.assertTrue(self.deck.is_legal_format('standard'))
    
    def test_deck_export_import(self):
        """Test exportar e importar mazo"""
        self.deck.add_card(self.lightning_bolt, 4)
        self.deck.add_card(self.counterspell, 4)
        
        # Exportar
        deck_data = self.deck.to_dict()
        self.assertEqual(deck_data['name'], 'Test Deck')
        self.assertEqual(len(deck_data['cards']), 2)
        
        # Importar
        new_deck = Deck.from_dict(deck_data)
        self.assertEqual(new_deck.name, 'Test Deck')
        self.assertEqual(new_deck.total_cards, 8)


if __name__ == '__main__':
    unittest.main()