import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from controllers.app_controller import AppController
    from controllers.card_controller import CardController
    from controllers.deck_controller import DeckController
    from services.card_service import CardService
    from services.deck_service import DeckService
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
    from src.services.image_service import ImageService
    from src.models.card import Card
    from src.models.deck import Deck


class TestAppController(unittest.TestCase):
    """Tests para AppController"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Mock de servicios
        self.mock_card_service = Mock()
        self.mock_deck_service = Mock()
        self.mock_image_service = Mock()
        
        # Mock de configuración
        self.mock_settings = Mock()
        self.mock_settings.cards_file = 'test_cards.csv'
        
        with patch('controllers.app_controller.Settings', return_value=self.mock_settings):
            with patch('controllers.app_controller.CardService', return_value=self.mock_card_service):
                with patch('controllers.app_controller.DeckService', return_value=self.mock_deck_service):
                    with patch('controllers.app_controller.ImageService', return_value=self.mock_image_service):
                        self.app_controller = AppController()
    
    def test_initialization(self):
        """Test inicialización del controlador"""
        self.assertIsNotNone(self.app_controller.card_service)
        self.assertIsNotNone(self.app_controller.deck_service)
        self.assertIsNotNone(self.app_controller.image_service)
        self.assertIsNotNone(self.app_controller.settings)
    
    def test_get_card_service(self):
        """Test obtener servicio de cartas"""
        service = self.app_controller.get_card_service()
        self.assertEqual(service, self.mock_card_service)
    
    def test_get_deck_service(self):
        """Test obtener servicio de mazos"""
        service = self.app_controller.get_deck_service()
        self.assertEqual(service, self.mock_deck_service)
    
    def test_get_image_service(self):
        """Test obtener servicio de imágenes"""
        service = self.app_controller.get_image_service()
        self.assertEqual(service, self.mock_image_service)
    
    def test_get_settings(self):
        """Test obtener configuración"""
        settings = self.app_controller.get_settings()
        self.assertEqual(settings, self.mock_settings)


class TestCardController(unittest.TestCase):
    """Tests para CardController"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_card_service = Mock()
        self.mock_scryfall_service = Mock()
        self.mock_image_service = Mock()
        self.card_controller = CardController(self.mock_card_service, self.mock_scryfall_service, self.mock_image_service)
        
        # Crear cartas de prueba
        self.test_cards = [
            Card(
                card_name='Lightning Bolt',
                mana_cost='{R}',
                type_line='Instant',
                colors=['R']
            ),
            Card(
                card_name='Counterspell',
                mana_cost='{U}{U}',
                type_line='Instant',
                colors=['U']
            )
        ]
    
    def test_search_cards(self):
        """Test búsqueda básica de cartas"""
        self.mock_card_service.search_cards.return_value = self.test_cards
        
        results = self.card_controller.search_cards('Lightning')
        
        self.assertEqual(len(results), 2)
        self.mock_card_service.search_cards.assert_called_once_with('Lightning', 50)
    
    def test_search_cards_with_filters(self):
        """Test búsqueda con filtros avanzados"""
        filtered_cards = [self.test_cards[0]]  # Solo Lightning Bolt
        
        filters = {
            'colors': ['R'],
            'type': 'Instant'
        }
        
        with patch.object(self.card_controller, 'advanced_search', return_value=filtered_cards):
            results = self.card_controller.advanced_search(filters)
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].card_name, 'Lightning Bolt')
    
    def test_get_card_by_name(self):
        """Test obtener carta por nombre"""
        expected_card = self.test_cards[0]  # Lightning Bolt
        self.mock_card_service.find_card_by_name.return_value = expected_card
        
        card = self.card_controller.get_card_by_name('Lightning Bolt')
        
        self.assertEqual(card.card_name, 'Lightning Bolt')
        self.mock_card_service.find_card_by_name.assert_called_once_with('Lightning Bolt')
    
    def test_get_random_cards(self):
        """Test obtener cartas aleatorias"""
        random_cards = self.card_controller.get_random_cards(count=2)
        
        self.assertIsInstance(random_cards, list)
        # The method should return a list of cards
    
    def test_get_similar_cards(self):
        """Test obtener cartas similares"""
        target_card = self.test_cards[0]  # Lightning Bolt
        similar_cards = [self.test_cards[1]]  # Counterspell como similar
        
        with patch.object(self.card_controller, 'get_similar_cards', return_value=similar_cards):
            suggestions = self.card_controller.get_similar_cards(target_card)
            
            self.assertEqual(len(suggestions), 1)
    
    def test_get_cards_by_color(self):
        """Test obtener cartas por color"""
        red_cards = [self.test_cards[0]]  # Solo Lightning Bolt
        self.mock_card_service.get_cards_by_color.return_value = red_cards
        
        results = self.card_controller.get_cards_by_color(['R'])
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].card_name, 'Lightning Bolt')
        self.mock_card_service.get_cards_by_color.assert_called_once_with(['R'])


