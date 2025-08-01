# Development Guide

## Development Environment Setup

### Requirements

- Python 3.8+
- pip
- Git
- Code editor (VS Code recommended)

### Initial Setup

1. **Clone and configure the project:**
   ```bash
   git clone <REPOSITORY_URL>
   cd MTGDeckConstructorApp
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   pip install -r requirements.txt
   ```

2. **Install development dependencies:**
   ```bash
   pip install pytest pytest-cov black flake8 mypy
   ```

## Code Structure

### Architecture Principles

- **Separation of concerns**: Each module has a specific responsibility
- **Dependency injection**: Services are injected into controllers
- **Testability**: All code should be unit testable
- **Modularity**: Independent and reusable components

### Code Conventions

- **Style**: Follow PEP 8
- **Names**: snake_case for functions and variables, PascalCase for classes
- **Documentation**: Docstrings for all public classes and methods
- **Imports**: Organized in order: stdlib, third-party, local

## Testing

### Running Tests

```bash
# All tests
python -m pytest

# Specific tests
python -m pytest tests/test_services.py

# With coverage
python -m pytest --cov=src

# Using custom script
python run_tests.py
```

### Test Structure

- `tests/test_models.py`: Tests for data models
- `tests/test_services.py`: Tests for services
- `tests/test_controllers.py`: Tests for controllers
- `tests/test_integration.py`: Integration tests

### Writing Tests

#### Unit Tests

```python
import unittest
from unittest.mock import Mock, patch
from src.services.card_service import CardService

class TestCardService(unittest.TestCase):
    def setUp(self):
        self.card_service = CardService()
    
    def test_search_cards(self):
        # Arrange
        query = "Lightning"
        
        # Act
        result = self.card_service.search_cards(query)
        
        # Assert
        self.assertIsInstance(result, list)
```

#### Integration Tests

```python
def test_complete_workflow(self):
    # Test that verifies the complete application flow
    deck = self.deck_controller.create_new_deck("Test Deck")
    self.deck_controller.add_card_to_deck("Lightning Bolt", 4)
    result = self.deck_controller.save_current_deck()
    self.assertTrue(result)
```

### Mocking

Use mocks for:
- External services (Scryfall API)
- File operations
- Databases

```python
@patch('src.services.card_service.CardService._load_cards_from_file')
def test_load_cards(self, mock_load):
    mock_load.return_value = [{'name': 'Test Card'}]
    # Test implementation
```

## Contributing to the Project

### Workflow

1. **Fork the repository**
2. **Create feature branch:**
   ```bash
   git checkout -b feature/new-functionality
   ```
3. **Develop and test**
4. **Commit with descriptive messages:**
   ```bash
   git commit -m "feat: add advanced card search"
   ```
5. **Push and create Pull Request**

### Commit Conventions

- `feat:` New functionality
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Add or modify tests
- `refactor:` Code refactoring
- `style:` Format changes

### Checklist before PR

- [ ] Tests pass (`python -m pytest`)
- [ ] Code formatted (`black src/ tests/`)
- [ ] Linting without errors (`flake8 src/`)
- [ ] Documentation updated
- [ ] Changelog updated (if applicable)

## Debugging

### Logs

The application uses Python's `logging` module:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Important information")
logger.error("Error occurred")
```

### Log Configuration

Logs are configured in `main.py` and saved in `logs/`.

### IDE Debugging

Configuration for VS Code (`.vscode/launch.json`):

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Main",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal"
        }
    ]
}
```

## Performance

### Implemented Optimizations

- **Image cache**: Images are stored locally
- **Lazy loading**: Data is loaded on demand
- **Indexing**: Optimized searches in the card database

### Profiling

```python
import cProfile

def profile_function():
    # Code to profile
    pass

cProfile.run('profile_function()')
```

## Deployment

### Prepare Release

1. **Update version** in `setup.py` or `__version__.py`
2. **Update CHANGELOG.md**
3. **Run complete tests**
4. **Create version tag:**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

### Distribution

```bash
# Create distribution
python setup.py sdist bdist_wheel

# Upload to PyPI (if applicable)
twine upload dist/*
```

## Additional Resources

- [Magic: The Gathering Documentation](https://magic.wizards.com/)
- [Scryfall API](https://scryfall.com/docs/api)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [pytest Documentation](https://docs.pytest.org/)