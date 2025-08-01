"""Shared configuration and fixtures for all tests

This file contains pytest fixtures that can be used
in any test in the project.
"""

import pytest
import tempfile
import shutil
import os
import sys
import pandas as pd
from unittest.mock import Mock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.card import Card
from models.deck import Deck
from services.card_service import CardService
from services.deck_service import DeckService


@pytest.fixture
def sample_cards_data():
    """Sample card data for tests"""
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
    """List of sample Card objects"""
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
    """Sample Lightning Bolt card"""
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
    """Sample Counterspell card"""
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
    """Sample Serra Angel card"""
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
    """Sample deck with some cards"""
    deck = Deck(name="Sample Deck")
    deck.add_card(lightning_bolt, 4)
    deck.add_card(counterspell, 4)
    return deck


@pytest.fixture
def empty_deck():
    """Empty deck for tests"""
    return Deck(name="Empty Deck")


@pytest.fixture
def temp_directory():
    """Temporary directory for tests that require files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_cards_file(sample_cards_data, temp_directory):
    """Temporary CSV file with card data"""
    cards_file = os.path.join(temp_directory, 'test_cards.csv')
    sample_cards_data.to_csv(cards_file, index=False)
    return cards_file


@pytest.fixture
def temp_decks_directory(temp_directory):
    """Temporary directory for decks"""
    decks_dir = os.path.join(temp_directory, 'decks')
    os.makedirs(decks_dir, exist_ok=True)
    return decks_dir


@pytest.fixture
def mock_card_service(sample_cards):
    """Mock of the card service"""
    service = Mock(spec=CardService)
    service.cards = sample_cards
    service.search_cards.return_value = sample_cards
    service.get_card_by_name.return_value = sample_cards[0]
    service.get_random_cards.return_value = sample_cards[:2]
    return service


@pytest.fixture
def mock_deck_service():
    """Mock of the deck service"""
    service = Mock(spec=DeckService)
    service.save_deck.return_value = True
    service.load_deck.return_value = Deck(name="Mock Deck")
    service.list_saved_decks.return_value = ['deck1.json', 'deck2.json']
    service.validate_deck_format.return_value = True
    service.export_deck_to_text.return_value = "Mock Deck\n4 Lightning Bolt\nTotal: 4 cards"
    return service


@pytest.fixture
def mock_image_service():
    """Mock of the image service"""
    service = Mock()
    service.download_card_image.return_value = True
    service.get_card_image_path.return_value = '/path/to/image.jpg'
    service.get_cache_info.return_value = {'total_images': 10, 'total_size': 1024}
    service.clear_cache.return_value = True
    return service


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Automatic configuration for all tests"""
    # Configure environment variables for tests
    os.environ['MTG_TEST_MODE'] = '1'
    
    yield
    
    # Clean up after test
    if 'MTG_TEST_MODE' in os.environ:
        del os.environ['MTG_TEST_MODE']


# Custom markers to categorize tests
pytestmark = [
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.filterwarnings("ignore::PendingDeprecationWarning")
]


def pytest_configure(config):
    """Custom pytest configuration"""
    # Register custom markers
    config.addinivalue_line(
        "markers", "unit: mark test as unit"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )
    config.addinivalue_line(
        "markers", "network: mark test that requires network"
    )
    config.addinivalue_line(
        "markers", "gui: mark test for graphical interface"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test items during collection"""
    # Add 'slow' marker to integration tests
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        elif "test_models" in item.nodeid or "test_services" in item.nodeid or "test_controllers" in item.nodeid:
            item.add_marker(pytest.mark.unit)