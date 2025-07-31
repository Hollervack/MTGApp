"""Vista del navegador de cartas"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import List, Dict, Any, Optional

from ..controllers.app_controller import AppController
from ..models.card import Card


class CardBrowserView:
    """Vista para navegar y buscar cartas"""
    
    def __init__(self, parent: tk.Widget, app_controller: AppController):
        self.parent = parent
        self.app_controller = app_controller
        self.logger = logging.getLogger('MTGDeckConstructor.CardBrowserView')
        
        self.current_cards: List[Card] = []
        self.frame = None
        
        self._create_interface()
        self._load_initial_cards()
    
    def _create_interface(self):
        """Crea la interfaz del navegador de cartas"""
        # Frame principal
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel superior - filtros y búsqueda
        self._create_search_panel()
        
        # Panel central - lista de cartas
        self._create_cards_panel()
        
        # Panel inferior - detalles de carta
        self._create_details_panel()
    
    def _create_search_panel(self):
        """Crea el panel de búsqueda y filtros"""
        search_frame = ttk.LabelFrame(self.frame, text="Búsqueda y Filtros")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Primera fila - búsqueda principal
        row1_frame = ttk.Frame(search_frame)
        row1_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row1_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(row1_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind('<KeyRelease>', self._on_search_changed)
        
        ttk.Button(row1_frame, text="Buscar", command=self._perform_search).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(row1_frame, text="Limpiar", command=self._clear_search).pack(side=tk.LEFT)
        
        # Segunda fila - filtros
        row2_frame = ttk.Frame(search_frame)
        row2_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Filtro por color
        ttk.Label(row2_frame, text="Color:").pack(side=tk.LEFT, padx=(0, 5))
        self.color_var = tk.StringVar(value="Todos")
        color_combo = ttk.Combobox(row2_frame, textvariable=self.color_var, width=15,
                                  values=["Todos", "Blanco", "Azul", "Negro", "Rojo", "Verde", "Incoloro", "Multicolor"])
        color_combo.pack(side=tk.LEFT, padx=(0, 10))
        color_combo.bind('<<ComboboxSelected>>', self._on_filter_changed)
        
        # Filtro por tipo
        ttk.Label(row2_frame, text="Tipo:").pack(side=tk.LEFT, padx=(0, 5))
        self.type_var = tk.StringVar(value="Todos")
        type_combo = ttk.Combobox(row2_frame, textvariable=self.type_var, width=15,
                                 values=["Todos", "Criatura", "Instantáneo", "Conjuro", "Encantamiento", "Artefacto", "Planeswalker", "Tierra"])
        type_combo.pack(side=tk.LEFT, padx=(0, 10))
        type_combo.bind('<<ComboboxSelected>>', self._on_filter_changed)
        
        # Filtro por rareza
        ttk.Label(row2_frame, text="Rareza:").pack(side=tk.LEFT, padx=(0, 5))
        self.rarity_var = tk.StringVar(value="Todas")
        rarity_combo = ttk.Combobox(row2_frame, textvariable=self.rarity_var, width=15,
                                   values=["Todas", "Común", "Poco común", "Rara", "Mítica"])
        rarity_combo.pack(side=tk.LEFT, padx=(0, 10))
        rarity_combo.bind('<<ComboboxSelected>>', self._on_filter_changed)
    
    def _create_cards_panel(self):
        """Crea el panel de lista de cartas"""
        cards_frame = ttk.LabelFrame(self.frame, text="Cartas")
        cards_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Crear Treeview para mostrar cartas
        tree_frame = ttk.Frame(cards_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configurar columnas
        columns = ('name', 'mana_cost', 'type', 'rarity', 'set')
        self.cards_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configurar encabezados
        self.cards_tree.heading('name', text='Nombre')
        self.cards_tree.heading('mana_cost', text='Coste de Maná')
        self.cards_tree.heading('type', text='Tipo')
        self.cards_tree.heading('rarity', text='Rareza')
        self.cards_tree.heading('set', text='Set')
        
        # Configurar anchos de columna
        self.cards_tree.column('name', width=200)
        self.cards_tree.column('mana_cost', width=100)
        self.cards_tree.column('type', width=150)
        self.cards_tree.column('rarity', width=100)
        self.cards_tree.column('set', width=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.cards_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.cards_tree.xview)
        self.cards_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Empaquetar
        self.cards_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind eventos
        self.cards_tree.bind('<<TreeviewSelect>>', self._on_card_selected)
        self.cards_tree.bind('<Double-1>', self._on_card_double_click)
        
        # Frame para información de resultados
        info_frame = ttk.Frame(cards_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.results_label = ttk.Label(info_frame, text="Cartas encontradas: 0")
        self.results_label.pack(side=tk.LEFT)
    
    def _create_details_panel(self):
        """Crea el panel de detalles de carta"""
        details_frame = ttk.LabelFrame(self.frame, text="Detalles de la Carta")
        details_frame.pack(fill=tk.X)
        
        # Frame para imagen y texto
        content_frame = ttk.Frame(details_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame izquierdo para imagen
        image_frame = ttk.Frame(content_frame)
        image_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.card_image_label = ttk.Label(image_frame, text="Imagen de carta\n(No disponible)")
        self.card_image_label.pack()
        
        # Frame derecho para detalles
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.details_text = tk.Text(text_frame, height=8, width=50, wrap=tk.WORD)
        details_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)
        
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _load_initial_cards(self):
        """Carga las cartas iniciales"""
        try:
            # Cargar todas las cartas (limitado para rendimiento)
            all_cards = self.app_controller.get_all_cards()[:1000]  # Limitar a 1000
            self._update_cards_display(all_cards)
        except Exception as e:
            self.logger.error(f"Error cargando cartas iniciales: {e}")
            messagebox.showerror("Error", f"Error cargando cartas: {e}")
    
    def _on_search_changed(self, event=None):
        """Maneja cambios en tiempo real en la búsqueda"""
        # Búsqueda en tiempo real solo si hay más de 2 caracteres
        search_term = self.search_var.get().strip()
        if len(search_term) >= 3:
            self._perform_search()
    
    def _perform_search(self):
        """Realiza la búsqueda de cartas"""
        try:
            search_term = self.search_var.get().strip()
            if not search_term:
                self._load_initial_cards()
                return
            
            results = self.app_controller.search_cards(search_term)
            self._apply_filters(results)
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda: {e}")
            messagebox.showerror("Error", f"Error en búsqueda: {e}")
    
    def _on_filter_changed(self, event=None):
        """Maneja cambios en los filtros"""
        # Aplicar filtros a las cartas actuales
        if hasattr(self, 'current_cards'):
            self._apply_filters(self.current_cards)
    
    def _apply_filters(self, cards: List[Card]):
        """Aplica los filtros seleccionados a la lista de cartas"""
        filtered_cards = cards.copy()
        
        # Filtro por color
        color_filter = self.color_var.get()
        if color_filter != "Todos":
            # Implementación básica del filtro de color
            pass  # TODO: Implementar filtro de color
        
        # Filtro por tipo
        type_filter = self.type_var.get()
        if type_filter != "Todos":
            # Implementación básica del filtro de tipo
            pass  # TODO: Implementar filtro de tipo
        
        # Filtro por rareza
        rarity_filter = self.rarity_var.get()
        if rarity_filter != "Todas":
            # Implementación básica del filtro de rareza
            pass  # TODO: Implementar filtro de rareza
        
        self._update_cards_display(filtered_cards)
    
    def _update_cards_display(self, cards: List[Card]):
        """Actualiza la visualización de cartas"""
        # Limpiar árbol
        for item in self.cards_tree.get_children():
            self.cards_tree.delete(item)
        
        # Agregar cartas
        self.current_cards = cards
        for card in cards:
            self.cards_tree.insert('', tk.END, values=(
                card.card_name,
                getattr(card, 'mana_cost', ''),
                getattr(card, 'type_line', ''),
                getattr(card, 'rarity', ''),
                getattr(card, 'set_code', '')
            ))
        
        # Actualizar contador
        self.results_label.config(text=f"Cartas encontradas: {len(cards)}")
    
    def _on_card_selected(self, event=None):
        """Maneja la selección de una carta"""
        selection = self.cards_tree.selection()
        if not selection:
            return
        
        # Obtener datos de la carta seleccionada
        item = self.cards_tree.item(selection[0])
        card_name = item['values'][0]
        
        # Buscar la carta en la lista actual
        selected_card = None
        for card in self.current_cards:
            if card.card_name == card_name:
                selected_card = card
                break
        
        if selected_card:
            self._show_card_details(selected_card)
    
    def _on_card_double_click(self, event=None):
        """Maneja doble clic en una carta"""
        # Implementar acción de doble clic (ej: agregar a mazo)
        messagebox.showinfo("Info", "Función en desarrollo: Agregar a mazo")
    
    def _show_card_details(self, card: Card):
        """Muestra los detalles de una carta"""
        # Limpiar texto anterior
        self.details_text.delete(1.0, tk.END)
        
        # Mostrar información de la carta
        details = f"Nombre: {card.card_name}\n"
        details += f"Coste de Maná: {getattr(card, 'mana_cost', 'N/A')}\n"
        details += f"Tipo: {getattr(card, 'type_line', 'N/A')}\n"
        details += f"Rareza: {getattr(card, 'rarity', 'N/A')}\n"
        details += f"Set: {getattr(card, 'set_code', 'N/A')}\n\n"
        
        if hasattr(card, 'oracle_text'):
            details += f"Texto: {card.oracle_text}\n\n"
        
        if hasattr(card, 'power') and hasattr(card, 'toughness'):
            details += f"Fuerza/Resistencia: {card.power}/{card.toughness}\n"
        
        self.details_text.insert(1.0, details)
        
        # TODO: Cargar imagen de la carta
        self.card_image_label.config(text=f"Imagen de\n{card.card_name}\n(No disponible)")
    
    def _clear_search(self):
        """Limpia la búsqueda y filtros"""
        self.search_var.set("")
        self.color_var.set("Todos")
        self.type_var.set("Todos")
        self.rarity_var.set("Todas")
        self._load_initial_cards()
    
    def show(self):
        """Muestra la vista"""
        if self.frame:
            self.frame.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """Oculta la vista"""
        if self.frame:
            self.frame.pack_forget()
    
    def refresh(self):
        """Refresca la vista"""
        self._load_initial_cards()