"""Main window of the MTG Deck Constructor application"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from ..controllers.app_controller import AppController
from .deck_builder_view import DeckBuilderView
from .card_browser_view import CardBrowserView
from .collection_view import CollectionView


class MainWindow:
    """Main window of the MTG Deck Constructor application"""
    
    def __init__(self, app_controller: AppController):
        self.app_controller = app_controller
        self.settings = app_controller.get_settings()
        self.logger = logging.getLogger('MTGDeckConstructor.MainWindow')
        
        # Create main window
        self.root = tk.Tk()
        self.root.title(f"{self.settings.app_name} v{self.settings.app_version}")
        
        # Configure window
        self._setup_window()
        self._create_menu()
        self._create_main_interface()
        self._setup_bindings()
        
        # State variables
        self.current_view = None
        self.views = {}
        
        self.logger.info("Main window initialized")
    
    def _setup_window(self):
        """Configures the main window"""
        # Size and position
        width, height = self.settings.window_size
        self.root.geometry(f"{width}x{height}")
        
        if self.settings.get('ui.window_resizable', True):
            self.root.resizable(True, True)
        else:
            self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configure close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Configure style
        self.style = ttk.Style()
        theme = self.settings.get('ui.theme', 'default')
        if theme in self.style.theme_names():
            self.style.theme_use(theme)
    
    def _create_menu(self):
        """Creates the menu bar"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # File Menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Deck", command=self._new_deck, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Deck...", command=self._open_deck, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Deck", command=self._save_deck, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._save_deck_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Import Deck...", command=self._import_deck)
        file_menu.add_command(label="Export Deck...", command=self._export_deck)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing, accelerator="Ctrl+Q")
        
        # Edit Menu
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Search Cards...", command=self._show_card_browser, accelerator="Ctrl+F")
        edit_menu.add_command(label="Collection", command=self._show_collection, accelerator="Ctrl+L")
        edit_menu.add_separator()
        edit_menu.add_command(label="Preferences...", command=self._show_preferences)
        
        # View Menu
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Deck Builder", command=self._show_deck_builder)
        view_menu.add_command(label="Card Browser", command=self._show_card_browser)
        view_menu.add_command(label="Collection", command=self._show_collection)
        view_menu.add_separator()
        view_menu.add_command(label="Statistics", command=self._show_stats)
        
        # Tools Menu
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Analyze Deck", command=self._analyze_deck)
        tools_menu.add_command(label="Compare with Collection", command=self._compare_with_collection)
        tools_menu.add_command(label="Clear Image Cache", command=self._clear_image_cache)
        
        # Help Menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self._show_about)
    
    def _create_main_interface(self):
        """Creates the main interface"""
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barra de herramientas
        self._create_toolbar()
        
        # Área de contenido principal
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Status bar
        self._create_status_bar()
        
        # Mostrar vista inicial
        self._show_deck_builder()
    
    def _create_toolbar(self):
        """Creates the toolbar"""
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Main buttons
        ttk.Button(self.toolbar, text="New Deck", command=self._new_deck).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.toolbar, text="Open", command=self._open_deck).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.toolbar, text="Save", command=self._save_deck).pack(side=tk.LEFT, padx=(0, 5))
        
        # Separator
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Views
        ttk.Button(self.toolbar, text="Builder", command=self._show_deck_builder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.toolbar, text="Browser", command=self._show_card_browser).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.toolbar, text="Collection", command=self._show_collection).pack(side=tk.LEFT, padx=(0, 5))
        
        # Separador
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Tools
        ttk.Button(self.toolbar, text="Analyze", command=self._analyze_deck).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.toolbar, text="Compare", command=self._compare_with_collection).pack(side=tk.LEFT, padx=(0, 5))
    
    def _create_status_bar(self):
        """Creates the status bar"""
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Additional information
        self.info_var = tk.StringVar()
        self.info_label = ttk.Label(self.status_frame, textvariable=self.info_var)
        self.info_label.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Update initial information
        self._update_status_info()
    
    def _setup_bindings(self):
        """Configures keyboard shortcuts"""
        self.root.bind('<Control-n>', lambda e: self._new_deck())
        self.root.bind('<Control-o>', lambda e: self._open_deck())
        self.root.bind('<Control-s>', lambda e: self._save_deck())
        self.root.bind('<Control-Shift-S>', lambda e: self._save_deck_as())
        self.root.bind('<Control-f>', lambda e: self._show_card_browser())
        self.root.bind('<Control-l>', lambda e: self._show_collection())
        self.root.bind('<Control-q>', lambda e: self._on_closing())
        self.root.bind('<F5>', lambda e: self._refresh_current_view())
    
    def _show_view(self, view_class, view_name: str):
        """Shows a specific view"""
        try:
            # Limpiar contenido actual
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            
            # Crear o reutilizar vista
            if view_name not in self.views:
                if view_name == 'deck_builder':
                    self.views[view_name] = DeckBuilderView(
                        self.content_frame, 
                        self.app_controller.get_deck_service(),
                        self.app_controller.get_card_service(),
                        self.app_controller.get_image_service()
                    )
                elif view_name == 'card_browser':
                    self.views[view_name] = CardBrowserView(
                        self.content_frame,
                        self.app_controller.get_card_service(),
                        self.app_controller.get_image_service()
                    )
                elif view_name == 'collection':
                    self.views[view_name] = CollectionView(
                        self.content_frame,
                        self.app_controller.get_card_service()
                    )
            
            # Show view
            view = self.views[view_name]
            view.show()
            self.current_view = view_name
            
            # Update status
            self.status_var.set(f"View: {view_name.replace('_', ' ').title()}")
            
        except Exception as e:
            self.logger.error(f"Error showing view {view_name}: {e}")
            messagebox.showerror("Error", f"Could not load view: {e}")
    
    def _show_deck_builder(self):
        """Shows the deck builder"""
        self._show_view(DeckBuilderView, 'deck_builder')
    
    def _show_card_browser(self):
        """Shows the card browser"""
        self._show_view(CardBrowserView, 'card_browser')
    
    def _show_collection(self):
        """Shows the collection"""
        self._show_view(CollectionView, 'collection')
    
    def _new_deck(self):
        """Creates a new deck"""
        try:
            # Show deck builder
            self._show_deck_builder()
            
            # Create new deck in builder
            if 'deck_builder' in self.views:
                self.views['deck_builder'].new_deck()
            
            self.status_var.set("New deck created")
        except Exception as e:
            self.logger.error(f"Error creating new deck: {e}")
            messagebox.showerror("Error", f"Could not create deck: {e}")
    
    def _open_deck(self):
        """Opens an existing deck"""
        try:
            # Mostrar diálogo de selección
            decks_dir = Path(self.settings.decks_directory)
            file_path = filedialog.askopenfilename(
                title="Open Deck",
                initialdir=decks_dir,
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                # Show deck builder
                self._show_deck_builder()
                
                # Load deck in builder
                if 'deck_builder' in self.views:
                    filename = Path(file_path).name
                    success = self.views['deck_builder'].load_deck(filename)
                    
                    if success:
                        self.status_var.set(f"Deck loaded: {filename}")
                    else:
                        messagebox.showerror("Error", "Could not load deck")
        except Exception as e:
            self.logger.error(f"Error loading deck: {e}")
            messagebox.showerror("Error", f"Could not load deck: {e}")
    
    def _save_deck(self):
        """Saves the current deck"""
        try:
            if 'deck_builder' in self.views:
                success = self.views['deck_builder'].save_deck()
                if success:
                    self.status_var.set("Deck saved")
                else:
                    messagebox.showwarning("Warning", "Could not save the deck")
            else:
                messagebox.showinfo("Information", "No deck to save")
        except Exception as e:
            self.logger.error(f"Error saving deck: {e}")
            messagebox.showerror("Error", f"Could not save deck: {e}")
    
    def _save_deck_as(self):
        """Save the deck with a new name"""
        try:
            if 'deck_builder' in self.views:
                success = self.views['deck_builder'].save_deck_as()
                if success:
                    self.status_var.set("Deck saved with new name")
            else:
                messagebox.showinfo("Information", "No deck to save")
        except Exception as e:
            self.logger.error(f"Error saving deck as: {e}")
            messagebox.showerror("Error", f"Could not save deck: {e}")
    
    def _import_deck(self):
        """Import a deck from file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Import Deck",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                # Show deck builder
                self._show_deck_builder()
                
                # Import in builder
                if 'deck_builder' in self.views:
                    success = self.views['deck_builder'].import_deck(file_path)
                    if success:
                        self.status_var.set(f"Deck imported: {Path(file_path).name}")
        except Exception as e:
            self.logger.error(f"Error importing deck: {e}")
            messagebox.showerror("Error", f"Could not import deck: {e}")
    
    def _export_deck(self):
        """Export the current deck"""
        try:
            if 'deck_builder' in self.views:
                success = self.views['deck_builder'].export_deck()
                if success:
                    self.status_var.set("Deck exported")
            else:
                messagebox.showinfo("Information", "No deck to export")
        except Exception as e:
            self.logger.error(f"Error exporting deck: {e}")
            messagebox.showerror("Error", f"Could not export deck: {e}")
    
    def _analyze_deck(self):
        """Analyzes the current deck"""
        try:
            if 'deck_builder' in self.views:
                self.views['deck_builder'].analyze_deck()
            else:
                messagebox.showinfo("Information", "No deck to analyze")
        except Exception as e:
            self.logger.error(f"Error analyzing deck: {e}")
            messagebox.showerror("Error", f"Could not analyze deck: {e}")
    
    def _compare_with_collection(self):
        """Compares the deck with the collection"""
        try:
            if 'deck_builder' in self.views:
                self.views['deck_builder'].compare_with_collection()
            else:
                messagebox.showinfo("Information", "No deck to compare")
        except Exception as e:
            self.logger.error(f"Error comparing deck: {e}")
            messagebox.showerror("Error", f"Could not compare deck: {e}")
    
    def _clear_image_cache(self):
        """Clears the image cache"""
        try:
            result = messagebox.askyesno(
                "Confirm", 
                "Are you sure you want to clear the image cache?"
            )
            
            if result:
                self.app_controller.get_image_service().clear_cache()
                self.status_var.set("Image cache cleared")
                messagebox.showinfo("Information", "Image cache cleared successfully")
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            messagebox.showerror("Error", f"Could not clear cache: {e}")
    
    def _show_stats(self):
        """Shows application statistics"""
        try:
            stats = self.app_controller.get_application_stats()
            
            # Create statistics window
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Statistics")
            stats_window.geometry("400x300")
            stats_window.transient(self.root)
            stats_window.grab_set()
            
            # Contenido
            text_widget = tk.Text(stats_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            # Formatear estadísticas
            content = f"""APPLICATION STATISTICS

Application Information:
- Name: {stats.get('app_info', {}).get('name', 'N/A')}
- Version: {stats.get('app_info', {}).get('version', 'N/A')}

Collection:
- Total cards: {stats.get('collection_stats', {}).get('total_cards', 0)}
- Unique cards: {stats.get('collection_stats', {}).get('unique_cards', 0)}

Decks:
- Total decks: {stats.get('deck_stats', {}).get('total_decks', 0)}

Image Cache:
- Cached images: {stats.get('cache_stats', {}).get('cached_images', 0)}
- Cache size: {stats.get('cache_stats', {}).get('cache_size_mb', 0):.1f} MB"""
            
            text_widget.insert(tk.END, content)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Error showing statistics: {e}")
            messagebox.showerror("Error", f"Could not load statistics: {e}")
    
    def _show_preferences(self):
        """Shows the preferences window"""
        messagebox.showinfo("Information", "Preferences window not implemented yet")
    
    def _show_about(self):
        """Shows information about the application"""
        about_text = f"""{self.settings.app_name}
Version {self.settings.app_version}

Application for building and managing Magic: The Gathering decks.

Developed with Python and Tkinter."""
        
        messagebox.showinfo("About", about_text)
    
    def _refresh_current_view(self):
        """Refreshes the current view"""
        try:
            if self.current_view and self.current_view in self.views:
                view = self.views[self.current_view]
                if hasattr(view, 'refresh'):
                    view.refresh()
                self.status_var.set("View refreshed")
        except Exception as e:
            self.logger.error(f"Error refreshing view: {e}")
    
    def _update_status_info(self):
        """Updates the status bar information"""
        try:
            stats = self.app_controller.get_application_stats()
            collection_stats = stats.get('collection_stats', {})
            total_cards = collection_stats.get('total_cards', 0)
            unique_cards = collection_stats.get('unique_cards', 0)
            
            self.info_var.set(f"Collection: {total_cards} cards ({unique_cards} unique)")
            
            # Programar próxima actualización
            self.root.after(30000, self._update_status_info)  # Cada 30 segundos
        except Exception as e:
            self.logger.error(f"Error updating status information: {e}")
    
    def _on_closing(self):
        """Handles application closing"""
        try:
            # Ask if there are unsaved changes
            if 'deck_builder' in self.views:
                if hasattr(self.views['deck_builder'], 'has_unsaved_changes'):
                    if self.views['deck_builder'].has_unsaved_changes():
                        result = messagebox.askyesnocancel(
                            "Save changes",
                            "There are unsaved changes. Do you want to save them before exiting?"
                        )
                        
                        if result is True:  # Yes, save
                            if not self.views['deck_builder'].save_deck():
                                return  # Don't close if couldn't save
                        elif result is None:  # Cancel
                            return  # Don't close
            
            # Save window configurations
            if self.settings.get('ui.remember_window_size', True):
                self.settings.set('ui.window_width', self.root.winfo_width())
                self.settings.set('ui.window_height', self.root.winfo_height())
            
            # Close application
            self.app_controller.shutdown()
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error closing application: {e}")
            self.root.destroy()  # Force close
    
    def run(self):
        """Runs the application"""
        try:
            self.logger.info("Starting graphical interface")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Error in graphical interface: {e}")
            raise