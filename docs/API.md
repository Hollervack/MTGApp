# API Documentation

## Project Architecture

The project follows an MVC (Model-View-Controller) architecture with additional services:

- **Models**: Represent data entities (Card, Deck)
- **Views**: User interface (GUI with tkinter)
- **Controllers**: Control logic between views and services
- **Services**: Business logic and data access

## Main Services

### CardService

Manages card-related operations.

#### Main Methods:

- `load_cards()`: Loads cards from CSV file
- `search_cards(query, limit=50)`: Searches cards by name
- `find_card_by_name(name)`: Finds a specific card by name
- `get_cards_by_color(color)`: Filters cards by color
- `get_random_cards(count=10)`: Gets random cards
- `get_statistics()`: Gets collection statistics

### DeckService

Manages deck-related operations.

#### Main Methods:

- `create_deck(name, format_type='Standard')`: Creates a new deck
- `save_deck(deck, filename)`: Saves a deck to file
- `load_deck(filename)`: Loads a deck from file
- `list_decks()`: Lists all saved decks
- `delete_deck(filename)`: Deletes a deck
- `analyze_deck(deck)`: Analyzes deck statistics
- `validate_deck_format(deck, format_type)`: Validates if a deck complies with a format

### ScryfallService

Integration with Scryfall API to get updated card data.

#### Main Methods:

- `search_cards(query)`: Searches cards on Scryfall
- `get_card_by_name(name)`: Gets detailed information of a card
- `get_random_card()`: Gets a random card
- `get_card_image_url(card_id)`: Gets the image URL of a card

### ImageService

Manages cache and download of card images.

#### Main Methods:

- `get_card_image(card_id, image_url)`: Gets card image (cache or download)
- `cache_image(url, filename)`: Stores image in cache
- `get_cache_info()`: Gets cache information
- `clear_cache()`: Clears image cache

## Controllers

### AppController

Main controller that coordinates the entire application.

### CardController

Manages card search and display operations.

#### Main Methods:

- `search_cards(query, limit=50)`: Searches cards
- `get_card_by_name(name)`: Gets specific card
- `get_random_cards(count=10)`: Gets random cards
- `advanced_search(filters)`: Advanced search with filters
- `get_similar_cards(card)`: Finds similar cards
- `get_cards_by_color(color)`: Filters by color

### DeckController

Manages deck construction and management operations.

#### Main Methods:

- `create_new_deck(name='New Deck', format_type='Standard')`: Creates new deck
- `load_deck(filename)`: Loads existing deck
- `save_current_deck()`: Saves current deck
- `add_card_to_deck(card_name, quantity=1)`: Adds card to deck
- `remove_card_from_deck(card_name, quantity=1)`: Removes card from deck
- `get_deck_analysis()`: Analyzes current deck
- `export_deck_to_file(filename, format_type='txt')`: Exports deck
- `validate_deck_format(format_type)`: Validates deck format
- `get_available_decks()`: Lists available decks
- `delete_deck(filename)`: Deletes deck

## Data Models

### Card

Represents a Magic: The Gathering card.

#### Attributes:

- `name`: Card name
- `mana_cost`: Mana cost
- `type_line`: Type line
- `oracle_text`: Card text
- `power`: Power (for creatures)
- `toughness`: Toughness (for creatures)
- `colors`: Card colors
- `rarity`: Rarity
- `set_code`: Set code
- `collector_number`: Collector number

#### Properties:

- `is_creature`: True if it's a creature
- `is_spell`: True if it's a spell
- `is_land`: True if it's a land

### Deck

Represents a deck of cards.

#### Attributes:

- `name`: Deck name
- `format_type`: Deck format (Standard, Modern, etc.)
- `cards`: Dictionary of cards and quantities
- `sideboard`: Dictionary of sideboard cards

#### Methods:

- `add_card(card, quantity=1, sideboard=False)`: Adds card to deck
- `remove_card(card_name, quantity=1, sideboard=False)`: Removes card
- `get_total_cards()`: Gets total cards
- `get_mana_curve()`: Calculates mana curve
- `get_color_distribution()`: Calculates color distribution
- `is_legal_format(format_type)`: Verifies format legality
- `to_dict()`: Converts to dictionary
- `from_dict(data)`: Creates from dictionary

## File Formats

### Decks (.deck)

Decks are saved in JSON format with the following structure:

```json
{
  "name": "Deck Name",
  "format": "Standard",
  "cards": {
    "Lightning Bolt": 4,
    "Counterspell": 3
  },
  "sideboard": {
    "Negate": 2
  }
}
```

### Card Database (.csv)

The card database uses CSV format with the following columns:

- name
- mana_cost
- type_line
- oracle_text
- power
- toughness
- colors
- rarity
- set
- collector_number