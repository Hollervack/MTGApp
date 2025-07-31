# Instalación y Configuración

## Requisitos del Sistema

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (para clonar el repositorio)

## Instalación

### 1. Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd MTGDeckConstructorApp
```

### 2. Crear Entorno Virtual (Recomendado)

```bash
python -m venv venv

# En macOS/Linux:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configuración Inicial

El archivo `config.json` contiene la configuración de la aplicación. Los valores por defecto deberían funcionar para la mayoría de casos de uso.

### 5. Ejecutar la Aplicación

```bash
python main.py
```

## Estructura de Directorios

```
MTGDeckConstructorApp/
├── src/                 # Código fuente principal
│   ├── controllers/     # Controladores de la aplicación
│   ├── models/         # Modelos de datos
│   ├── services/       # Servicios y lógica de negocio
│   └── views/          # Interfaz de usuario
├── tests/              # Tests unitarios e integración
├── data/               # Datos de cartas y mazos
├── docs/               # Documentación
├── cache/              # Cache de imágenes (generado automáticamente)
├── logs/               # Archivos de log (generado automáticamente)
└── main.py             # Punto de entrada de la aplicación
```

## Configuración Avanzada

### Base de Datos de Cartas

La aplicación utiliza un archivo CSV (`data/databaseMTG.csv`) como base de datos de cartas. Este archivo debe contener información sobre las cartas de Magic: The Gathering.

### Cache de Imágenes

Las imágenes de cartas se almacenan en cache en el directorio `cache/images/` para mejorar el rendimiento.

### Logs

Los archivos de log se generan automáticamente en el directorio `logs/` para ayudar en la depuración y monitoreo.