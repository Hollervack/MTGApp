#!/usr/bin/env python3
"""Starting point of the MTG Deck Constructor application"""

import sys
import logging
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from src.controllers.app_controller import AppController
from src.views.main_window import MainWindow
from src.config.settings import get_settings


def setup_logging():
    """Configures basic logging before initializing the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main application function"""
    try:
        # Configure basic logging
        setup_logging()
        logger = logging.getLogger('MTGDeckConstructor.Main')
        
        logger.info("Inizializing MTG Deck Constructor...")
        
        # Inicializar controlador principal
        app_controller = AppController()
        
        # Initialize application
        if not app_controller.initialize_application():
            logger.error("Error initializing application")
            sys.exit(1)
        
        # Create and show main window
        main_window = MainWindow(app_controller)
        
        # Run application
        main_window.run()
        
        logger.info("App closed successfully")
        
    except KeyboardInterrupt:
        logger.info("App interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Critical error in the application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()