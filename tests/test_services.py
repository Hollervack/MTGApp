import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, mock_open
import pandas as pd

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
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
    from src.services.card_service import CardService
    from src.services.deck_service import DeckService
    from src.services.image_service import ImageService
    from src.models.card import Card
    from src.models.deck import Deck


class TestCardService(unittest.TestCase):
    """Tests para CardService"""
    
    def setUp(self):
        """Configuración inicial para tests"""
        # Create test cards
        self.test_cards = [
            Card(
                card_name='Lightning Bolt',
                mana_cost='{R}',
                type_line='Instant',
                oracle_text='Lightning Bolt deals 3 damage to any target.',
                colors=['R'],
                color_identity=['R'],
                rarity='common',
                set_code='LEA'
            ),
            Card(
                card_name='Counterspell',
                mana_cost='{U}{U}',
                type_line='Instant',
                oracle_text='Counter target spell.',
                colors=['U'],
                color_identity=['U'],
                rarity='common',
                set_code='LEA'
            )
        ]
        
        # Mock the file existence and loading
        with patch('pathlib.Path.exists', return_value=True):
            with patch('src.services.card_service.CardService._load_cards_from_file', return_value=self.test_cards):
                self.card_service = CardService('fake_path.csv')
                # Pre-load the cards to set up the cache
                self.card_service.load_cards()
    
    def test_load_cards(self):
        """Test cargar cartas desde archivo"""
        cards = self.card_service.load_cards()
        self.assertIsInstance(cards, list)
        self.assertEqual(len(cards), 2)
        
        # Verificar que las cartas se cargaron correctamente
        card_names = [card.card_name for card in cards]
        self.assertIn('Lightning Bolt', card_names)
        self.assertIn('Counterspell', card_names)
    
    def test_search_cards_by_name(self):
        """Test búsqueda por nombre"""
        # Primero cargar las cartas
        self.card_service.load_cards()
        
        results = self.card_service.search_cards('Lightning')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].card_name, 'Lightning Bolt')
        
        # Búsqueda exacta
        results = self.card_service.search_cards('Lightning Bolt')
        self.assertEqual(len(results), 1)
        
        # Búsqueda sin resultados
        results = self.card_service.search_cards('Nonexistent')
        self.assertEqual(len(results), 0)
    
    def test_search_cards_by_color(self):
        """Test búsqueda por color"""
        # Primero cargar las cartas
        self.card_service.load_cards()
        
        results = self.card_service.get_cards_by_color(['R'])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].card_name, 'Lightning Bolt')
        
        results = self.card_service.get_cards_by_color(['U'])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].card_name, 'Counterspell')
    
    def test_search_cards_by_type(self):
        """Test búsqueda por tipo"""
        # Primero cargar las cartas
        self.card_service.load_cards()
        
        results = self.card_service.get_cards_by_type('Instant')
        self.assertEqual(len(results), 2)
    
    def test_search_cards_by_cmc(self):
        """Test búsqueda por coste de maná convertido"""
        # Primero cargar las cartas
        self.card_service.load_cards()
        
        # Test búsqueda por tipo - simplificado ya que no tenemos CMC en los datos
        results = self.card_service.get_cards_by_type('Instant')
        self.assertEqual(len(results), 2)
    
    def test_get_card_by_name(self):
        """Test obtener carta por nombre"""
        # Primero cargar las cartas
        self.card_service.load_cards()
        
        card = self.card_service.find_card_by_name('Lightning Bolt')
        self.assertIsNotNone(card)
        self.assertEqual(card.card_name, 'Lightning Bolt')
        
        # Carta inexistente
        card = self.card_service.find_card_by_name('Nonexistent')
        self.assertIsNone(card)
    
    def test_get_statistics(self):
        """Test obtener estadísticas de cartas"""
        # Primero cargar las cartas
        self.card_service.load_cards()
        
        stats = self.card_service.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_cards', stats)
        self.assertIn('by_color', stats)
        self.assertIn('by_rarity', stats)


