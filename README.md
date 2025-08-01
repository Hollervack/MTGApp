# MTG Deck Constructor App

A modern and comprehensive application for building and managing Magic: The Gathering decks, developed in Python with a modular and professional architecture.

## 🎯 Key Features

- **Intuitive Deck Builder**: Modern graphical interface for creating and editing decks
- **Card Browser**: Advanced search and filtering of cards
- **Collection Management**: Manage your personal card collection
- **Deck Analysis**: Detailed statistics of mana curve, color distribution and types
- **Collection Comparison**: Check which cards you have available to build decks
- **Import/Export**: Support for common text formats
- **Image Cache**: Automatically downloads and stores card images
- **Scryfall Integration**: Access to the most complete MTG database

## 🏗️ Project Architecture

The project follows a modular MVC (Model-View-Controller) architecture:

```
MTGDeckConstructorApp/
├── src/
│   ├── models/          # Data models (Card, Deck)
│   ├── views/           # Graphic interface
│   ├── controllers/     # Bussiness logic
│   ├── services/        # Services (API, cache, data)
│   └── config/          # Configuration
├── data/                # App data
├── tests/               # Unit Tests
├── docs/                # Documents
├── main.py              # Starting point
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## 🚀 Quick Installation

```bash
git clone <repository-url>
cd MTGDeckConstructorApp
python -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
python main.py
```

📖 **For detailed instructions, see [docs/INSTALLATION.md](docs/INSTALLATION.md)**

## 📚 Documentation

- **[Installation and Configuration](docs/INSTALLATION.md)** - Complete installation guide
- **[API and Architecture](docs/API.md)** - Detailed technical documentation
- **[Development Guide](docs/DEVELOPMENT.md)** - For contributors and developers
- **[Changelog](CHANGELOG.md)** - Project change history

## 🧪 Testing

The project includes a complete test suite with **66.7% success rate**:

```bash
# Run all tests
python -m pytest

# Run with custom script
python run_tests.py

# Tests with coverage
python -m pytest --cov=src
```

## ✨ Technical Features

- **MVC Architecture**: Clear separation of responsibilities
- **Dependency Injection**: Modular and testable code
- **Smart Cache**: Performance optimization for images
- **API Integration**: Connection with Scryfall for updated data
- **Testing Suite**: Unit and integration tests
- **Type Hints**: Self-documented and more maintainable code
- **Error Handling**: Robust error and exception handling

## 📊 Data Structure

### Cards File (CSV)

The application expects a `data/cartas.csv` file with the following structure:

```csv
card_name,quantity,mana_cost,type_line,colors,rarity,set_code
"Lightning Bolt",4,"R","Instant","R","common","M21"
"Counterspell",2,"UU","Instant","U","common","M21"
```

### Configuration

The application automatically generates a `config.json` file with customizable settings:

- File and directory paths
- Interface configurations
- Image cache parameters
- API configurations

## 🎮 Application Usage

### Deck Builder

1. **Create New Deck**: `File > New Deck` or `Ctrl+N`
2. **Add Cards**: Search for cards and add them to the deck
3. **Save Deck**: `File > Save Deck` or `Ctrl+S`
4. **Analyze Deck**: `Tools > Analyze Deck`

### Card Browser

- **Simple Search**: Type the card name
- **Advanced Filters**: By color, type, rarity, set, etc.
- **Image View**: Visualize cards with their official images

### Collection Management

- **View Collection**: Explore all your cards
- **Update Quantities**: Modify the quantities of cards you own
- **Statistics**: View summaries of your collection

## 🔧 Advanced Configuration

### Path Customization

Edit the `config.json` file to customize:

```json
{
  "data": {
    "cards_file": "data/cartas.csv",
    "decks_directory": "data/decks",
    "images_directory": "data/images"
  }
}
```

### Image Cache Configuration

```json
{
  "images": {
    "cache_enabled": true,
    "cache_size_mb": 500,
    "auto_download": true,
    "image_quality": "normal"
  }
}
```

## 🧪 Development and Testing

### Running Tests

```bash
# Install development dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

### Code Formatting

```bash
# Install formatting tools
pip install black flake8

# Format code
black src/

# Check style
flake8 src/
```

## 📁 Detailed File Structure

### Models (`src/models/`)
- `card.py`: Data model for MTG cards
- `deck.py`: Data model for decks

### Services (`src/services/`)
- `card_service.py`: Card and collection management
- `deck_service.py`: Deck operations
- `image_service.py`: Image cache and download
- `scryfall_service.py`: Scryfall API integration

### Controllers (`src/controllers/`)
- `app_controller.py`: Main application controller
- `deck_controller.py`: Deck management logic
- `card_controller.py`: Card management logic

### Views (`src/views/`)
- `main_window.py`: Main application window
- `deck_builder_view.py`: Deck builder view
- `card_browser_view.py`: Card browser view
- `collection_view.py`: Collection view

## 🤝 Contributing

Contributions are welcome. Please:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is under the MIT License. See the `LICENSE` file for more details.

## 🙏 Acknowledgments

- [Scryfall](https://scryfall.com/) for providing the MTG data API
- [Wizards of the Coast](https://company.wizards.com/) for Magic: The Gathering
- The Python community for the excellent libraries used

## 📞 Support

If you encounter any problems or have suggestions:

1. Check the [existing Issues](../../issues)
2. Create a new Issue if necessary
3. Provide detailed information about the problem

---

**MTG Deck Constructor App** - Build decks like a professional 🎴✨