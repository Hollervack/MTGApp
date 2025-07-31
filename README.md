# MTG Deck Constructor App

Una aplicación moderna y completa para la construcción y gestión de mazos de Magic: The Gathering, desarrollada en Python con una arquitectura modular y profesional.

## 🎯 Características Principales

- **Constructor de Mazos Intuitivo**: Interfaz gráfica moderna para crear y editar mazos
- **Navegador de Cartas**: Búsqueda avanzada y filtrado de cartas
- **Gestión de Colección**: Administra tu colección personal de cartas
- **Análisis de Mazos**: Estadísticas detalladas de curva de maná, distribución de colores y tipos
- **Comparación con Colección**: Verifica qué cartas tienes disponibles para construir mazos
- **Importación/Exportación**: Soporte para formatos de texto comunes
- **Caché de Imágenes**: Descarga y almacena imágenes de cartas automáticamente
- **Integración con Scryfall**: Acceso a la base de datos más completa de MTG

## 🏗️ Arquitectura del Proyecto

El proyecto sigue una arquitectura MVC (Model-View-Controller) modular:

```
MTGDeckConstructorApp/
├── src/
│   ├── models/          # Modelos de datos (Card, Deck)
│   ├── views/           # Interfaces gráficas
│   ├── controllers/     # Lógica de negocio
│   ├── services/        # Servicios (API, caché, datos)
│   └── config/          # Configuraciones
├── data/                # Datos de la aplicación
├── tests/               # Pruebas unitarias
├── docs/                # Documentación
├── main.py              # Punto de entrada
├── requirements.txt     # Dependencias
└── README.md           # Este archivo
```

## 🚀 Instalación Rápida

```bash
git clone <repository-url>
cd MTGDeckConstructorApp
python -m venv venv
source venv/bin/activate  # En macOS/Linux
pip install -r requirements.txt
python main.py
```

📖 **Para instrucciones detalladas, consulta [docs/INSTALLATION.md](docs/INSTALLATION.md)**

## 📚 Documentación

- **[Instalación y Configuración](docs/INSTALLATION.md)** - Guía completa de instalación
- **[API y Arquitectura](docs/API.md)** - Documentación técnica detallada
- **[Guía de Desarrollo](docs/DEVELOPMENT.md)** - Para contribuidores y desarrolladores
- **[Changelog](CHANGELOG.md)** - Historial de cambios del proyecto

## 🧪 Testing

El proyecto incluye una suite completa de tests con **66.7% de éxito**:

```bash
# Ejecutar todos los tests
python -m pytest

# Ejecutar con el script personalizado
python run_tests.py

# Tests con cobertura
python -m pytest --cov=src
```

## ✨ Características Técnicas

- **Arquitectura MVC**: Separación clara de responsabilidades
- **Inyección de Dependencias**: Código modular y testeable
- **Cache Inteligente**: Optimización de rendimiento para imágenes
- **API Integration**: Conexión con Scryfall para datos actualizados
- **Testing Suite**: Tests unitarios y de integración
- **Type Hints**: Código autodocumentado y más mantenible
- **Error Handling**: Manejo robusto de errores y excepciones

## 📊 Estructura de Datos

### Archivo de Cartas (CSV)

La aplicación espera un archivo `data/cartas.csv` con la siguiente estructura:

```csv
card_name,quantity,mana_cost,type_line,colors,rarity,set_code
"Lightning Bolt",4,"R","Instant","R","common","M21"
"Counterspell",2,"UU","Instant","U","common","M21"
```

### Configuración

La aplicación genera automáticamente un archivo `config.json` con configuraciones personalizables:

- Rutas de archivos y directorios
- Configuraciones de interfaz
- Parámetros de caché de imágenes
- Configuraciones de API

## 🎮 Uso de la Aplicación

### Constructor de Mazos

1. **Crear un Nuevo Mazo**: `Archivo > Nuevo Mazo` o `Ctrl+N`
2. **Añadir Cartas**: Busca cartas y añádelas al mazo
3. **Guardar Mazo**: `Archivo > Guardar Mazo` o `Ctrl+S`
4. **Analizar Mazo**: `Herramientas > Analizar Mazo`

### Navegador de Cartas

- **Búsqueda Simple**: Escribe el nombre de la carta
- **Filtros Avanzados**: Por color, tipo, rareza, set, etc.
- **Vista de Imágenes**: Visualiza las cartas con sus imágenes oficiales

### Gestión de Colección

- **Ver Colección**: Explora todas tus cartas
- **Actualizar Cantidades**: Modifica las cantidades de cartas que posees
- **Estadísticas**: Ve resúmenes de tu colección

## 🔧 Configuración Avanzada

### Personalización de Rutas

Edita el archivo `config.json` para personalizar:

```json
{
  "data": {
    "cards_file": "data/cartas.csv",
    "decks_directory": "data/decks",
    "images_directory": "data/images"
  }
}
```

### Configuración de Caché de Imágenes

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

## 🧪 Desarrollo y Testing

### Ejecutar Pruebas

```bash
# Instalar dependencias de desarrollo
pip install pytest pytest-cov

# Ejecutar pruebas
pytest tests/

# Ejecutar con cobertura
pytest --cov=src tests/
```

### Formateo de Código

```bash
# Instalar herramientas de formateo
pip install black flake8

# Formatear código
black src/

# Verificar estilo
flake8 src/
```

## 📁 Estructura de Archivos Detallada

### Modelos (`src/models/`)
- `card.py`: Modelo de datos para cartas MTG
- `deck.py`: Modelo de datos para mazos

### Servicios (`src/services/`)
- `card_service.py`: Gestión de cartas y colección
- `deck_service.py`: Operaciones con mazos
- `image_service.py`: Caché y descarga de imágenes
- `scryfall_service.py`: Integración con API de Scryfall

### Controladores (`src/controllers/`)
- `app_controller.py`: Controlador principal de la aplicación
- `deck_controller.py`: Lógica de gestión de mazos
- `card_controller.py`: Lógica de gestión de cartas

### Vistas (`src/views/`)
- `main_window.py`: Ventana principal de la aplicación
- `deck_builder_view.py`: Vista del constructor de mazos
- `card_browser_view.py`: Vista del navegador de cartas
- `collection_view.py`: Vista de la colección

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- [Scryfall](https://scryfall.com/) por proporcionar la API de datos de MTG
- [Wizards of the Coast](https://company.wizards.com/) por Magic: The Gathering
- La comunidad de Python por las excelentes librerías utilizadas

## 📞 Soporte

Si encuentras algún problema o tienes sugerencias:

1. Revisa los [Issues existentes](../../issues)
2. Crea un nuevo Issue si es necesario
3. Proporciona información detallada sobre el problema

---

**MTG Deck Constructor App** - Construye mazos como un profesional 🎴✨