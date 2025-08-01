# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete project documentation
- Installation and configuration guide
- API and architecture documentation
- Development and contribution guide
- Complete test suite with 66.7% success rate
- Improved .gitignore configuration

### Changed
- Complete restructuring of project architecture
- Migration to MVC pattern with services
- Significant improvement in test coverage

### Fixed
- Fixed service initialization in tests
- Aligned controller methods with real implementation
- Fixed method signatures in tests
- Fixes in data models (Card and Deck)

## [1.0.0] - 2025-01-31

### Added
- Initial implementation of MTG Deck Constructor
- MVC architecture with separate services
- Models for Card and Deck
- Services for card, deck, image and Scryfall management
- Controllers for application, cards and decks
- Graphical interface with tkinter
- Image cache system
- Scryfall API integration
- Support for multiple Magic formats (Standard, Modern, etc.)
- Card search and filtering functionalities
- Deck builder with validation
- Deck export and import
- Statistical deck analysis
- Logging system
- JSON file configuration

### Technical Details
- Python 3.8+ compatible
- Modular and testable architecture
- Robust error handling
- Inline code documentation
- Flexible JSON configuration

---

## Types of Changes
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for features that will be removed
- `Removed` for removed features
- `Fixed` for bug fixes
- `Security` for security vulnerabilities