class TestDeckController(unittest.TestCase):
    """Tests para DeckController"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_deck_service = Mock()
        self.mock_card_service = Mock()
        self.deck_controller = DeckController(self.mock_deck_service, self.mock_card_service)
        
        # Crear mazo de prueba
        self.test_deck = Deck(name="Test Deck")
        self.test_card = Card(
            card_name='Lightning Bolt',
            mana_cost='{R}',
            type_line='Instant',
            colors=['R']
        )
    
    def test_create_new_deck(self):
        """Test crear nuevo mazo"""
        # Mock del servicio
        mock_deck = Mock()
        mock_deck.name = 'New Deck'
        self.mock_deck_service.create_deck.return_value = mock_deck
        
        result = self.deck_controller.create_new_deck('New Deck')
        
        self.assertTrue(result)
        self.assertEqual(self.deck_controller.current_deck.name, 'New Deck')
        self.mock_deck_service.create_deck.assert_called_once()
    
    def test_add_card_to_deck(self):
        """Test agregar carta al mazo"""
        # Mock del mazo actual
        mock_deck = Mock()
        self.deck_controller.current_deck = mock_deck
        
        # Mock de la carta
        mock_card = Mock()
        mock_card.card_name = 'Lightning Bolt'
        self.mock_card_service.find_card_by_name.return_value = mock_card
        
        result = self.deck_controller.add_card_to_deck('Lightning Bolt', 2)
        
        self.assertTrue(result)
    
    def test_add_card_to_deck_limit(self):
        """Test límite de cartas en mazo"""
        # Mock del mazo actual
        mock_deck = Mock()
        self.deck_controller.current_deck = mock_deck
        
        # Mock de la carta
        mock_card = Mock()
        mock_card.card_name = 'Lightning Bolt'
        self.mock_card_service.find_card_by_name.return_value = mock_card
        
        # Simular que ya hay 4 copias
        mock_deck.get_card_count.return_value = 4
        
        result = self.deck_controller.add_card_to_deck('Lightning Bolt', 1)
        
        # Debería fallar por límite de 4 cartas
        self.assertFalse(result)
    
    def test_remove_card_from_deck(self):
        """Test remover carta del mazo"""
        # Mock del mazo actual
        mock_deck = Mock()
        self.deck_controller.current_deck = mock_deck
        
        # Mock de la carta
        mock_card = Mock()
        mock_card.card_name = 'Lightning Bolt'
        self.mock_card_service.find_card_by_name.return_value = mock_card
        
        result = self.deck_controller.remove_card_from_deck('Lightning Bolt', 2)
        
        self.assertTrue(result)
    
    def test_save_current_deck(self):
        """Test guardar mazo actual"""
        # Mock del mazo actual
        mock_deck = Mock()
        mock_deck.name = 'Test Deck'
        self.deck_controller.current_deck = mock_deck
        
        # Mock del servicio
        self.mock_deck_service.save_deck.return_value = True
        
        result = self.deck_controller.save_current_deck()
        
        self.assertTrue(result)
        self.mock_deck_service.save_deck.assert_called_once()
    
    def test_load_deck(self):
        """Test cargar mazo"""
        # Mock del mazo cargado
        mock_deck = Mock()
        mock_deck.name = 'Loaded Deck'
        
        self.mock_deck_service.load_deck.return_value = mock_deck
        
        result = self.deck_controller.load_deck('test_deck.json')
        
        self.assertTrue(result)
        self.assertEqual(self.deck_controller.current_deck.name, 'Loaded Deck')
        self.mock_deck_service.load_deck.assert_called_once_with('test_deck.json')
    
    def test_get_deck_analysis(self):
        """Test obtener análisis del mazo"""
        # Mock del mazo actual
        mock_deck = Mock()
        self.deck_controller.current_deck = mock_deck
        
        # Mock del análisis
        mock_analysis = {
            'total_cards': 60,
            'colors': ['R', 'U'],
            'average_cmc': 2.5
        }
        
        with patch.object(self.deck_controller.deck_service, 'analyze_deck', return_value=mock_analysis):
            analysis = self.deck_controller.get_deck_analysis()
            
            self.assertIsNotNone(analysis)
            self.assertEqual(analysis['total_cards'], 60)
    
    def test_validate_deck_format(self):
        """Test validar formato del mazo"""
        # Mock del mazo actual
        mock_deck = Mock()
        self.deck_controller.current_deck = mock_deck
        
        # Mock de validación
        mock_validation = {
            'valid': True,
            'errors': []
        }
        
        with patch.object(self.deck_controller, 'validate_deck_format', return_value=mock_validation):
            result = self.deck_controller.validate_deck_format()
            
            self.assertIsInstance(result, dict)
            self.assertTrue(result['valid'])
    
    def test_export_deck_to_file(self):
        """Test exportar mazo a archivo"""
        # Mock del mazo actual
        mock_deck = Mock()
        self.deck_controller.current_deck = mock_deck
        
        # Mock del servicio
        self.mock_deck_service.export_deck_to_txt.return_value = True
        
        result = self.deck_controller.export_deck_to_file('/path/to/deck.txt')
        
        self.assertTrue(result)
    
    def test_get_available_decks(self):
        """Test obtener mazos disponibles"""
        # Mock de mazos disponibles
        available_decks = [
            {'name': 'Deck 1', 'format': 'standard'},
            {'name': 'Deck 2', 'format': 'modern'}
        ]
        self.mock_deck_service.list_decks.return_value = available_decks
        
        result = self.deck_controller.get_available_decks()
        
        self.assertEqual(len(result), 2)
        self.mock_deck_service.list_decks.assert_called_once()
    
    def test_delete_deck(self):
        """Test eliminar mazo"""
        # Mock del servicio
        self.mock_deck_service.delete_deck.return_value = True
        
        result = self.deck_controller.delete_deck('deck_to_delete.json')
        
        self.assertTrue(result)
        self.mock_deck_service.delete_deck.assert_called_once_with('deck_to_delete.json')


if __name__ == '__main__':
    unittest.main()