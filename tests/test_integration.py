import unittest
import sys
import os
import tempfile
import shutil
import json
from unittest.mock import patch, Mock
import pandas as pd

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from controllers.app_controller import AppController
    from controllers.card_controller import CardController
    from controllers.deck_controller import DeckController
    from services.card_service import CardService
    from services.deck_service import DeckService
    from services.scryfall_service import ScryfallService
    from services.image_service import ImageService
    from models.card import Card
    from models.deck import Deck
except ImportError:
    # Fallback para imports absolutos
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from src.controllers.app_controller import AppController
    from src.controllers.card_controller import CardController
    from src.controllers.deck_controller import DeckController
    from src.services.card_service import CardService
    from src.services.deck_service import DeckService
    from src.services.scryfall_service import ScryfallService
    from src.services.image_service import ImageService
    from src.models.card import Card
    from src.models.deck import Deck


class TestIntegration(unittest.TestCase):
    """Tests de integración para el sistema completo"""
    
    def setUp(self):
        """Configuración inicial para tests de integración"""
        # Crear directorio temporal para tests
        self.test_dir = tempfile.mkdtemp()
        self.cards_file = os.path.join(self.test_dir, 'test_cards.csv')
        self.decks_dir = os.path.join(self.test_dir, 'decks')
        
        # Crear datos de prueba
        self.test_data = pd.DataFrame([
            {
                'card_name': 'Lightning Bolt',
                'mana_cost': '{R}',
                'type_line': 'Instant',
                'oracle_text': 'Lightning Bolt deals 3 damage to any target.',
                'power': '',
                'toughness': '',
                'colors': "['R']",
                'color_identity': "['R']",
                'rarity': 'common',
                'set_code': 'LEA',
                'collector_number': '161',
                'artist': 'Christopher Rush',
                'image_uris': '{}'
            },
            {
                'card_name': 'Counterspell',
                'mana_cost': '{U}{U}',
                'type_line': 'Instant',
                'oracle_text': 'Counter target spell.',
                'power': '',
                'toughness': '',
                'colors': "['U']",
                'color_identity': "['U']",
                'rarity': 'common',
                'set_code': 'LEA',
                'collector_number': '055',
                'artist': 'Mark Poole',
                'image_uris': '{}'
            },
            {
                'card_name': 'Serra Angel',
                'mana_cost': '{3}{W}{W}',
                'type_line': 'Creature — Angel',
                'oracle_text': 'Flying, vigilance',
                'power': '4',
                'toughness': '4',
                'colors': "['W']",
                'color_identity': "['W']",
                'rarity': 'uncommon',
                'set_code': 'LEA',
                'collector_number': '030',
                'artist': 'Douglas Shuler',
                'image_uris': '{}'
            }
        ])
        
        # Guardar datos de prueba
        self.test_data.to_csv(self.cards_file, index=False)
        
        # Crear directorio de mazos
        os.makedirs(self.decks_dir, exist_ok=True)
    
    def tearDown(self):
        """Limpieza después de cada test"""
        shutil.rmtree(self.test_dir)
    
    def test_card_service_integration(self):
        """Test integración del servicio de cartas"""
        card_service = CardService(self.cards_file)
        
        # Verificar carga de cartas
        self.assertEqual(len(card_service.cards), 3)
        
        # Test búsqueda por nombre
        results = card_service.search_cards(card_name='Lightning')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].card_name, 'Lightning Bolt')
        
        # Test búsqueda por color
        red_cards = card_service.search_cards(colors=['R'])
        self.assertEqual(len(red_cards), 1)
        
        # Test búsqueda por tipo
        instants = card_service.search_cards(type_line='Instant')
        self.assertEqual(len(instants), 2)
        
        # Test búsqueda por tipo de carta
        creatures = card_service.search_cards(type_line='Creature')
        self.assertEqual(len(creatures), 1)
    
    def test_deck_service_integration(self):
        """Test integración del servicio de mazos"""
        # Crear servicios
        card_service = CardService(self.cards_file)
        deck_service = DeckService(card_service, self.decks_dir)
        
        # Test crear mazo
        deck = deck_service.create_deck('Integration Test Deck')
        self.assertEqual(deck.name, 'Integration Test Deck')
        
        # Test agregar cartas
        lightning_bolt = card_service.find_card_by_name('Lightning Bolt')
        self.assertIsNotNone(lightning_bolt)
        
        deck.add_card(lightning_bolt, 4)
        self.assertEqual(deck.total_cards, 4)
        
        # Test guardar mazo
        save_result = deck_service.save_deck(deck)
        self.assertTrue(save_result)
        
        # Verificar que el archivo existe
        expected_filename = deck_service._safe_filename(deck.name) + '.json'
        deck_file = os.path.join(self.decks_dir, expected_filename)
        self.assertTrue(os.path.exists(deck_file))
        
        # Test cargar mazo
        loaded_deck = deck_service.load_deck(expected_filename)
        self.assertIsNotNone(loaded_deck)
        self.assertEqual(loaded_deck.name, 'Integration Test Deck')
        self.assertEqual(loaded_deck.total_cards, 4)
        
        # Test listar mazos
        decks = deck_service.list_decks()
        self.assertIsInstance(decks, list)
        self.assertTrue(len(decks) > 0)
        
        deck_names = [d['name'] for d in decks]
        self.assertIn('Integration Test Deck', deck_names)
    
    def test_card_controller_integration(self):
        """Test integración del controlador de cartas"""
        card_service = CardService(self.cards_file)
        card_controller = CardController(card_service)
        
        # Test búsqueda de cartas
        results = card_controller.search_cards(card_name='Lightning')
        self.assertEqual(len(results), 1)
        
        # Test obtener detalles de carta
        card = card_controller.get_card_details('Lightning Bolt')
        self.assertIsNotNone(card)
        self.assertEqual(card.card_name, 'Lightning Bolt')
        
        # Test cartas aleatorias
        random_cards = card_controller.get_random_cards(2)
        self.assertEqual(len(random_cards), 2)
        
        # Test sugerencias
        suggestions = card_controller.get_card_suggestions('Light')
        self.assertGreater(len(suggestions), 0)
    
    def test_deck_controller_integration(self):
        """Test integración del controlador de mazos"""
        # Crear servicios
        card_service = CardService(self.cards_file)
        deck_service = DeckService(card_service, self.decks_dir)
        
        # Crear controlador
        deck_controller = DeckController(deck_service, card_service)
        
        # Test crear mazo
        result = deck_controller.create_new_deck("Integration Deck")
        self.assertTrue(result)
        self.assertTrue(deck_controller.has_current_deck())
        
        # Test agregar carta al mazo actual
        result = deck_controller.add_card_to_deck('Lightning Bolt', 4)
        self.assertTrue(result)
        
        current_deck = deck_controller.get_current_deck()
        self.assertIsNotNone(current_deck)
        self.assertEqual(current_deck.total_cards, 4)
        
        # Test guardar mazo
        save_result = deck_controller.save_current_deck()
        self.assertTrue(save_result)
        
        # Test cargar mazo
        deck_controller.clear_current_deck()
        load_result = deck_controller.load_deck('Integration_Deck.json')
        self.assertTrue(load_result)
        self.assertEqual(deck_controller.get_current_deck().name, "Integration Deck")
    
    @patch('src.config.settings.Settings')
    def test_app_controller_integration(self, mock_settings_class):
        """Test integración del controlador principal"""
        # Mock settings
        mock_settings = Mock()
        mock_settings.cards_file = self.cards_file
        mock_settings.decks_directory = self.decks_dir
        mock_settings_class.return_value = mock_settings
        
        # Crear controlador de aplicación
        app_controller = AppController()
        
        # Verificar servicios
        self.assertIsNotNone(app_controller.get_card_service())
        self.assertIsNotNone(app_controller.get_deck_service())
        self.assertIsNotNone(app_controller.get_image_service())
        
        # Test flujo completo: buscar carta y crear mazo
        card_service = app_controller.get_card_service()
        deck_service = app_controller.get_deck_service()
        
        # Buscar carta
        cards = card_service.search_cards(card_name='Lightning')
        self.assertEqual(len(cards), 1)
        
        # Crear mazo y agregar carta
        deck = Deck(name="App Integration Deck")
        deck.add_card(cards[0], 4)
        
        # Guardar mazo
        result = deck_service.save_deck(deck, 'app_integration_deck.json')
        self.assertTrue(result)
    
    def test_complete_workflow(self):
        """Test flujo de trabajo completo"""
        # 1. Inicializar servicios
        card_service = CardService(self.cards_file)
        deck_service = DeckService(card_service, self.decks_dir)
        
        # 2. Crear servicios adicionales
        scryfall_service = Mock(spec=ScryfallService)
        image_service = Mock(spec=ImageService)
        
        # 3. Crear controladores
        card_controller = CardController(card_service, scryfall_service, image_service)
        deck_controller = DeckController(deck_service, card_service)
        
        # 3. Buscar cartas para el mazo
        red_cards = card_controller.search_cards('Lightning')
        blue_cards = card_controller.search_cards('Counterspell')
        white_cards = card_controller.search_cards('Serra')
        
        # 4. Crear mazo
        result = deck_controller.create_new_deck("Complete Workflow Deck")
        self.assertTrue(result)
        
        # 5. Agregar cartas al mazo
        if red_cards:
            deck_controller.add_card_to_deck(red_cards[0].card_name, 4)
        if blue_cards:
            deck_controller.add_card_to_deck(blue_cards[0].card_name, 4)
        if white_cards:
            deck_controller.add_card_to_deck(white_cards[0].card_name, 2)
        
        # 6. Verificar estadísticas del mazo actual
        current_deck = deck_controller.get_current_deck()
        self.assertIsNotNone(current_deck)
        self.assertEqual(current_deck.total_cards, 10)
        
        # 7. Guardar mazo
        save_result = deck_controller.save_current_deck()
        self.assertTrue(save_result)
        
        # 8. Cargar mazo guardado
        deck_controller.clear_current_deck()
        load_result = deck_controller.load_deck('Complete_Workflow_Deck.json')
        self.assertTrue(load_result)
        self.assertEqual(deck_controller.get_current_deck().total_cards, 10)
    
    def test_error_handling(self):
        """Test manejo de errores en integración"""
        # Test archivo de cartas inexistente
        with self.assertRaises(FileNotFoundError):
            CardService('nonexistent_file.csv')
        
        # Test cargar mazo inexistente
        card_service = CardService(self.cards_file)
        deck_service = DeckService(card_service, self.decks_dir)
        deck = deck_service.load_deck('nonexistent_deck.json')
        self.assertIsNone(deck)
        
        # Test búsqueda sin resultados
        card_service = CardService(self.cards_file)
        results = card_service.search_cards(card_name='Nonexistent Card')
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()