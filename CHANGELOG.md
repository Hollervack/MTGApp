# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Documentación completa del proyecto
- Guía de instalación y configuración
- Documentación de API y arquitectura
- Guía de desarrollo y contribución
- Suite de tests completa con 66.7% de éxito
- Configuración de .gitignore mejorada

### Changed
- Reestructuración completa de la arquitectura del proyecto
- Migración a patrón MVC con servicios
- Mejora significativa en la cobertura de tests

### Fixed
- Corrección de inicialización de servicios en tests
- Alineación de métodos de controladores con implementación real
- Corrección de signatures de métodos en tests
- Fixes en modelos de datos (Card y Deck)

## [1.0.0] - 2025-01-31

### Added
- Implementación inicial del MTG Deck Constructor
- Arquitectura MVC con servicios separados
- Modelos para Card y Deck
- Servicios para gestión de cartas, mazos, imágenes y Scryfall
- Controladores para aplicación, cartas y mazos
- Interfaz gráfica con tkinter
- Sistema de cache para imágenes
- Integración con API de Scryfall
- Soporte para múltiples formatos de Magic (Standard, Modern, etc.)
- Funcionalidades de búsqueda y filtrado de cartas
- Constructor de mazos con validación
- Exportación e importación de mazos
- Análisis estadístico de mazos
- Sistema de logging
- Configuración mediante archivo JSON

### Technical Details
- Python 3.8+ compatible
- Arquitectura modular y testeable
- Separación clara de responsabilidades
- Inyección de dependencias
- Manejo de errores robusto
- Cache inteligente de recursos

## Tipos de Cambios

- `Added` para nuevas funcionalidades
- `Changed` para cambios en funcionalidades existentes
- `Deprecated` para funcionalidades que serán removidas
- `Removed` para funcionalidades removidas
- `Fixed` para corrección de bugs
- `Security` para vulnerabilidades de seguridad