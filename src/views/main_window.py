"""Ventana principal de la aplicación MTG Deck Constructor"""

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
    """Ventana principal de la aplicación"""
    
    def __init__(self, app_controller: AppController):
        self.app_controller = app_controller
        self.settings = app_controller.get_settings()
        self.logger = logging.getLogger('MTGDeckConstructor.MainWindow')
        
        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title(f"{self.settings.app_name} v{self.settings.app_version}")
        
        # Configurar ventana
        self._setup_window()
        self._create_menu()
        self._create_main_interface()
        self._setup_bindings()
        
        # Variables de estado
        self.current_view = None
        self.views = {}
        
        self.logger.info("Ventana principal inicializada")
    
    def _setup_window(self):
        """Configura la ventana principal"""
        # Tamaño y posición
        width, height = self.settings.window_size
        self.root.geometry(f"{width}x{height}")
        
        if self.settings.get('ui.window_resizable', True):
            self.root.resizable(True, True)
        else:
            self.root.resizable(False, False)
        
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configurar cierre
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Configurar estilo
        self.style = ttk.Style()
        theme = self.settings.get('ui.theme', 'default')
        if theme in self.style.theme_names():
            self.style.theme_use(theme)
    
    def _create_menu(self):
        """Crea la barra de menú"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo Mazo", command=self._new_deck, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir Mazo...", command=self._open_deck, accelerator="Ctrl+O")
        file_menu.add_command(label="Guardar Mazo", command=self._save_deck, accelerator="Ctrl+S")
        file_menu.add_command(label="Guardar Como...", command=self._save_deck_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Importar Mazo...", command=self._import_deck)
        file_menu.add_command(label="Exportar Mazo...", command=self._export_deck)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self._on_closing, accelerator="Ctrl+Q")
        
        # Menú Editar
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Buscar Cartas...", command=self._show_card_browser, accelerator="Ctrl+F")
        edit_menu.add_command(label="Colección", command=self._show_collection, accelerator="Ctrl+L")
        edit_menu.add_separator()
        edit_menu.add_command(label="Preferencias...", command=self._show_preferences)
        
        # Menú Ver
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Ver", menu=view_menu)
        view_menu.add_command(label="Constructor de Mazos", command=self._show_deck_builder)
        view_menu.add_command(label="Navegador de Cartas", command=self._show_card_browser)
        view_menu.add_command(label="Colección", command=self._show_collection)
        view_menu.add_separator()
        view_menu.add_command(label="Estadísticas", command=self._show_stats)
        
        # Menú Herramientas
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Analizar Mazo", command=self._analyze_deck)
        tools_menu.add_command(label="Comparar con Colección", command=self._compare_with_collection)
        tools_menu.add_command(label="Limpiar Caché de Imágenes", command=self._clear_image_cache)
        
        # Menú Ayuda
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de...", command=self._show_about)
    
    def _create_main_interface(self):
        """Crea la interfaz principal"""
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barra de herramientas
        self._create_toolbar()
        
        # Área de contenido principal
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Barra de estado
        self._create_status_bar()
        
        # Mostrar vista inicial
        self._show_deck_builder()
    
    def _create_toolbar(self):
        """Crea la barra de herramientas"""
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Botones principales
        ttk.Button(self.toolbar, text="Nuevo Mazo", command=self._new_deck).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.toolbar, text="Abrir", command=self._open_deck).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.toolbar, text="Guardar", command=self._save_deck).pack(side=tk.LEFT, padx=(0, 5))
        
        # Separador
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Botones de vista
        ttk.Button(self.toolbar, text="Constructor", command=self._show_deck_builder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.toolbar, text="Navegador", command=self._show_card_browser).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.toolbar, text="Colección", command=self._show_collection).pack(side=tk.LEFT, padx=(0, 5))
        
        # Separador
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Botones de análisis
        ttk.Button(self.toolbar, text="Analizar", command=self._analyze_deck).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.toolbar, text="Comparar", command=self._compare_with_collection).pack(side=tk.LEFT, padx=(0, 5))
    
    def _create_status_bar(self):
        """Crea la barra de estado"""
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Etiqueta de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Información adicional
        self.info_var = tk.StringVar()
        self.info_label = ttk.Label(self.status_frame, textvariable=self.info_var)
        self.info_label.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Actualizar información inicial
        self._update_status_info()
    
    def _setup_bindings(self):
        """Configura los atajos de teclado"""
        self.root.bind('<Control-n>', lambda e: self._new_deck())
        self.root.bind('<Control-o>', lambda e: self._open_deck())
        self.root.bind('<Control-s>', lambda e: self._save_deck())
        self.root.bind('<Control-Shift-S>', lambda e: self._save_deck_as())
        self.root.bind('<Control-f>', lambda e: self._show_card_browser())
        self.root.bind('<Control-l>', lambda e: self._show_collection())
        self.root.bind('<Control-q>', lambda e: self._on_closing())
        self.root.bind('<F5>', lambda e: self._refresh_current_view())
    
    def _show_view(self, view_class, view_name: str):
        """Muestra una vista específica"""
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
            
            # Mostrar vista
            view = self.views[view_name]
            view.show()
            self.current_view = view_name
            
            # Actualizar estado
            self.status_var.set(f"Vista: {view_name.replace('_', ' ').title()}")
            
        except Exception as e:
            self.logger.error(f"Error al mostrar vista {view_name}: {e}")
            messagebox.showerror("Error", f"No se pudo cargar la vista: {e}")
    
    def _show_deck_builder(self):
        """Muestra el constructor de mazos"""
        self._show_view(DeckBuilderView, 'deck_builder')
    
    def _show_card_browser(self):
        """Muestra el navegador de cartas"""
        self._show_view(CardBrowserView, 'card_browser')
    
    def _show_collection(self):
        """Muestra la vista de colección"""
        self._show_view(CollectionView, 'collection')
    
    def _new_deck(self):
        """Crea un nuevo mazo"""
        try:
            # Mostrar constructor de mazos
            self._show_deck_builder()
            
            # Crear nuevo mazo en el constructor
            if 'deck_builder' in self.views:
                self.views['deck_builder'].new_deck()
            
            self.status_var.set("Nuevo mazo creado")
        except Exception as e:
            self.logger.error(f"Error al crear nuevo mazo: {e}")
            messagebox.showerror("Error", f"No se pudo crear el mazo: {e}")
    
    def _open_deck(self):
        """Abre un mazo existente"""
        try:
            # Mostrar diálogo de selección
            decks_dir = Path(self.settings.decks_directory)
            file_path = filedialog.askopenfilename(
                title="Abrir Mazo",
                initialdir=decks_dir,
                filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
            )
            
            if file_path:
                # Mostrar constructor de mazos
                self._show_deck_builder()
                
                # Cargar mazo en el constructor
                if 'deck_builder' in self.views:
                    filename = Path(file_path).name
                    success = self.views['deck_builder'].load_deck(filename)
                    
                    if success:
                        self.status_var.set(f"Mazo cargado: {filename}")
                    else:
                        messagebox.showerror("Error", "No se pudo cargar el mazo")
        except Exception as e:
            self.logger.error(f"Error al abrir mazo: {e}")
            messagebox.showerror("Error", f"No se pudo abrir el mazo: {e}")
    
    def _save_deck(self):
        """Guarda el mazo actual"""
        try:
            if 'deck_builder' in self.views:
                success = self.views['deck_builder'].save_deck()
                if success:
                    self.status_var.set("Mazo guardado")
                else:
                    messagebox.showwarning("Advertencia", "No se pudo guardar el mazo")
            else:
                messagebox.showinfo("Información", "No hay mazo para guardar")
        except Exception as e:
            self.logger.error(f"Error al guardar mazo: {e}")
            messagebox.showerror("Error", f"No se pudo guardar el mazo: {e}")
    
    def _save_deck_as(self):
        """Guarda el mazo con un nuevo nombre"""
        try:
            if 'deck_builder' in self.views:
                success = self.views['deck_builder'].save_deck_as()
                if success:
                    self.status_var.set("Mazo guardado con nuevo nombre")
            else:
                messagebox.showinfo("Información", "No hay mazo para guardar")
        except Exception as e:
            self.logger.error(f"Error al guardar mazo como: {e}")
            messagebox.showerror("Error", f"No se pudo guardar el mazo: {e}")
    
    def _import_deck(self):
        """Importa un mazo desde archivo"""
        try:
            file_path = filedialog.askopenfilename(
                title="Importar Mazo",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
            )
            
            if file_path:
                # Mostrar constructor de mazos
                self._show_deck_builder()
                
                # Importar en el constructor
                if 'deck_builder' in self.views:
                    success = self.views['deck_builder'].import_deck(file_path)
                    if success:
                        self.status_var.set(f"Mazo importado: {Path(file_path).name}")
        except Exception as e:
            self.logger.error(f"Error al importar mazo: {e}")
            messagebox.showerror("Error", f"No se pudo importar el mazo: {e}")
    
    def _export_deck(self):
        """Exporta el mazo actual"""
        try:
            if 'deck_builder' in self.views:
                success = self.views['deck_builder'].export_deck()
                if success:
                    self.status_var.set("Mazo exportado")
            else:
                messagebox.showinfo("Información", "No hay mazo para exportar")
        except Exception as e:
            self.logger.error(f"Error al exportar mazo: {e}")
            messagebox.showerror("Error", f"No se pudo exportar el mazo: {e}")
    
    def _analyze_deck(self):
        """Analiza el mazo actual"""
        try:
            if 'deck_builder' in self.views:
                self.views['deck_builder'].analyze_deck()
            else:
                messagebox.showinfo("Información", "No hay mazo para analizar")
        except Exception as e:
            self.logger.error(f"Error al analizar mazo: {e}")
            messagebox.showerror("Error", f"No se pudo analizar el mazo: {e}")
    
    def _compare_with_collection(self):
        """Compara el mazo con la colección"""
        try:
            if 'deck_builder' in self.views:
                self.views['deck_builder'].compare_with_collection()
            else:
                messagebox.showinfo("Información", "No hay mazo para comparar")
        except Exception as e:
            self.logger.error(f"Error al comparar mazo: {e}")
            messagebox.showerror("Error", f"No se pudo comparar el mazo: {e}")
    
    def _clear_image_cache(self):
        """Limpia la caché de imágenes"""
        try:
            result = messagebox.askyesno(
                "Confirmar", 
                "¿Está seguro de que desea limpiar la caché de imágenes?"
            )
            
            if result:
                self.app_controller.get_image_service().clear_cache()
                self.status_var.set("Caché de imágenes limpiada")
                messagebox.showinfo("Información", "Caché de imágenes limpiada correctamente")
        except Exception as e:
            self.logger.error(f"Error al limpiar caché: {e}")
            messagebox.showerror("Error", f"No se pudo limpiar la caché: {e}")
    
    def _show_stats(self):
        """Muestra estadísticas de la aplicación"""
        try:
            stats = self.app_controller.get_application_stats()
            
            # Crear ventana de estadísticas
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Estadísticas")
            stats_window.geometry("400x300")
            stats_window.transient(self.root)
            stats_window.grab_set()
            
            # Contenido
            text_widget = tk.Text(stats_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            # Formatear estadísticas
            content = f"""ESTADÍSTICAS DE LA APLICACIÓN

