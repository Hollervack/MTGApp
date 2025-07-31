"""Configuración y fixtures compartidas para todos los tests

Este archivo contiene fixtures de pytest que pueden ser utilizadas
en cualquier test del proyecto.
"""

import pytest
import tempfile
import shutil
import os
import sys
import pandas as pd
from unittest.mock import Mock

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.card import Card
from models.deck import Deck
from services.card_service import CardService
from services.deck_service import DeckService


@pytest.fixture
def sample_cards_data():
    """Datos de cartas de ejemplo para tests"""
    return pd.DataFrame([
        {
            'name': 'Lightning Bolt',
            'mana_cost': '{R}',
            'type_line': 'Instant',
            'oracle_text': 'Lightning Bolt deals 3 damage to any target.',
            'power': '',
            'toughness': '',
            'colors': "['R']",
            'color_identity': "['R']",
            'cmc': 1,
            'rarity': 'common',
            'set': 'LEA',
            'collector_number': '161',
            'artist': 'Christopher Rush',
            'image_uris': '{}'
        },
        {
            'name': 'Counterspell',
            'mana_cost': '{U}{U}',
            'type_line': 'Instant',
            'oracle_text': 'Counter target spell.',
            'power': '',
            'toughness': '',
            'colors': "['U']",
            'color_identity': "['U']",
            'cmc': 2,
            'rarity': 'common',
            'set': 'LEA',
            'collector_number': '055',
            'artist': 'Mark Poole',
            'image_uris': '{}'
        },
        {
            'name': 'Serra Angel',
            'mana_cost': '{3}{W}{W}',
            'type_line': 'Creature — Angel',
            'oracle_text': 'Flying, vigilance',
            'power': '4',
            'toughness': '4',
            'colors': "['W']",
            'color_identity': "['W']",
            'cmc': 5,
            'rarity': 'uncommon',
            'set': 'LEA',
            'collector_number': '030',
            'artist': 'Douglas Shuler',
            'image_uris': '{}'
        },
        {
            'name': 'Black Lotus',
            'mana_cost': '{0}',
            'type_line': 'Artifact',
            'oracle_text': '{T}, Sacrifice Black Lotus: Add three mana of any one color.',
            'power': '',
            'toughness': '',
            'colors': "[]",
            'color_identity': "[]",
            'cmc': 0,
            'rarity': 'rare',
            'set': 'LEA',
            'collector_number': '232',
            'artist': 'Christopher Rush',
            'image_uris': '{}'
        },
        {
            'name': 'Shivan Dragon',
            'mana_cost': '{4}{R}{R}',
            'type_line': 'Creature — Dragon',
            'oracle_text': 'Flying',
            'power': '5',
            'toughness': '5',
            'colors': "['R']",
            'color_identity': "['R']",
            'cmc': 6,
            'rarity': 'rare',
            'set': 'LEA',
            'collector_number': '175',
            'artist': 'Melissa A. Benson',
            'image_uris': '{}'
        }
    ])


@pytest.fixture
def sample_cards(sample_cards_data):
    """Lista de objetos Card de ejemplo"""
    cards = []
    for _, row in sample_cards_data.iterrows():
        card = Card(
            name=row['name'],
            mana_cost=row['mana_cost'],
            type_line=row['type_line'],
            oracle_text=row['oracle_text'],
            power=row['power'] if row['power'] else None,
            toughness=row['toughness'] if row['toughness'] else None,
            colors=eval(row['colors']),
            color_identity=eval(row['color_identity']),
            cmc=row['cmc'],
            rarity=row['rarity'],
            set_code=row['set'],
            collector_number=row['collector_number'],
            artist=row['artist']
        )
        cards.append(card)
    return cards


@pytest.fixture
def lightning_bolt():
    """Carta Lightning Bolt de ejemplo"""
    return Card(
        name='Lightning Bolt',
        mana_cost='{R}',
        type_line='Instant',
        oracle_text='Lightning Bolt deals 3 damage to any target.',
        colors=['R'],
        color_identity=['R'],
        cmc=1,
        rarity='common',
        set_code='LEA',
        collector_number='161',
        artist='Christopher Rush'
    )


