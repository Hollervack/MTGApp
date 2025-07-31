#!/usr/bin/env python3
"""Punto de entrada principal para MTG Deck Constructor App"""

import sys
import logging
from pathlib import Path

# Añadir el directorio src al path para importaciones
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from src.controllers.app_controller import AppController
from src.views.main_window import MainWindow
from src.config.settings import get_settings


def setup_logging():
    """Configura el logging básico antes de inicializar la aplicación"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Función principal de la aplicación"""
    try:
        # Configurar logging básico
        setup_logging()
        logger = logging.getLogger('MTGDeckConstructor.Main')
        
        logger.info("Iniciando MTG Deck Constructor...")
        
        # Inicializar controlador principal
        app_controller = AppController()
        
        # Inicializar aplicación
        if not app_controller.initialize_application():
            logger.error("Error al inicializar la aplicación")
            sys.exit(1)
        
        # Crear y mostrar ventana principal
        main_window = MainWindow(app_controller)
        
        # Ejecutar aplicación
        main_window.run()
        
        logger.info("Aplicación cerrada correctamente")
        
    except KeyboardInterrupt:
        logger.info("Aplicación interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error crítico en la aplicación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()