Información de la Aplicación:
- Nombre: {stats.get('app_info', {}).get('name', 'N/A')}
- Versión: {stats.get('app_info', {}).get('version', 'N/A')}

Colección:
- Total de cartas: {stats.get('collection_stats', {}).get('total_cards', 0)}
- Cartas únicas: {stats.get('collection_stats', {}).get('unique_cards', 0)}

Mazos:
- Total de mazos: {stats.get('deck_stats', {}).get('total_decks', 0)}

Caché de Imágenes:
- Imágenes en caché: {stats.get('cache_stats', {}).get('cached_images', 0)}
- Tamaño de caché: {stats.get('cache_stats', {}).get('cache_size_mb', 0):.1f} MB"""
            
            text_widget.insert(tk.END, content)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Error al mostrar estadísticas: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar las estadísticas: {e}")
    
    def _show_preferences(self):
        """Muestra la ventana de preferencias"""
        messagebox.showinfo("Información", "Ventana de preferencias no implementada aún")
    
    def _show_about(self):
        """Muestra información sobre la aplicación"""
        about_text = f"""{self.settings.app_name}
Versión {self.settings.app_version}

Aplicación para construcción y gestión de mazos de Magic: The Gathering.

Desarrollado con Python y Tkinter."""
        
        messagebox.showinfo("Acerca de", about_text)
    
    def _refresh_current_view(self):
        """Actualiza la vista actual"""
        try:
            if self.current_view and self.current_view in self.views:
                view = self.views[self.current_view]
                if hasattr(view, 'refresh'):
                    view.refresh()
                self.status_var.set("Vista actualizada")
        except Exception as e:
            self.logger.error(f"Error al actualizar vista: {e}")
    
    def _update_status_info(self):
        """Actualiza la información de la barra de estado"""
        try:
            stats = self.app_controller.get_application_stats()
            collection_stats = stats.get('collection_stats', {})
            total_cards = collection_stats.get('total_cards', 0)
            unique_cards = collection_stats.get('unique_cards', 0)
            
            self.info_var.set(f"Colección: {total_cards} cartas ({unique_cards} únicas)")
            
            # Programar próxima actualización
            self.root.after(30000, self._update_status_info)  # Cada 30 segundos
        except Exception as e:
            self.logger.error(f"Error al actualizar información de estado: {e}")
    
    def _on_closing(self):
        """Maneja el cierre de la aplicación"""
        try:
            # Preguntar si hay cambios sin guardar
            if 'deck_builder' in self.views:
                if hasattr(self.views['deck_builder'], 'has_unsaved_changes'):
                    if self.views['deck_builder'].has_unsaved_changes():
                        result = messagebox.askyesnocancel(
                            "Guardar cambios",
                            "Hay cambios sin guardar. ¿Desea guardarlos antes de salir?"
                        )
                        
                        if result is True:  # Sí, guardar
                            if not self.views['deck_builder'].save_deck():
                                return  # No cerrar si no se pudo guardar
                        elif result is None:  # Cancelar
                            return  # No cerrar
            
            # Guardar configuraciones de ventana
            if self.settings.get('ui.remember_window_size', True):
                self.settings.set('ui.window_width', self.root.winfo_width())
                self.settings.set('ui.window_height', self.root.winfo_height())
            
            # Cerrar aplicación
            self.app_controller.shutdown()
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error al cerrar aplicación: {e}")
            self.root.destroy()  # Forzar cierre
    
    def run(self):
        """Ejecuta la aplicación"""
        try:
            self.logger.info("Iniciando interfaz gráfica")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Error en la interfaz gráfica: {e}")
            raise