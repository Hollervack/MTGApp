"""Card collection view"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import logging
from typing import List, Dict, Any, Optional

from ..controllers.app_controller import AppController
from ..models.card import Card


class CollectionView:
    """View for managing the user's card collection"""
    
    def __init__(self, parent: tk.Widget, app_controller: AppController):
        self.parent = parent
        self.app_controller = app_controller
        self.logger = logging.getLogger('MTGDeckConstructor.CollectionView')
        
        self.collection_cards: Dict[str, int] = {}  # card_name -> quantity
        self.frame = None
        
        self._create_interface()
        self._load_collection()
    
    def _create_interface(self):
        """Creates the main interface"""
        # Main frame
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel superior - herramientas
        self._create_tools_panel()
        
        # Panel central - lista de cartas de la colección
        self._create_collection_panel()
        
        # Panel inferior - estadísticas
        self._create_stats_panel()
    
    def _create_tools_panel(self):
        """Crea el panel de herramientas"""
        tools_frame = ttk.LabelFrame(self.frame, text="Collection Tools")
        tools_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Tool buttons
        row1_frame = ttk.Frame(tools_frame)
        row1_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(row1_frame, text="Import Collection", command=self._import_collection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1_frame, text="Export Collection", command=self._export_collection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1_frame, text="Clear Collection", command=self._clear_collection).pack(side=tk.LEFT, padx=(0, 10))
        
        # Separador
        ttk.Separator(row1_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Search
        ttk.Label(row1_frame, text="Search in collection:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(row1_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind('<KeyRelease>', self._on_search_changed)
        
        ttk.Button(row1_frame, text="Search", command=self._search_collection).pack(side=tk.LEFT)
        
        # Second row - add cards
        row2_frame = ttk.Frame(tools_frame)
        row2_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row2_frame, text="Add card:").pack(side=tk.LEFT, padx=(0, 5))
        self.add_card_var = tk.StringVar()
        add_card_entry = ttk.Entry(row2_frame, textvariable=self.add_card_var, width=25)
        add_card_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(row2_frame, text="Quantity:").pack(side=tk.LEFT, padx=(5, 5))
        self.quantity_var = tk.StringVar(value="1")
        quantity_spin = ttk.Spinbox(row2_frame, from_=1, to=99, textvariable=self.quantity_var, width=5)
        quantity_spin.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(row2_frame, text="Add", command=self._add_card_to_collection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row2_frame, text="Remove", command=self._remove_card_from_collection).pack(side=tk.LEFT)
    
    def _create_collection_panel(self):
        """Creates the collection panel"""
        collection_frame = ttk.LabelFrame(self.frame, text="My Collection")
        collection_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create Treeview to display collection
        tree_frame = ttk.Frame(collection_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure columns
        columns = ('quantity', 'name', 'mana_cost', 'type', 'rarity', 'set', 'value')
        self.collection_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Configure headers
        self.collection_tree.heading('quantity', text='Qty.')
        self.collection_tree.heading('name', text='Name')
        self.collection_tree.heading('mana_cost', text='Cost')
        self.collection_tree.heading('type', text='Type')
        self.collection_tree.heading('rarity', text='Rarity')
        self.collection_tree.heading('set', text='Set')
        self.collection_tree.heading('value', text='Value')
        
        # Configure column widths
        self.collection_tree.column('quantity', width=50)
        self.collection_tree.column('name', width=200)
        self.collection_tree.column('mana_cost', width=80)
        self.collection_tree.column('type', width=120)
        self.collection_tree.column('rarity', width=80)
        self.collection_tree.column('set', width=60)
        self.collection_tree.column('value', width=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.collection_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.collection_tree.xview)
        self.collection_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Empaquetar
        self.collection_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind eventos
        self.collection_tree.bind('<<TreeviewSelect>>', self._on_card_selected)
        self.collection_tree.bind('<Double-1>', self._on_card_double_click)
        
        # Action buttons
        actions_frame = ttk.Frame(collection_frame)
        actions_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Button(actions_frame, text="Edit Quantity", command=self._edit_quantity).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="View Details", command=self._view_card_details).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="Delete", command=self._remove_selected_card).pack(side=tk.LEFT)
    
    def _create_stats_panel(self):
        """Creates the statistics panel"""
        stats_frame = ttk.LabelFrame(self.frame, text="Estadísticas de la Colección")
        stats_frame.pack(fill=tk.X)
        
        # Frame para estadísticas
        stats_content = ttk.Frame(stats_frame)
        stats_content.pack(fill=tk.X, padx=5, pady=5)
        
        # Primera fila de estadísticas
        row1_stats = ttk.Frame(stats_content)
        row1_stats.pack(fill=tk.X, pady=(0, 5))
        
        self.total_cards_label = ttk.Label(row1_stats, text="Total cards: 0")
        self.total_cards_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.unique_cards_label = ttk.Label(row1_stats, text="Unique cards: 0")
        self.unique_cards_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.total_value_label = ttk.Label(row1_stats, text="Total value: $0.00")
        self.total_value_label.pack(side=tk.LEFT)
        
        # Segunda fila de estadísticas
        row2_stats = ttk.Frame(stats_content)
        row2_stats.pack(fill=tk.X)
        
        self.by_rarity_label = ttk.Label(row2_stats, text="By rarity: Common: 0, Uncommon: 0, Rare: 0, Mythic: 0")
        self.by_rarity_label.pack(side=tk.LEFT)
    
    def _load_collection(self):
        """Loads the collection from storage"""
        try:
            # For now, empty collection
            # TODO: Implement loading from file
            self.collection_cards = {}
            self._update_collection_display()
        except Exception as e:
            self.logger.error(f"Error loading collection: {e}")
            messagebox.showerror("Error", f"Error loading collection: {e}")
    
    def _update_collection_display(self):
        """Updates the collection display"""
        # Clear tree
        for item in self.collection_tree.get_children():
            self.collection_tree.delete(item)
        
        # Add collection cards
        for card_name, quantity in self.collection_cards.items():
            # Search for card information
            try:
                cards = self.app_controller.search_cards(card_name)
                if cards:
                    card = cards[0]  # Take first match
                    self.collection_tree.insert('', tk.END, values=(
                        quantity,
                        card.card_name,
                        getattr(card, 'mana_cost', ''),
                        getattr(card, 'type_line', ''),
                        getattr(card, 'rarity', ''),
                        getattr(card, 'set_code', ''),
                        "$0.00"  # TODO: Implement prices
                    ))
                else:
                    # Card not found in database
                    self.collection_tree.insert('', tk.END, values=(
                        quantity,
                        card_name,
                        "?", "?", "?", "?", "$0.00"
                    ))
            except Exception as e:
                self.logger.error(f"Error getting card information {card_name}: {e}")
        
        self._update_stats()
    
    def _update_stats(self):
        """Updates the collection statistics"""
        total_cards = sum(self.collection_cards.values())
        unique_cards = len(self.collection_cards)
        
        self.total_cards_label.config(text=f"Total cards: {total_cards}")
        self.unique_cards_label.config(text=f"Unique cards: {unique_cards}")
        self.total_value_label.config(text="Total value: $0.00")  # TODO: Calcular valor real
        self.by_rarity_label.config(text="By rarity: Common: 0, Uncommon: 0, Rare: 0, Mythic: 0")  # TODO: Calcular por rareza
    
    def _on_search_changed(self, event=None):
        """Handles search changes"""
        search_term = self.search_var.get().strip().lower()
        if not search_term:
            self._update_collection_display()
            return
        
        # Filtrar cartas que coincidan con la búsqueda
        filtered_cards = {}
        for card_name, quantity in self.collection_cards.items():
            if search_term in card_name.lower():
                filtered_cards[card_name] = quantity
        
        # Actualizar visualización con cartas filtradas
        self._display_filtered_collection(filtered_cards)
    
    def _display_filtered_collection(self, filtered_cards: Dict[str, int]):
        """Shows a filtered collection"""
        # Limpiar árbol
        for item in self.collection_tree.get_children():
            self.collection_tree.delete(item)
        
        # Agregar cartas filtradas
        for card_name, quantity in filtered_cards.items():
            try:
                cards = self.app_controller.search_cards(card_name)
                if cards:
                    card = cards[0]
                    self.collection_tree.insert('', tk.END, values=(
                        quantity,
                        card.card_name,
                        getattr(card, 'mana_cost', ''),
                        getattr(card, 'type_line', ''),
                        getattr(card, 'rarity', ''),
                        getattr(card, 'set_code', ''),
                        "$0.00"
                    ))
            except Exception as e:
                self.logger.error(f"Error in filtered card {card_name}: {e}")
    
    def _search_collection(self):
        """Performs search in the collection"""
        self._on_search_changed()
    
    def _add_card_to_collection(self):
        """Adds a card to the collection"""
        card_name = self.add_card_var.get().strip()
        if not card_name:
            messagebox.showwarning("Warning", "Enter a card name")
            return
        
        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                messagebox.showwarning("Warning", "Quantity must be greater than 0")
                return
        except ValueError:
            messagebox.showwarning("Warning", "Invalid quantity")
            return
        
        # Verificar que la carta existe
        try:
            cards = self.app_controller.search_cards(card_name)
            if not cards:
                result = messagebox.askyesno("Card not found", 
                                           f"Card '{card_name}' not found in database.\nAdd it anyway?")
                if not result:
                    return
        except Exception as e:
            self.logger.error(f"Error verifying card: {e}")
        
        # Agregar a la colección
        if card_name in self.collection_cards:
            self.collection_cards[card_name] += quantity
        else:
            self.collection_cards[card_name] = quantity
        
        # Limpiar campos
        self.add_card_var.set("")
        self.quantity_var.set("1")
        
        # Actualizar visualización
        self._update_collection_display()
        
        messagebox.showinfo("Success", f"Added {quantity}x {card_name} to collection")
    
    def _remove_card_from_collection(self):
        """Removes a card from the collection"""
        card_name = self.add_card_var.get().strip()
        if not card_name:
            messagebox.showwarning("Warning", "Enter a card name")
            return
        
        if card_name not in self.collection_cards:
            messagebox.showwarning("Warning", "Card is not in collection")
            return
        
        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                messagebox.showwarning("Warning", "Quantity must be greater than 0")
                return
        except ValueError:
            messagebox.showwarning("Warning", "Invalid quantity")
            return
        
        # Quitar de la colección
        current_quantity = self.collection_cards[card_name]
        if quantity >= current_quantity:
            del self.collection_cards[card_name]
            messagebox.showinfo("Success", f"Completely removed {card_name} from collection")
        else:
            self.collection_cards[card_name] -= quantity
            messagebox.showinfo("Success", f"Removed {quantity}x {card_name} from collection")
        
        # Limpiar campos
        self.add_card_var.set("")
        self.quantity_var.set("1")
        
        # Actualizar visualización
        self._update_collection_display()
    
    def _on_card_selected(self, event=None):
        """Handles card selection"""
        selection = self.collection_tree.selection()
        if selection:
            item = self.collection_tree.item(selection[0])
            card_name = item['values'][1]
            self.add_card_var.set(card_name)
    
    def _on_card_double_click(self, event=None):
        """Handles double click on a card"""
        self._edit_quantity()
    
    def _edit_quantity(self):
        """Edits the quantity of a selected card"""
        selection = self.collection_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a card")
            return
        
        item = self.collection_tree.item(selection[0])
        card_name = item['values'][1]
        current_quantity = item['values'][0]
        
        # Dialog for new quantity
        new_quantity = tk.simpledialog.askinteger(
            "Edit Quantity",
            f"New quantity for {card_name}:",
            initialvalue=current_quantity,
            minvalue=0,
            maxvalue=99
        )
        
        if new_quantity is not None:
            if new_quantity == 0:
                del self.collection_cards[card_name]
            else:
                self.collection_cards[card_name] = new_quantity
            
            self._update_collection_display()
    
    def _view_card_details(self):
        """Shows details of the selected card"""
        messagebox.showinfo("Info", "Function under development: View card details")
    
    def _remove_selected_card(self):
        """Removes the selected card from the collection"""
        selection = self.collection_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a card")
            return
        
        item = self.collection_tree.item(selection[0])
        card_name = item['values'][1]
        
        result = messagebox.askyesno("Confirm", f"Remove {card_name} from collection?")
        if result:
            del self.collection_cards[card_name]
            self._update_collection_display()
    
    def _import_collection(self):
        """Imports a collection from file"""
        file_path = filedialog.askopenfilename(
            title="Import Collection",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            # TODO: Implementar importación
            messagebox.showinfo("Info", "Function under development: Import collection")
    
    def _export_collection(self):
        """Exports the collection to file"""
        if not self.collection_cards:
            messagebox.showwarning("Warning", "Collection is empty")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Collection",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            # TODO: Implementar exportación
            messagebox.showinfo("Info", "Function under development: Export collection")
    
    def _clear_collection(self):
        """Clears the entire collection"""
        if not self.collection_cards:
            messagebox.showinfo("Info", "Collection is already empty")
            return
        
        result = messagebox.askyesno("Confirm", "Are you sure you want to clear the entire collection?")
        if result:
            self.collection_cards.clear()
            self._update_collection_display()
            messagebox.showinfo("Success", "Collection cleared")
    
    def show(self):
        """Shows the view"""
        if self.frame:
            self.frame.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """Hides the view"""
        if self.frame:
            self.frame.pack_forget()
    
    def refresh(self):
        """Refreshes the view"""
        self._update_collection_display()
    
    def get_collection(self) -> Dict[str, int]:
        """Gets the current collection"""
        return self.collection_cards.copy()
    
    def set_collection(self, collection: Dict[str, int]):
        """Sets the collection"""
        self.collection_cards = collection.copy()
        self._update_collection_display()