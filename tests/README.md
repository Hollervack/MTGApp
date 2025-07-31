# Tests - MTG Deck Constructor

Este directorio contiene todos los tests para la aplicación MTG Deck Constructor.

## Estructura de Tests

```
tests/
├── __init__.py              # Inicialización del paquete de tests
├── conftest.py              # Configuración y fixtures compartidas
├── test_models.py           # Tests para modelos (Card, Deck)
├── test_services.py         # Tests para servicios
├── test_controllers.py      # Tests para controladores
├── test_integration.py      # Tests de integración
└── README.md               # Este archivo
```

## Tipos de Tests

### Tests Unitarios
- **test_models.py**: Tests para las clases `Card` y `Deck`
- **test_services.py**: Tests para `CardService`, `DeckService`, `ImageService`
- **test_controllers.py**: Tests para `AppController`, `CardController`, `DeckController`

### Tests de Integración
- **test_integration.py**: Tests que verifican el funcionamiento conjunto de múltiples componentes

## Cómo Ejecutar los Tests

### Opción 1: Script Personalizado (Recomendado)

```bash
# Ejecutar todos los tests
python run_tests.py

# Ejecutar con cobertura
python run_tests.py --coverage

# Ejecutar solo tests unitarios
python run_tests.py --unit

# Ejecutar solo tests de integración
python run_tests.py --integration

# Ejecutar módulo específico
python run_tests.py --module test_models

# Salida detallada
python run_tests.py --verbose
```

### Opción 2: unittest (Python estándar)

```bash
# Ejecutar todos los tests
python -m unittest discover tests

# Ejecutar test específico
python -m unittest tests.test_models

# Ejecutar con salida detallada
python -m unittest discover tests -v
```

### Opción 3: pytest (Recomendado para desarrollo)

```bash
# Instalar dependencias de testing
pip install pytest pytest-cov pytest-mock

# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=src

# Ejecutar solo tests unitarios
pytest -m unit

# Ejecutar solo tests de integración
pytest -m integration

# Ejecutar tests en paralelo
pytest -n auto

# Generar reporte HTML de cobertura
pytest --cov=src --cov-report=html
```

## Configuración de Tests

### Variables de Entorno
- `MTG_TEST_MODE=1`: Activa el modo de testing (configurado automáticamente)

### Fixtures Disponibles

En `conftest.py` se definen fixtures reutilizables:

- `sample_cards_data`: DataFrame con datos de cartas de ejemplo
- `sample_cards`: Lista de objetos Card de ejemplo
- `lightning_bolt`, `counterspell`, `serra_angel`: Cartas específicas
- `sample_deck`, `empty_deck`: Mazos de ejemplo
- `temp_directory`: Directorio temporal para tests
- `temp_cards_file`: Archivo CSV temporal con datos
- `mock_card_service`, `mock_deck_service`: Mocks de servicios

### Marcadores de Tests

- `@pytest.mark.unit`: Tests unitarios
- `@pytest.mark.integration`: Tests de integración
- `@pytest.mark.slow`: Tests que tardan más tiempo
- `@pytest.mark.network`: Tests que requieren conexión de red
- `@pytest.mark.gui`: Tests de interfaz gráfica

## Cobertura de Código

### Generar Reporte de Cobertura

```bash
# Con el script personalizado
python run_tests.py --coverage

# Con pytest
pytest --cov=src --cov-report=html --cov-report=term

# Solo con coverage
coverage run -m pytest
coverage report
coverage html
```

### Interpretar Resultados

- **Verde**: Líneas cubiertas por tests
- **Rojo**: Líneas no cubiertas
- **Amarillo**: Líneas parcialmente cubiertas

Objetivo: Mantener cobertura > 80%

## Mejores Prácticas

### Escribir Tests

1. **Nombres descriptivos**: `test_add_card_to_deck_success`
2. **Arrange-Act-Assert**: Organizar, ejecutar, verificar
3. **Un concepto por test**: Cada test debe verificar una sola cosa
4. **Tests independientes**: No deben depender del orden de ejecución
5. **Usar fixtures**: Reutilizar configuración común

### Ejemplo de Test

```python
def test_add_card_to_deck(sample_deck, lightning_bolt):
    """Test agregar carta al mazo"""
    # Arrange
    initial_count = sample_deck.total_cards
    
    # Act
    sample_deck.add_card(lightning_bolt, 2)
    
    # Assert
    assert sample_deck.total_cards == initial_count + 2
    assert sample_deck.cards[lightning_bolt.name] == 2
```

### Mocking

Usar mocks para:
- Servicios externos (API de Scryfall)
- Sistema de archivos
- Bases de datos
- Interfaces gráficas

```python
from unittest.mock import Mock, patch

@patch('requests.get')
def test_download_image(mock_get):
    mock_get.return_value.status_code = 200
    # Test implementation
```

## Debugging Tests

### Tests Fallidos

```bash
# Ejecutar solo tests fallidos
pytest --lf

# Parar en primer fallo
pytest -x

# Mostrar variables locales en fallos
pytest -l

# Entrar en debugger en fallo
pytest --pdb
```

### Logging en Tests

```python
import logging

def test_with_logging(caplog):
    with caplog.at_level(logging.INFO):
        # Test code
        pass
    assert "Expected message" in caplog.text
```

## Integración Continua

Para CI/CD, usar:

```bash
# Ejecutar tests con salida para CI
pytest --junitxml=test-results.xml --cov=src --cov-report=xml
```

## Troubleshooting

### Problemas Comunes

1. **ImportError**: Verificar que `src` esté en el PYTHONPATH
2. **FileNotFoundError**: Usar fixtures de archivos temporales
3. **Tests lentos**: Usar mocks en lugar de operaciones reales
4. **Tests flaky**: Verificar dependencias entre tests

### Soluciones

```python
# Agregar src al path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Usar directorio temporal
import tempfile
with tempfile.TemporaryDirectory() as temp_dir:
    # Test code
```

## Contribuir

Al agregar nuevas funcionalidades:

1. Escribir tests antes del código (TDD)
2. Mantener cobertura alta
3. Actualizar fixtures si es necesario
4. Documentar tests complejos
5. Ejecutar toda la suite antes de commit

```bash
# Verificar antes de commit
python run_tests.py --coverage
```