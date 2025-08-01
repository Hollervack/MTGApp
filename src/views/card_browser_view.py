"""Card browser view"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import List, Dict, Any, Optional

from ..controllers.app_controller import AppController
from ..models.card import Card


class CardBrowserView:
    """View for browsing and searching cards"""
    
    def __init__(self, parent: tk.Widget, app_controller: AppController):
        self.parent = parent
        self.app_controller = app_controller
        self.logger = logging.getLogger('MTGDeckConstructor.CardBrowserView')
        
        self.current_cards: List[Card] = []
        self.frame = None
        
        self._create_interface()
        self._load_initial_cards()
    
    def _create_interface(self):
        """Creates the card browser interface"""
        # Frame principal
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel superior - filtros y búsqueda
        self._create_search_panel()
        
        # Central panel - card list
        self._create_cards_panel()
        
        # Bottom panel - card details
        self._create_details_panel()
    
    def _create_search_panel(self):
        """Creates the search and filters panel"""
        search_frame = ttk.LabelFrame(self.frame, text="Search and Filters")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # First row - main search
        row1_frame = ttk.Frame(search_frame)
        row1_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row1_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(row1_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind('<KeyRelease>', self._on_search_changed)
        
        ttk.Button(row1_frame, text="Search", command=self._perform_search).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(row1_frame, text="Clear", command=self._clear_search).pack(side=tk.LEFT)
        
        # Second row - filters
        row2_frame = ttk.Frame(search_frame)
        row2_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Color filter
        ttk.Label(row2_frame, text="Color:").pack(side=tk.LEFT, padx=(0, 5))
        self.color_var = tk.StringVar(value="All")
        color_combo = ttk.Combobox(row2_frame, textvariable=self.color_var, width=15,
                                  values=["All", "White", "Blue", "Black", "Red", "Green", "Colorless", "Multicolor"])
        color_combo.pack(side=tk.LEFT, padx=(0, 10))
        color_combo.bind('<<ComboboxSelected>>', self._on_filter_changed)
        
        # Type filter
        ttk.Label(row2_frame, text="Type:").pack(side=tk.LEFT, padx=(0, 5))
        self.type_var = tk.StringVar(value="All")
        type_combo = ttk.Combobox(row2_frame, textvariable=self.type_var, width=15,
                                 values=["All", "Creature", "Instant", "Sorcery", "Enchantment", "Artifact", "Planeswalker", "Land"])
        type_combo.pack(side=tk.LEFT, padx=(0, 10))
        type_combo.bind('<<ComboboxSelected>>', self._on_filter_changed)
        
        # Rarity filter
        ttk.Label(row2_frame, text="Rarity:").pack(side=tk.LEFT, padx=(0, 5))
        self.rarity_var = tk.StringVar(value="All")
        rarity_combo = ttk.Combobox(row2_frame, textvariable=self.rarity_var, width=15,
                                   values=["All", "Common", "Uncommon", "Rare", "Mythic"])
        rarity_combo.pack(side=tk.LEFT, padx=(0, 10))
        rarity_combo.bind('<<ComboboxSelected>>', self._on_filter_changed)
    
    def _create_cards_panel(self):
        """Creates the card list panel"""
        cards_frame = ttk.LabelFrame(self.frame, text="Cards")
        cards_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create Treeview to display cards
        tree_frame = ttk.Frame(cards_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure columns
        columns = ('name', 'mana_cost', 'type', 'rarity', 'set')
        self.cards_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure headers
        self.cards_tree.heading('name', text='Name')
        self.cards_tree.heading('mana_cost', text='Mana Cost')
        self.cards_tree.heading('type', text='Type')
        self.cards_tree.heading('rarity', text='Rarity')
        self.cards_tree.heading('set', text='Set')
        
        # Configure column widths
        self.cards_tree.column('name', width=200)
        self.cards_tree.column('mana_cost', width=100)
        self.cards_tree.column('type', width=150)
        self.cards_tree.column('rarity', width=100)
        self.cards_tree.column('set', width=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.cards_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.cards_tree.xview)
        self.cards_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack
        self.cards_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.cards_tree.bind('<<TreeviewSelect>>', self._on_card_selected)
        self.cards_tree.bind('<Double-1>', self._on_card_double_click)
        
        # Frame for results information
        info_frame = ttk.Frame(cards_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.results_label = ttk.Label(info_frame, text="Cards found: 0")
        self.results_label.pack(side=tk.LEFT)
    
    def _create_details_panel(self):
        """Creates the card details panel"""
        details_frame = ttk.LabelFrame(self.frame, text="Card Details")
        details_frame.pack(fill=tk.X)
        
        # Frame for image and text
        content_frame = ttk.Frame(details_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left frame for image
        image_frame = ttk.Frame(content_frame)
        image_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.card_image_label = ttk.Label(image_frame, text="Card image\n(Not available)")
        self.card_image_label.pack()
        
        # Right frame for details
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.details_text = tk.Text(text_frame, height=8, width=50, wrap=tk.WORD)
        details_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)
        
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _load_initial_cards(self):
        """Loads initial cards"""
        try:
            # Load all cards (limited for performance)
            all_cards = self.app_controller.get_all_cards()[:1000]  # Limit to 1000
            self._update_cards_display(all_cards)
        except Exception as e:
            self.logger.error(f"Error loading initial cards: {e}")
            messagebox.showerror("Error", f"Error loading cards: {e}")
    
    def _on_search_changed(self, event=None):
        """Handles real-time changes in search"""
        # Real-time search only if there are more than 2 characters
        search_term = self.search_var.get().strip()
        if len(search_term) >= 3:
            self._perform_search()
    
    def _perform_search(self):
        """Performs card search"""
        try:
            search_term = self.search_var.get().strip()
            if not search_term:
                self._load_initial_cards()
                return
            
            results = self.app_controller.search_cards(search_term)
            self._apply_filters(results)
            
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            messagebox.showerror("Error", f"Search error: {e}")
    
    def _on_filter_changed(self, event=None):
        """Handles filter changes"""
        # Apply filters to current cards
        if hasattr(self, 'current_cards'):
            self._apply_filters(self.current_cards)
    
    def _apply_filters(self, cards: List[Card]):
        """Applies selected filters to the card list"""
        filtered_cards = cards.copy()
        
        # Color filter
        color_filter = self.color_var.get()
        if color_filter != "All":
            # Basic color filter implementation
            pass  # TODO: Implement color filter
        
        # Type filter
        type_filter = self.type_var.get()
        if type_filter != "All":
            # Basic type filter implementation
            pass  # TODO: Implement type filter
        
        # Rarity filter
        rarity_filter = self.rarity_var.get()
        if rarity_filter != "All":
            # Basic rarity filter implementation
            pass  # TODO: Implement rarity filter
        
        self._update_cards_display(filtered_cards)
    
    def _update_cards_display(self, cards: List[Card]):
        """Updates the card display"""
        # Clear tree
        for item in self.cards_tree.get_children():
            self.cards_tree.delete(item)
        
        # Add cards
        self.current_cards = cards
        for card in cards:
            self.cards_tree.insert('', tk.END, values=(
                card.card_name,
                getattr(card, 'mana_cost', ''),
                getattr(card, 'type_line', ''),
                getattr(card, 'rarity', ''),
                getattr(card, 'set_code', '')
            ))
        
        # Update counter
        self.results_label.config(text=f"Cards found: {len(cards)}")
    
    def _on_card_selected(self, event=None):
        """Handles card selection"""
        selection = self.cards_tree.selection()
        if not selection:
            return
        
        # Get selected card data
        item = self.cards_tree.item(selection[0])
        card_name = item['values'][0]
        
        # Search for the card in current list
        selected_card = None
        for card in self.current_cards:
            if card.card_name == card_name:
                selected_card = card
                break
        
        if selected_card:
            self._show_card_details(selected_card)
    
    def _on_card_double_click(self, event=None):
        """Handles double click on a card"""
        # Implement double click action (e.g.: add to deck)
        messagebox.showinfo("Info", "Function under development: Add to deck")
    
    def _show_card_details(self, card: Card):
        """Shows card details"""
        # Clear previous text
        self.details_text.delete(1.0, tk.END)
        
        # Show card information
        details = f"Name: {card.card_name}\n"
        details += f"Mana Cost: {getattr(card, 'mana_cost', 'N/A')}\n"
        details += f"Type: {getattr(card, 'type_line', 'N/A')}\n"
        details += f"Rarity: {getattr(card, 'rarity', 'N/A')}\n"
        details += f"Set: {getattr(card, 'set_code', 'N/A')}\n\n"
        
        if hasattr(card, 'oracle_text'):
            details += f"Text: {card.oracle_text}\n\n"
        
        if hasattr(card, 'power') and hasattr(card, 'toughness'):
            details += f"Power/Toughness: {card.power}/{card.toughness}\n"
        
        self.details_text.insert(1.0, details)
        
        # TODO: Load card image
        self.card_image_label.config(text=f"Image of\n{card.card_name}\n(Not available)")
    
    def _clear_search(self):
        """Clears search and filters"""
        self.search_var.set("")
        self.color_var.set("Todos")
        self.type_var.set("Todos")
        self.rarity_var.set("Todas")
        self._load_initial_cards()
    
    def show(self):
        """Shows the view"""
        if self.frame:
            self.frame.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """Hides the view"""
        if self.frame:
            self.frame.pack_forget()
    
    def refresh(self):
        """Refresca la vista"""
        self._load_initial_cards()