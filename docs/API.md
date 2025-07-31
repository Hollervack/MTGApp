# Documentación de la API

## Arquitectura del Proyecto

El proyecto sigue una arquitectura MVC (Model-View-Controller) con servicios adicionales:

- **Models**: Representan las entidades de datos (Card, Deck)
- **Views**: Interfaz de usuario (GUI con tkinter)
- **Controllers**: Lógica de control entre vistas y servicios
- **Services**: Lógica de negocio y acceso a datos

## Servicios Principales

### CardService

Gestiona las operaciones relacionadas con cartas.

#### Métodos Principales:

- `load_cards()`: Carga las cartas desde el archivo CSV
- `search_cards(query, limit=50)`: Busca cartas por nombre
- `find_card_by_name(name)`: Encuentra una carta específica por nombre
- `get_cards_by_color(color)`: Filtra cartas por color
- `get_random_cards(count=10)`: Obtiene cartas aleatorias
- `get_statistics()`: Obtiene estadísticas de la colección

### DeckService

Gestiona las operaciones relacionadas con mazos.

#### Métodos Principales:

- `create_deck(name, format_type='Standard')`: Crea un nuevo mazo
- `save_deck(deck, filename)`: Guarda un mazo en archivo
- `load_deck(filename)`: Carga un mazo desde archivo
- `list_decks()`: Lista todos los mazos guardados
- `delete_deck(filename)`: Elimina un mazo
- `analyze_deck(deck)`: Analiza las estadísticas de un mazo
- `validate_deck_format(deck, format_type)`: Valida si un mazo cumple con un formato

### ScryfallService

Integración con la API de Scryfall para obtener datos actualizados de cartas.

#### Métodos Principales:

- `search_cards(query)`: Busca cartas en Scryfall
- `get_card_by_name(name)`: Obtiene información detallada de una carta
- `get_random_card()`: Obtiene una carta aleatoria
- `get_card_image_url(card_id)`: Obtiene la URL de la imagen de una carta

### ImageService

Gestiona el cache y descarga de imágenes de cartas.

#### Métodos Principales:

- `get_card_image(card_id, image_url)`: Obtiene imagen de carta (cache o descarga)
- `cache_image(url, filename)`: Almacena imagen en cache
- `get_cache_info()`: Obtiene información del cache
- `clear_cache()`: Limpia el cache de imágenes

## Controladores

### AppController

Controlador principal que coordina toda la aplicación.

### CardController

Gestiona las operaciones de búsqueda y visualización de cartas.

#### Métodos Principales:

- `search_cards(query, limit=50)`: Busca cartas
- `get_card_by_name(name)`: Obtiene carta específica
- `get_random_cards(count=10)`: Obtiene cartas aleatorias
- `advanced_search(filters)`: Búsqueda avanzada con filtros
- `get_similar_cards(card)`: Encuentra cartas similares
- `get_cards_by_color(color)`: Filtra por color

### DeckController

Gestiona las operaciones de construcción y gestión de mazos.

#### Métodos Principales:

- `create_new_deck(name='New Deck', format_type='Standard')`: Crea nuevo mazo
- `load_deck(filename)`: Carga mazo existente
- `save_current_deck()`: Guarda el mazo actual
- `add_card_to_deck(card_name, quantity=1)`: Añade carta al mazo
- `remove_card_from_deck(card_name, quantity=1)`: Remueve carta del mazo
- `get_deck_analysis()`: Analiza el mazo actual
- `export_deck_to_file(filename, format_type='txt')`: Exporta mazo
- `validate_deck_format(format_type)`: Valida formato del mazo
- `get_available_decks()`: Lista mazos disponibles
- `delete_deck(filename)`: Elimina mazo

## Modelos de Datos

### Card

Representa una carta de Magic: The Gathering.

#### Atributos:

- `name`: Nombre de la carta
- `mana_cost`: Coste de maná
- `type_line`: Línea de tipo
- `oracle_text`: Texto de la carta
- `power`: Poder (para criaturas)
- `toughness`: Resistencia (para criaturas)
- `colors`: Colores de la carta
- `rarity`: Rareza
- `set_code`: Código del set
- `collector_number`: Número de coleccionista

#### Propiedades:

- `is_creature`: Verdadero si es una criatura
- `is_spell`: Verdadero si es un hechizo
- `is_land`: Verdadero si es una tierra

### Deck

Representa un mazo de cartas.

#### Atributos:

- `name`: Nombre del mazo
- `format_type`: Formato del mazo (Standard, Modern, etc.)
- `cards`: Diccionario de cartas y cantidades
- `sideboard`: Diccionario de cartas del sideboard

#### Métodos:

- `add_card(card, quantity=1, sideboard=False)`: Añade carta al mazo
- `remove_card(card_name, quantity=1, sideboard=False)`: Remueve carta
- `get_total_cards()`: Obtiene total de cartas
- `get_mana_curve()`: Calcula curva de maná
- `get_color_distribution()`: Calcula distribución de colores
- `is_legal_format(format_type)`: Verifica legalidad en formato
- `to_dict()`: Convierte a diccionario
- `from_dict(data)`: Crea desde diccionario

## Formatos de Archivo

### Mazos (.deck)

Los mazos se guardan en formato JSON con la siguiente estructura:

```json
{
  "name": "Nombre del Mazo",
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

### Base de Datos de Cartas (.csv)

La base de datos de cartas utiliza formato CSV con las siguientes columnas:

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