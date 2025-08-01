"""Deck builder view"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, List, Dict, Any

from ..controllers.app_controller import AppController
from ..models.deck import Deck
from ..models.card import Card


class DeckBuilderView:
    """View for building and editing decks"""
    
    def __init__(self, parent: tk.Widget, app_controller: AppController):
        self.parent = parent
        self.app_controller = app_controller
        self.logger = logging.getLogger('MTGDeckConstructor.DeckBuilderView')
        
        self.current_deck: Optional[Deck] = None
        self.frame = None
        
        self._create_interface()
    
    def _create_interface(self):
        """Creates the deck builder interface"""
        # Main frame
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top panel - deck information
        self._create_deck_info_panel()
        
        # Central panel - card list and search
        self._create_main_panel()
        
        # Bottom panel - statistics
        self._create_stats_panel()
    
    def _create_deck_info_panel(self):
        """Creates the deck information panel"""
        info_frame = ttk.LabelFrame(self.frame, text="Deck Information")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Deck name
        ttk.Label(info_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.deck_name_var = tk.StringVar(value="New Deck")
        self.deck_name_entry = ttk.Entry(info_frame, textvariable=self.deck_name_var, width=30)
        self.deck_name_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Format
        ttk.Label(info_frame, text="Format:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.format_var = tk.StringVar(value="Standard")
        format_combo = ttk.Combobox(info_frame, textvariable=self.format_var, 
                                   values=["Standard", "Modern", "Legacy", "Vintage", "Commander", "Pioneer"])
        format_combo.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Description
        ttk.Label(info_frame, text="Description:").grid(row=1, column=0, sticky=tk.NW, padx=5, pady=5)
        self.description_text = tk.Text(info_frame, height=3, width=50)
        self.description_text.grid(row=1, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)
    
    def _create_main_panel(self):
        """Creates the main panel with search and card list"""
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Left panel - card search
        search_frame = ttk.LabelFrame(main_frame, text="Search Cards")
        search_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Search
        ttk.Label(search_frame, text="Search:").pack(anchor=tk.W, padx=5, pady=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        search_entry.bind('<KeyRelease>', self._on_search_changed)
        
        # Search results list
        search_list_frame = ttk.Frame(search_frame)
        search_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.search_listbox = tk.Listbox(search_list_frame)
        search_scrollbar = ttk.Scrollbar(search_list_frame, orient=tk.VERTICAL, command=self.search_listbox.yview)
        self.search_listbox.configure(yscrollcommand=search_scrollbar.set)
        
        self.search_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        search_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add button
        ttk.Button(search_frame, text="Add to Deck", command=self._add_card_to_deck).pack(pady=5)
        
        # Right panel - deck cards
        deck_frame = ttk.LabelFrame(main_frame, text="Deck Cards")
        deck_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Deck cards list
        deck_list_frame = ttk.Frame(deck_frame)
        deck_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.deck_listbox = tk.Listbox(deck_list_frame)
        deck_scrollbar = ttk.Scrollbar(deck_list_frame, orient=tk.VERTICAL, command=self.deck_listbox.yview)
        self.deck_listbox.configure(yscrollcommand=deck_scrollbar.set)
        
        self.deck_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        deck_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Deck buttons
        buttons_frame = ttk.Frame(deck_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Remove", command=self._remove_card_from_deck).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Edit Quantity", command=self._edit_card_quantity).pack(side=tk.LEFT)
    
    def _create_stats_panel(self):
        """Creates the deck statistics panel"""
        stats_frame = ttk.LabelFrame(self.frame, text="Deck Statistics")
        stats_frame.pack(fill=tk.X)
        
        # Basic statistics
        self.total_cards_label = ttk.Label(stats_frame, text="Total cards: 0")
        self.total_cards_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.unique_cards_label = ttk.Label(stats_frame, text="Unique cards: 0")
        self.unique_cards_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.avg_cmc_label = ttk.Label(stats_frame, text="Average CMC: 0.0")
        self.avg_cmc_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
    
    def _on_search_changed(self, event=None):
        """Handles search changes"""
        search_term = self.search_var.get().strip()
        if len(search_term) >= 2:
            try:
                results = self.app_controller.search_cards(search_term)
                self._update_search_results(results)
            except Exception as e:
                self.logger.error(f"Search error: {e}")
    
    def _update_search_results(self, cards: List[Card]):
        """Updates the search results list"""
        self.search_listbox.delete(0, tk.END)
        for card in cards[:50]:  # Limit to 50 results
            self.search_listbox.insert(tk.END, card.display_name)
    
    def _add_card_to_deck(self):
        """Adds a card to the deck"""
        selection = self.search_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a card to add")
            return
        
        # Basic implementation for now
        card_name = self.search_listbox.get(selection[0])
        self.deck_listbox.insert(tk.END, f"1x {card_name}")
        self._update_stats()
    
    def _remove_card_from_deck(self):
        """Removes a card from the deck"""
        selection = self.deck_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a card to remove")
            return
        
        self.deck_listbox.delete(selection[0])
        self._update_stats()
    
    def _edit_card_quantity(self):
        """Edits the quantity of a card"""
        # Basic implementation
        messagebox.showinfo("Info", "Function under development")
    
    def _update_stats(self):
        """Updates the deck statistics"""
        total_cards = self.deck_listbox.size()
        self.total_cards_label.config(text=f"Total cards: {total_cards}")
        self.unique_cards_label.config(text=f"Unique cards: {total_cards}")
        self.avg_cmc_label.config(text="Average CMC: 0.0")
    
    def new_deck(self):
        """Creates a new deck"""
        self.current_deck = None
        self.deck_name_var.set("New Deck")
        self.format_var.set("Standard")
        self.description_text.delete(1.0, tk.END)
        self.deck_listbox.delete(0, tk.END)
        self._update_stats()
    
    def load_deck(self, deck: Deck):
        """Loads a deck into the view"""
        self.current_deck = deck
        self.deck_name_var.set(deck.name)
        self.format_var.set(deck.format)
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(1.0, deck.description or "")
        
        # Load cards
        self.deck_listbox.delete(0, tk.END)
        for card_name, quantity in deck.cards.items():
            self.deck_listbox.insert(tk.END, f"{quantity}x {card_name}")
        
        self._update_stats()
    
    def get_current_deck(self) -> Optional[Deck]:
        """Gets the current deck"""
        # Basic implementation
        return self.current_deck
    
    def show(self):
        """Shows the view"""
        if self.frame:
            self.frame.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """Hides the view"""
        if self.frame:
            self.frame.pack_forget()