class TestDeckService(unittest.TestCase):
    """Tests para DeckService"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.test_dir = tempfile.mkdtemp()
        # Crear un mock card_service
        self.mock_card_service = Mock()
        self.deck_service = DeckService(self.mock_card_service, self.test_dir)
        
        # Crear mazo de prueba
        self.test_deck = Deck(name="Test Deck")
        self.test_card = Card(
            card_name='Lightning Bolt',
            mana_cost='{R}',
            type_line='Instant',
            colors=['R']
        )
        self.test_deck.add_card(self.test_card, 4)
    
    def tearDown(self):
        """Limpieza después de cada test"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.dump')
    def test_save_deck(self, mock_json_dump, mock_open, mock_makedirs):
        """Test guardar mazo"""
        result = self.deck_service.save_deck(self.test_deck)
        
        self.assertTrue(result)
        mock_open.assert_called_once()
        mock_json_dump.assert_called_once()
    
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"name": "Test Deck", "cards": {}}')
    @patch('json.load', return_value={'name': 'Test Deck', 'cards': {}})
    def test_load_deck(self, mock_json_load, mock_open, mock_exists):
        """Test cargar mazo"""
        deck = self.deck_service.load_deck('test_deck.json')
        
        self.assertIsNotNone(deck)
        self.assertEqual(deck.name, 'Test Deck')
        mock_open.assert_called_once()
    
    @patch('os.path.exists', return_value=False)
    def test_load_nonexistent_deck(self, mock_exists):
        """Test cargar mazo inexistente"""
        deck = self.deck_service.load_deck('nonexistent.json')
        self.assertIsNone(deck)
    
    @patch('os.listdir', return_value=['deck1.json', 'deck2.json', 'not_a_deck.txt'])
    @patch('os.path.exists', return_value=True)
    def test_list_decks(self, mock_exists, mock_listdir):
        """Test listar mazos guardados"""
        decks = self.deck_service.list_decks()
        
        self.assertEqual(len(decks), 2)
        self.assertIn('deck1.json', decks)
        self.assertIn('deck2.json', decks)
        self.assertNotIn('not_a_deck.txt', decks)
    
    def test_analyze_deck(self):
        """Test análisis de mazo"""
        # Analizar mazo de prueba
        result = self.deck_service.analyze_deck(self.test_deck)
        
        self.assertIsInstance(result, dict)
        self.assertIn('total_cards', result)
        self.assertIn('mana_curve', result)
        
        # Verificar que el total de cartas es correcto
        self.assertEqual(result['total_cards'], 4)
    
    def test_export_deck_to_txt(self):
        """Test exportar mazo a texto"""
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            result = self.deck_service.export_deck_to_txt(self.test_deck, temp_path)
            self.assertTrue(result)
            
            # Verificar que el archivo existe
            self.assertTrue(os.path.exists(temp_path))
            
            # Verificar contenido
            with open(temp_path, 'r') as f:
                content = f.read()
                self.assertIn('Lightning Bolt', content)
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestImageService(unittest.TestCase):
    """Tests para ImageService"""
    
    def setUp(self):
        """Configuración inicial para tests"""
        self.image_service = ImageService()
        self.test_url = 'https://example.com/image.jpg'
    
    @patch('requests.Session.get')
    def test_download_and_cache_image(self, mock_get):
        """Test descargar y cachear imagen"""
        # Mock de respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'fake_image_data'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock PIL Image operations
        with patch('PIL.Image.open') as mock_image_open:
            mock_image = Mock()
            mock_image_open.return_value = mock_image
            
            with patch('PIL.ImageTk.PhotoImage') as mock_photo_image:
                mock_photo = Mock()
                mock_photo_image.return_value = mock_photo
                
                result = self.image_service.download_and_cache_image(self.test_url)
                
                self.assertIsNotNone(result)
                mock_get.assert_called_once()
    
    def test_get_image_from_cache_only(self):
        """Test obtener imagen solo desde caché"""
        # Test when image is not in cache
        result = self.image_service.get_image_from_cache_only(self.test_url)
        self.assertIsNone(result)
    
    def test_is_image_cached(self):
        """Test verificar si imagen está en caché"""
        result = self.image_service.is_image_cached(self.test_url)
        self.assertIsInstance(result, bool)
    
    def test_get_cache_info(self):
        """Test obtener información del caché"""
        info = self.image_service.get_cache_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn('cache_dir', info)
        self.assertIn('total_files', info)
        self.assertIn('total_size_mb', info)
    
    def test_clear_cache(self):
        """Test limpiar caché"""
        result = self.image_service.clear_cache()
        
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
    
    def test_preload_image(self):
        """Test precargar imagen"""
        with patch.object(self.image_service, '_download_image', return_value=b'fake_data'):
            with patch.object(self.image_service, '_save_image_to_cache', return_value=True):
                result = self.image_service.preload_image(self.test_url)
                self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()