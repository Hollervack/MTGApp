import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from logic.card_loader import cargar_cartas
from logic.scryfall import get_card_image
from logic.deck_compare import cargar_baraja_edhrec, comparar_con_coleccion
from utils.image_utils import descargar_imagen

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Cartas MTG - MVP")
        self.geometry("900x500")

        self.cartas = cargar_cartas()
        self.cartas_por_nombre = {c['card_name']: c for c in self.cartas}
        nombres = sorted([nombre for nombre in self.cartas_por_nombre.keys() if nombre])

        self.combo = ttk.Combobox(self, values=nombres, width=50)
        self.combo.pack(pady=10)

        self.boton = ttk.Button(self, text="Mostrar carta", command=self.mostrar_carta)
        self.boton.pack(pady=5)

        self.boton_baraja = ttk.Button(self, text="Cargar baraja EDHREC", command=self.analizar_baraja)
        self.boton_baraja.pack(pady=5)

        self.label_imagen = tk.Label(self)
        self.label_imagen.pack(pady=10)

    def mostrar_carta(self):
        nombre = self.combo.get()
        if not nombre:
            messagebox.showwarning("Aviso", "Selecciona una carta.")
            return

        carta = self.cartas_por_nombre.get(nombre)
        if not carta:
            messagebox.showerror("Error", "Carta no encontrada.")
            return

        uuid = carta['scryfall_uuid']
        url_imagen = get_card_image(uuid)
        if url_imagen:
            img = descargar_imagen(url_imagen)
            if img:
                self.label_imagen.configure(image=img)
                self.label_imagen.image = img
            else:
                messagebox.showerror("Error", "No se pudo descargar la imagen.")
        else:
            messagebox.showerror("Error", "No se encontró la imagen en Scryfall.")

    def analizar_baraja(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return

        baraja = cargar_baraja_edhrec(filepath)
        faltantes = comparar_con_coleccion(baraja, self.cartas)

        if not faltantes:
            messagebox.showinfo("Genial!", "¡Ya tienes todas las cartas de esta baraja!")
            return

        ventana = tk.Toplevel(self)
        ventana.title("Cartas que te faltan")
        ventana.geometry("600x400")

        tree = ttk.Treeview(ventana, columns=("Card", "Owned", "Needed", "Missing"), show='headings')
        for col in ("Card", "Owned", "Needed", "Missing"):
            tree.heading(col, text=col)
            tree.column(col, width=140)
        for carta in faltantes:
            tree.insert('', 'end', values=(carta['Card'], carta['Owned'], carta['Needed'], carta['Missing']))
        tree.pack(expand=True, fill='both', pady=10)

        def guardar_csv():
            salida = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if salida:
                import csv
                with open(salida, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['Card', 'Owned', 'Needed', 'Missing'])
                    writer.writeheader()
                    writer.writerows(faltantes)
                messagebox.showinfo("Guardado", "Lista de compra guardada correctamente.")

        boton_guardar = ttk.Button(ventana, text="Guardar lista como CSV", command=guardar_csv)
        boton_guardar.pack(pady=5)