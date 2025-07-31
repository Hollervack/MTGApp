"""Vista de la colección de cartas"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import logging
from typing import List, Dict, Any, Optional

from ..controllers.app_controller import AppController
from ..models.card import Card


class CollectionView:
    """Vista para gestionar la colección de cartas del usuario"""
    
    def __init__(self, parent: tk.Widget, app_controller: AppController):
        self.parent = parent
        self.app_controller = app_controller
        self.logger = logging.getLogger('MTGDeckConstructor.CollectionView')
        
        self.collection_cards: Dict[str, int] = {}  # card_name -> quantity
        self.frame = None
        
        self._create_interface()
        self._load_collection()
    
    def _create_interface(self):
        """Crea la interfaz de la colección"""
        # Frame principal
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
        tools_frame = ttk.LabelFrame(self.frame, text="Herramientas de Colección")
        tools_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Primera fila - importar/exportar
        row1_frame = ttk.Frame(tools_frame)
        row1_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(row1_frame, text="Importar Colección", command=self._import_collection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1_frame, text="Exportar Colección", command=self._export_collection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1_frame, text="Limpiar Colección", command=self._clear_collection).pack(side=tk.LEFT, padx=(0, 10))
        
        # Separador
        ttk.Separator(row1_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Búsqueda en colección
        ttk.Label(row1_frame, text="Buscar en colección:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(row1_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind('<KeyRelease>', self._on_search_changed)
        
        ttk.Button(row1_frame, text="Buscar", command=self._search_collection).pack(side=tk.LEFT)
        
        # Segunda fila - agregar cartas
        row2_frame = ttk.Frame(tools_frame)
        row2_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row2_frame, text="Agregar carta:").pack(side=tk.LEFT, padx=(0, 5))
        self.add_card_var = tk.StringVar()
        add_card_entry = ttk.Entry(row2_frame, textvariable=self.add_card_var, width=25)
        add_card_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(row2_frame, text="Cantidad:").pack(side=tk.LEFT, padx=(5, 5))
        self.quantity_var = tk.StringVar(value="1")
        quantity_spin = ttk.Spinbox(row2_frame, from_=1, to=99, textvariable=self.quantity_var, width=5)
        quantity_spin.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(row2_frame, text="Agregar", command=self._add_card_to_collection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row2_frame, text="Quitar", command=self._remove_card_from_collection).pack(side=tk.LEFT)
    
    def _create_collection_panel(self):
        """Crea el panel de la colección"""
        collection_frame = ttk.LabelFrame(self.frame, text="Mi Colección")
        collection_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Crear Treeview para mostrar la colección
        tree_frame = ttk.Frame(collection_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configurar columnas
        columns = ('quantity', 'name', 'mana_cost', 'type', 'rarity', 'set', 'value')
        self.collection_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Configurar encabezados
        self.collection_tree.heading('quantity', text='Cant.')
        self.collection_tree.heading('name', text='Nombre')
        self.collection_tree.heading('mana_cost', text='Coste')
        self.collection_tree.heading('type', text='Tipo')
        self.collection_tree.heading('rarity', text='Rareza')
        self.collection_tree.heading('set', text='Set')
        self.collection_tree.heading('value', text='Valor')
        
        # Configurar anchos de columna
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
        
        # Frame para botones de acción
        actions_frame = ttk.Frame(collection_frame)
        actions_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Button(actions_frame, text="Editar Cantidad", command=self._edit_quantity).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="Ver Detalles", command=self._view_card_details).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="Eliminar", command=self._remove_selected_card).pack(side=tk.LEFT)
    
    def _create_stats_panel(self):
        """Crea el panel de estadísticas"""
        stats_frame = ttk.LabelFrame(self.frame, text="Estadísticas de la Colección")
        stats_frame.pack(fill=tk.X)
        
        # Frame para estadísticas
        stats_content = ttk.Frame(stats_frame)
        stats_content.pack(fill=tk.X, padx=5, pady=5)
        
        # Primera fila de estadísticas
        row1_stats = ttk.Frame(stats_content)
        row1_stats.pack(fill=tk.X, pady=(0, 5))
        
        self.total_cards_label = ttk.Label(row1_stats, text="Total de cartas: 0")
        self.total_cards_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.unique_cards_label = ttk.Label(row1_stats, text="Cartas únicas: 0")
        self.unique_cards_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.total_value_label = ttk.Label(row1_stats, text="Valor total: $0.00")
        self.total_value_label.pack(side=tk.LEFT)
        
        # Segunda fila de estadísticas
        row2_stats = ttk.Frame(stats_content)
        row2_stats.pack(fill=tk.X)
        
        self.by_rarity_label = ttk.Label(row2_stats, text="Por rareza: Común: 0, Poco común: 0, Rara: 0, Mítica: 0")
        self.by_rarity_label.pack(side=tk.LEFT)
    
    def _load_collection(self):
        """Carga la colección desde el almacenamiento"""
        try:
            # Por ahora, colección vacía
            # TODO: Implementar carga desde archivo
            self.collection_cards = {}
            self._update_collection_display()
        except Exception as e:
            self.logger.error(f"Error cargando colección: {e}")
            messagebox.showerror("Error", f"Error cargando colección: {e}")
    
    def _update_collection_display(self):
        """Actualiza la visualización de la colección"""
        # Limpiar árbol
        for item in self.collection_tree.get_children():
            self.collection_tree.delete(item)
        
        # Agregar cartas de la colección
        for card_name, quantity in self.collection_cards.items():
            # Buscar información de la carta
            try:
                cards = self.app_controller.search_cards(card_name)
                if cards:
                    card = cards[0]  # Tomar la primera coincidencia
                    self.collection_tree.insert('', tk.END, values=(
                        quantity,
                        card.card_name,
                        getattr(card, 'mana_cost', ''),
                        getattr(card, 'type_line', ''),
                        getattr(card, 'rarity', ''),
                        getattr(card, 'set_code', ''),
                        "$0.00"  # TODO: Implementar precios
                    ))
                else:
                    # Carta no encontrada en la base de datos
                    self.collection_tree.insert('', tk.END, values=(
                        quantity,
                        card_name,
                        "?", "?", "?", "?", "$0.00"
                    ))
            except Exception as e:
                self.logger.error(f"Error obteniendo información de carta {card_name}: {e}")
        
        self._update_stats()
    
    def _update_stats(self):
        """Actualiza las estadísticas de la colección"""
        total_cards = sum(self.collection_cards.values())
        unique_cards = len(self.collection_cards)
        
        self.total_cards_label.config(text=f"Total de cartas: {total_cards}")
        self.unique_cards_label.config(text=f"Cartas únicas: {unique_cards}")
        self.total_value_label.config(text="Valor total: $0.00")  # TODO: Calcular valor real
        self.by_rarity_label.config(text="Por rareza: Común: 0, Poco común: 0, Rara: 0, Mítica: 0")  # TODO: Calcular por rareza
    
    def _on_search_changed(self, event=None):
        """Maneja cambios en la búsqueda"""
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
        """Muestra una colección filtrada"""
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
                self.logger.error(f"Error en carta filtrada {card_name}: {e}")
    
    def _search_collection(self):
        """Realiza búsqueda en la colección"""
        self._on_search_changed()
    
    def _add_card_to_collection(self):
        """Agrega una carta a la colección"""
        card_name = self.add_card_var.get().strip()
        if not card_name:
            messagebox.showwarning("Advertencia", "Ingresa el nombre de una carta")
            return
        
        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                messagebox.showwarning("Advertencia", "La cantidad debe ser mayor a 0")
                return
        except ValueError:
            messagebox.showwarning("Advertencia", "Cantidad inválida")
            return
        
        # Verificar que la carta existe
        try:
            cards = self.app_controller.search_cards(card_name)
            if not cards:
                result = messagebox.askyesno("Carta no encontrada", 
                                           f"No se encontró la carta '{card_name}' en la base de datos.\n¿Agregarla de todas formas?")
                if not result:
                    return
        except Exception as e:
            self.logger.error(f"Error verificando carta: {e}")
        
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
        
        messagebox.showinfo("Éxito", f"Se agregaron {quantity}x {card_name} a la colección")
    
    def _remove_card_from_collection(self):
        """Quita una carta de la colección"""
        card_name = self.add_card_var.get().strip()
        if not card_name:
            messagebox.showwarning("Advertencia", "Ingresa el nombre de una carta")
            return
        
        if card_name not in self.collection_cards:
            messagebox.showwarning("Advertencia", "La carta no está en la colección")
            return
        
        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                messagebox.showwarning("Advertencia", "La cantidad debe ser mayor a 0")
                return
        except ValueError:
            messagebox.showwarning("Advertencia", "Cantidad inválida")
            return
        
        # Quitar de la colección
        current_quantity = self.collection_cards[card_name]
        if quantity >= current_quantity:
            del self.collection_cards[card_name]
            messagebox.showinfo("Éxito", f"Se quitó completamente {card_name} de la colección")
        else:
            self.collection_cards[card_name] -= quantity
            messagebox.showinfo("Éxito", f"Se quitaron {quantity}x {card_name} de la colección")
        
        # Limpiar campos
        self.add_card_var.set("")
        self.quantity_var.set("1")
        
        # Actualizar visualización
        self._update_collection_display()
    
    def _on_card_selected(self, event=None):
        """Maneja la selección de una carta"""
        selection = self.collection_tree.selection()
        if selection:
            item = self.collection_tree.item(selection[0])
            card_name = item['values'][1]
            self.add_card_var.set(card_name)
    
    def _on_card_double_click(self, event=None):
        """Maneja doble clic en una carta"""
        self._edit_quantity()
    
    def _edit_quantity(self):
        """Edita la cantidad de una carta seleccionada"""
        selection = self.collection_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una carta")
            return
        
        item = self.collection_tree.item(selection[0])
        card_name = item['values'][1]
        current_quantity = item['values'][0]
        
        # Diálogo para nueva cantidad
        new_quantity = tk.simpledialog.askinteger(
            "Editar Cantidad",
            f"Nueva cantidad para {card_name}:",
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
        """Muestra detalles de la carta seleccionada"""
        messagebox.showinfo("Info", "Función en desarrollo: Ver detalles de carta")
    
    def _remove_selected_card(self):
        """Elimina la carta seleccionada de la colección"""
        selection = self.collection_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una carta")
            return
        
        item = self.collection_tree.item(selection[0])
        card_name = item['values'][1]
        
        result = messagebox.askyesno("Confirmar", f"¿Eliminar {card_name} de la colección?")
        if result:
            del self.collection_cards[card_name]
            self._update_collection_display()
    
    def _import_collection(self):
        """Importa una colección desde archivo"""
        file_path = filedialog.askopenfilename(
            title="Importar Colección",
            filetypes=[("Archivos de texto", "*.txt"), ("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            # TODO: Implementar importación
            messagebox.showinfo("Info", "Función en desarrollo: Importar colección")
    
    def _export_collection(self):
        """Exporta la colección a archivo"""
        if not self.collection_cards:
            messagebox.showwarning("Advertencia", "La colección está vacía")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar Colección",
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            # TODO: Implementar exportación
            messagebox.showinfo("Info", "Función en desarrollo: Exportar colección")
    
    def _clear_collection(self):
        """Limpia toda la colección"""
        if not self.collection_cards:
            messagebox.showinfo("Info", "La colección ya está vacía")
            return
        
        result = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres limpiar toda la colección?")
        if result:
            self.collection_cards.clear()
            self._update_collection_display()
            messagebox.showinfo("Éxito", "Colección limpiada")
    
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
        self._update_collection_display()
    
    def get_collection(self) -> Dict[str, int]:
        """Obtiene la colección actual"""
        return self.collection_cards.copy()
    
    def set_collection(self, collection: Dict[str, int]):
        """Establece la colección"""
        self.collection_cards = collection.copy()
        self._update_collection_display()