@pytest.fixture
def counterspell():
    """Carta Counterspell de ejemplo"""
    return Card(
        name='Counterspell',
        mana_cost='{U}{U}',
        type_line='Instant',
        oracle_text='Counter target spell.',
        colors=['U'],
        color_identity=['U'],
        cmc=2,
        rarity='common',
        set_code='LEA',
        collector_number='055',
        artist='Mark Poole'
    )


@pytest.fixture
def serra_angel():
    """Carta Serra Angel de ejemplo"""
    return Card(
        name='Serra Angel',
        mana_cost='{3}{W}{W}',
        type_line='Creature — Angel',
        oracle_text='Flying, vigilance',
        power='4',
        toughness='4',
        colors=['W'],
        color_identity=['W'],
        cmc=5,
        rarity='uncommon',
        set_code='LEA',
        collector_number='030',
        artist='Douglas Shuler'
    )


@pytest.fixture
def sample_deck(lightning_bolt, counterspell):
    """Mazo de ejemplo con algunas cartas"""
    deck = Deck(name="Sample Deck")
    deck.add_card(lightning_bolt, 4)
    deck.add_card(counterspell, 4)
    return deck


@pytest.fixture
def empty_deck():
    """Mazo vacío para tests"""
    return Deck(name="Empty Deck")


@pytest.fixture
def temp_directory():
    """Directorio temporal para tests que requieren archivos"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_cards_file(sample_cards_data, temp_directory):
    """Archivo CSV temporal con datos de cartas"""
    cards_file = os.path.join(temp_directory, 'test_cards.csv')
    sample_cards_data.to_csv(cards_file, index=False)
    return cards_file


@pytest.fixture
def temp_decks_directory(temp_directory):
    """Directorio temporal para mazos"""
    decks_dir = os.path.join(temp_directory, 'decks')
    os.makedirs(decks_dir, exist_ok=True)
    return decks_dir


@pytest.fixture
def mock_card_service(sample_cards):
    """Mock del servicio de cartas"""
    service = Mock(spec=CardService)
    service.cards = sample_cards
    service.search_cards.return_value = sample_cards
    service.get_card_by_name.return_value = sample_cards[0]
    service.get_random_cards.return_value = sample_cards[:2]
    return service


@pytest.fixture
def mock_deck_service():
    """Mock del servicio de mazos"""
    service = Mock(spec=DeckService)
    service.save_deck.return_value = True
    service.load_deck.return_value = Deck(name="Mock Deck")
    service.list_saved_decks.return_value = ['deck1.json', 'deck2.json']
    service.validate_deck_format.return_value = True
    service.export_deck_to_text.return_value = "Mock Deck\n4 Lightning Bolt\nTotal: 4 cards"
    return service


@pytest.fixture
def mock_image_service():
    """Mock del servicio de imágenes"""
    service = Mock()
    service.download_card_image.return_value = True
    service.get_card_image_path.return_value = '/path/to/image.jpg'
    service.get_cache_info.return_value = {'total_images': 10, 'total_size': 1024}
    service.clear_cache.return_value = True
    return service


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Configuración automática para todos los tests"""
    # Configurar variables de entorno para tests
    os.environ['MTG_TEST_MODE'] = '1'
    
    yield
    
    # Limpiar después del test
    if 'MTG_TEST_MODE' in os.environ:
        del os.environ['MTG_TEST_MODE']


# Marcadores personalizados para categorizar tests
pytestmark = [
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.filterwarnings("ignore::PendingDeprecationWarning")
]


def pytest_configure(config):
    """Configuración personalizada de pytest"""
    # Registrar marcadores personalizados
    config.addinivalue_line(
        "markers", "unit: marca test como unitario"
    )
    config.addinivalue_line(
        "markers", "integration: marca test como de integración"
    )
    config.addinivalue_line(
        "markers", "slow: marca test como lento"
    )
    config.addinivalue_line(
        "markers", "network: marca test que requiere red"
    )
    config.addinivalue_line(
        "markers", "gui: marca test de interfaz gráfica"
    )


def pytest_collection_modifyitems(config, items):
    """Modificar items de test durante la recolección"""
    # Agregar marcador 'slow' a tests de integración
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        elif "test_models" in item.nodeid or "test_services" in item.nodeid or "test_controllers" in item.nodeid:
            item.add_marker(pytest.mark.unit)