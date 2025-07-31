# Guía de Desarrollo

## Configuración del Entorno de Desarrollo

### Requisitos

- Python 3.8+
- pip
- Git
- Editor de código (VS Code recomendado)

### Configuración Inicial

1. **Clonar y configurar el proyecto:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd MTGDeckConstructorApp
   python -m venv venv
   source venv/bin/activate  # En macOS/Linux
   pip install -r requirements.txt
   ```

2. **Instalar dependencias de desarrollo:**
   ```bash
   pip install pytest pytest-cov black flake8 mypy
   ```

## Estructura del Código

### Principios de Arquitectura

- **Separación de responsabilidades**: Cada módulo tiene una responsabilidad específica
- **Inyección de dependencias**: Los servicios se inyectan en los controladores
- **Testabilidad**: Todo el código debe ser testeable unitariamente
- **Modularidad**: Componentes independientes y reutilizables

### Convenciones de Código

- **Estilo**: Seguir PEP 8
- **Nombres**: snake_case para funciones y variables, PascalCase para clases
- **Documentación**: Docstrings para todas las clases y métodos públicos
- **Imports**: Organizados en orden: stdlib, third-party, local

## Testing

### Ejecutar Tests

```bash
# Todos los tests
python -m pytest

# Tests específicos
python -m pytest tests/test_services.py

# Con cobertura
python -m pytest --cov=src

# Usando el script personalizado
python run_tests.py
```

### Estructura de Tests

- `tests/test_models.py`: Tests para modelos de datos
- `tests/test_services.py`: Tests para servicios
- `tests/test_controllers.py`: Tests para controladores
- `tests/test_integration.py`: Tests de integración

### Escribir Tests

#### Tests Unitarios

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

#### Tests de Integración

```python
def test_complete_workflow(self):
    # Test que verifica el flujo completo de la aplicación
    deck = self.deck_controller.create_new_deck("Test Deck")
    self.deck_controller.add_card_to_deck("Lightning Bolt", 4)
    result = self.deck_controller.save_current_deck()
    self.assertTrue(result)
```

### Mocking

Usar mocks para:
- Servicios externos (Scryfall API)
- Operaciones de archivo
- Bases de datos

```python
@patch('src.services.card_service.CardService._load_cards_from_file')
def test_load_cards(self, mock_load):
    mock_load.return_value = [{'name': 'Test Card'}]
    # Test implementation
```

## Contribuir al Proyecto

### Flujo de Trabajo

1. **Fork del repositorio**
2. **Crear rama feature:**
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. **Desarrollar y testear**
4. **Commit con mensajes descriptivos:**
   ```bash
   git commit -m "feat: añadir búsqueda avanzada de cartas"
   ```
5. **Push y crear Pull Request**

### Convenciones de Commit

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `test:` Añadir o modificar tests
- `refactor:` Refactorización de código
- `style:` Cambios de formato

### Checklist antes de PR

- [ ] Tests pasan (`python -m pytest`)
- [ ] Código formateado (`black src/ tests/`)
- [ ] Linting sin errores (`flake8 src/`)
- [ ] Documentación actualizada
- [ ] Changelog actualizado (si aplica)

## Debugging

### Logs

La aplicación utiliza el módulo `logging` de Python:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Información importante")
logger.error("Error ocurrido")
```

### Configuración de Logs

Los logs se configuran en `main.py` y se guardan en `logs/`.

### Debugging en IDE

Configuración para VS Code (`.vscode/launch.json`):

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

### Optimizaciones Implementadas

- **Cache de imágenes**: Las imágenes se almacenan localmente
- **Lazy loading**: Los datos se cargan bajo demanda
- **Indexación**: Búsquedas optimizadas en la base de datos de cartas

### Profiling

```python
import cProfile

def profile_function():
    # Código a perfilar
    pass

cProfile.run('profile_function()')
```

## Deployment

### Preparar Release

1. **Actualizar versión** en `setup.py` o `__version__.py`
2. **Actualizar CHANGELOG.md**
3. **Ejecutar tests completos**
4. **Crear tag de versión:**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

### Distribución

```bash
# Crear distribución
python setup.py sdist bdist_wheel

# Subir a PyPI (si aplica)
twine upload dist/*
```

## Recursos Adicionales

- [Documentación de Magic: The Gathering](https://magic.wizards.com/)
- [API de Scryfall](https://scryfall.com/docs/api)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [pytest Documentation](https://docs.pytest.org/)