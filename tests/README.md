# Tests - MTG Deck Constructor

This directory contains all tests for the MTG Deck Constructor application.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Configuration and shared fixtures
├── test_models.py           # Tests for models (Card, Deck)
├── test_services.py         # Tests for services
├── test_controllers.py      # Tests for controllers
├── test_integration.py      # Integration tests
└── README.md               # This file
```

## Test Types

### Unit Tests
- **test_models.py**: Tests for `Card` and `Deck` classes
- **test_services.py**: Tests for `CardService`, `DeckService`, `ImageService`
- **test_controllers.py**: Tests for `AppController`, `CardController`, `DeckController`

### Integration Tests
- **test_integration.py**: Tests that verify the joint operation of multiple components

## How to Run Tests

### Option 1: Custom Script (Recommended)

```bash
# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage

# Run only unit tests
python run_tests.py --unit

# Run only integration tests
python run_tests.py --integration

# Run specific module
python run_tests.py --module test_models

# Verbose output
python run_tests.py --verbose
```

### Option 2: unittest (Python standard)

```bash
# Run all tests
python -m unittest discover tests

# Run specific test
python -m unittest tests.test_models

# Run with verbose output
python -m unittest discover tests -v
```

### Option 3: pytest (Recommended for development)

```bash
# Install testing dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests in parallel
pytest -n auto

# Generate HTML coverage report
pytest --cov=src --cov-report=html
```

## Test Configuration

### Environment Variables
- `MTG_TEST_MODE=1`: Activates testing mode (configured automatically)

### Available Fixtures

Reusable fixtures are defined in `conftest.py`:

- `sample_cards_data`: DataFrame with sample card data
- `sample_cards`: List of sample Card objects
- `lightning_bolt`, `counterspell`, `serra_angel`: Specific cards
- `sample_deck`, `empty_deck`: Sample decks
- `temp_directory`: Temporary directory for tests
- `temp_cards_file`: Temporary CSV file with data
- `mock_card_service`, `mock_deck_service`: Service mocks

### Test Markers

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Tests that take longer
- `@pytest.mark.network`: Tests that require network connection
- `@pytest.mark.gui`: Graphical interface tests

## Code Coverage

### Generate Coverage Report

```bash
# With custom script
python run_tests.py --coverage

# With pytest
pytest --cov=src --cov-report=html --cov-report=term

# Only with coverage
coverage run -m pytest
coverage report
coverage html
```

### Interpret Results

- **Green**: Lines covered by tests
- **Red**: Lines not covered
- **Yellow**: Partially covered lines

Goal: Maintain coverage > 80%

## Best Practices

### Writing Tests

1. **Nombres descriptivos**: `test_add_card_to_deck_success`
2. **Arrange-Act-Assert**: Organize, execute, verify
3. **One concept per test**: Each test should verify one thing
4. **Independent tests**: Should not depend on execution order
5. **Use fixtures**: Reuse common configuration

### Test Example

```python
def test_add_card_to_deck(sample_deck, lightning_bolt):
    """Test adding card to deck"""
    # Arrange
    initial_count = sample_deck.total_cards
    
    # Act
    sample_deck.add_card(lightning_bolt, 2)
    
    # Assert
    assert sample_deck.total_cards == initial_count + 2
    assert sample_deck.cards[lightning_bolt.name] == 2
```

### Mocking

Use mocks for:
- External services (Scryfall API)
- File system
- Databases
- Graphical interfaces

```python
from unittest.mock import Mock, patch

@patch('requests.get')
def test_download_image(mock_get):
    mock_get.return_value.status_code = 200
    # Test implementation
```

## Debugging Tests

### Failed Tests

```bash
# Run only failed tests
pytest --lf

# Stop on first failure
pytest -x

# Show local variables on failures
pytest -l

# Enter debugger on failure
pytest --pdb
```

### Logging in Tests

```python
import logging

def test_with_logging(caplog):
    with caplog.at_level(logging.INFO):
        # Test code
        pass
    assert "Expected message" in caplog.text
```

## Continuous Integration

For CI/CD, use:

```bash
# Run tests with CI output
pytest --junitxml=test-results.xml --cov=src --cov-report=xml
```

## Troubleshooting

### Common Problems

1. **ImportError**: Verify that `src` is in PYTHONPATH
2. **FileNotFoundError**: Use temporary file fixtures
3. **Slow tests**: Use mocks instead of real operations
4. **Flaky tests**: Check dependencies between tests

### Solutions

```python
# Add src to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Use temporary directory
import tempfile
with tempfile.TemporaryDirectory() as temp_dir:
    # Test code
```

## Contributing

When adding new features:

1. Write tests before code (TDD)
2. Maintain high coverage
3. Update fixtures if necessary
4. Document complex tests
5. Run entire suite before commit

```bash
# Verify before commit
python run_tests.py --coverage
```