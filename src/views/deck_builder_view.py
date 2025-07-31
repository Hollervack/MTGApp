"""Vista del constructor de mazos"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, List, Dict, Any

from ..controllers.app_controller import AppController
from ..models.deck import Deck
from ..models.card import Card


class DeckBuilderView:
    """Vista para construir y editar mazos"""
    
    def __init__(self, parent: tk.Widget, app_controller: AppController):
        self.parent = parent
        self.app_controller = app_controller
        self.logger = logging.getLogger('MTGDeckConstructor.DeckBuilderView')
        
        self.current_deck: Optional[Deck] = None
        self.frame = None
        
        self._create_interface()
    
    def _create_interface(self):
        """Crea la interfaz del constructor de mazos"""
        # Frame principal
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel superior - información del mazo
        self._create_deck_info_panel()
        
        # Panel central - lista de cartas y búsqueda
        self._create_main_panel()
        
        # Panel inferior - estadísticas
        self._create_stats_panel()
    
    def _create_deck_info_panel(self):
        """Crea el panel de información del mazo"""
        info_frame = ttk.LabelFrame(self.frame, text="Información del Mazo")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Nombre del mazo
        ttk.Label(info_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.deck_name_var = tk.StringVar(value="Nuevo Mazo")
        self.deck_name_entry = ttk.Entry(info_frame, textvariable=self.deck_name_var, width=30)
        self.deck_name_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Formato
        ttk.Label(info_frame, text="Formato:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.format_var = tk.StringVar(value="Standard")
        format_combo = ttk.Combobox(info_frame, textvariable=self.format_var, 
                                   values=["Standard", "Modern", "Legacy", "Vintage", "Commander", "Pioneer"])
        format_combo.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Descripción
        ttk.Label(info_frame, text="Descripción:").grid(row=1, column=0, sticky=tk.NW, padx=5, pady=5)
        self.description_text = tk.Text(info_frame, height=3, width=50)
        self.description_text.grid(row=1, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)
    
    def _create_main_panel(self):
        """Crea el panel principal con búsqueda y lista de cartas"""
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Panel izquierdo - búsqueda de cartas
        search_frame = ttk.LabelFrame(main_frame, text="Buscar Cartas")
        search_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Búsqueda
        ttk.Label(search_frame, text="Buscar:").pack(anchor=tk.W, padx=5, pady=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        search_entry.bind('<KeyRelease>', self._on_search_changed)
        
        # Lista de resultados de búsqueda
        search_list_frame = ttk.Frame(search_frame)
        search_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.search_listbox = tk.Listbox(search_list_frame)
        search_scrollbar = ttk.Scrollbar(search_list_frame, orient=tk.VERTICAL, command=self.search_listbox.yview)
        self.search_listbox.configure(yscrollcommand=search_scrollbar.set)
        
        self.search_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        search_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón agregar
        ttk.Button(search_frame, text="Agregar al Mazo", command=self._add_card_to_deck).pack(pady=5)
        
        # Panel derecho - cartas del mazo
        deck_frame = ttk.LabelFrame(main_frame, text="Cartas del Mazo")
        deck_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Lista de cartas del mazo
        deck_list_frame = ttk.Frame(deck_frame)
        deck_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.deck_listbox = tk.Listbox(deck_list_frame)
        deck_scrollbar = ttk.Scrollbar(deck_list_frame, orient=tk.VERTICAL, command=self.deck_listbox.yview)
        self.deck_listbox.configure(yscrollcommand=deck_scrollbar.set)
        
        self.deck_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        deck_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones del mazo
        buttons_frame = ttk.Frame(deck_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Quitar", command=self._remove_card_from_deck).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Editar Cantidad", command=self._edit_card_quantity).pack(side=tk.LEFT)
    
    def _create_stats_panel(self):
        """Crea el panel de estadísticas del mazo"""
        stats_frame = ttk.LabelFrame(self.frame, text="Estadísticas del Mazo")
        stats_frame.pack(fill=tk.X)
        
        # Estadísticas básicas
        self.total_cards_label = ttk.Label(stats_frame, text="Total de cartas: 0")
        self.total_cards_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.unique_cards_label = ttk.Label(stats_frame, text="Cartas únicas: 0")
        self.unique_cards_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.avg_cmc_label = ttk.Label(stats_frame, text="CMC promedio: 0.0")
        self.avg_cmc_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
    
    def _on_search_changed(self, event=None):
        """Maneja cambios en la búsqueda"""
        search_term = self.search_var.get().strip()
        if len(search_term) >= 2:
            try:
                results = self.app_controller.search_cards(search_term)
                self._update_search_results(results)
            except Exception as e:
                self.logger.error(f"Error en búsqueda: {e}")
    
    def _update_search_results(self, cards: List[Card]):
        """Actualiza la lista de resultados de búsqueda"""
        self.search_listbox.delete(0, tk.END)
        for card in cards[:50]:  # Limitar a 50 resultados
            self.search_listbox.insert(tk.END, card.display_name)
    
    def _add_card_to_deck(self):
        """Agrega una carta al mazo"""
        selection = self.search_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una carta para agregar")
            return
        
        # Por ahora, implementación básica
        card_name = self.search_listbox.get(selection[0])
        self.deck_listbox.insert(tk.END, f"1x {card_name}")
        self._update_stats()
    
    def _remove_card_from_deck(self):
        """Quita una carta del mazo"""
        selection = self.deck_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una carta para quitar")
            return
        
        self.deck_listbox.delete(selection[0])
        self._update_stats()
    
    def _edit_card_quantity(self):
        """Edita la cantidad de una carta"""
        # Implementación básica
        messagebox.showinfo("Info", "Función en desarrollo")
    
    def _update_stats(self):
        """Actualiza las estadísticas del mazo"""
        total_cards = self.deck_listbox.size()
        self.total_cards_label.config(text=f"Total de cartas: {total_cards}")
        self.unique_cards_label.config(text=f"Cartas únicas: {total_cards}")
        self.avg_cmc_label.config(text="CMC promedio: 0.0")
    
    def new_deck(self):
        """Crea un nuevo mazo"""
        self.current_deck = None
        self.deck_name_var.set("Nuevo Mazo")
        self.format_var.set("Standard")
        self.description_text.delete(1.0, tk.END)
        self.deck_listbox.delete(0, tk.END)
        self._update_stats()
    
    def load_deck(self, deck: Deck):
        """Carga un mazo en la vista"""
        self.current_deck = deck
        self.deck_name_var.set(deck.name)
        self.format_var.set(deck.format)
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(1.0, deck.description or "")
        
        # Cargar cartas
        self.deck_listbox.delete(0, tk.END)
        for card_name, quantity in deck.cards.items():
            self.deck_listbox.insert(tk.END, f"{quantity}x {card_name}")
        
        self._update_stats()
    
    def get_current_deck(self) -> Optional[Deck]:
        """Obtiene el mazo actual"""
        # Implementación básica
        return self.current_deck
    
    def show(self):
        """Muestra la vista"""
        if self.frame:
            self.frame.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """Oculta la vista"""
        if self.frame:
            self.frame.pack_forget()