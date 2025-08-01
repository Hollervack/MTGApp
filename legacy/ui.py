import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from logic.card_loader import load_cards
from logic.scryfall import get_card_image
from logic.deck_compare import load_edhrec_deck, compare_with_collection
from utils.image_utils import download_image

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MTG Card Manager - MVP")
        self.geometry("900x500")

        self.cards = load_cards()
        self.cards_by_name = {c['card_name']: c for c in self.cards}
        names = sorted([name for name in self.cards_by_name.keys() if name])

        self.combo = ttk.Combobox(self, values=names, width=50)
        self.combo.pack(pady=10)

        self.button = ttk.Button(self, text="Show card", command=self.show_card)
        self.button.pack(pady=5)

        self.deck_button = ttk.Button(self, text="Load EDHREC deck", command=self.analyze_deck)
        self.deck_button.pack(pady=5)

        self.image_label = tk.Label(self)
        self.image_label.pack(pady=10)

    def show_card(self):
        name = self.combo.get()
        if not name:
            messagebox.showwarning("Warning", "Select a card.")
            return

        card = self.cards_by_name.get(name)
        if not card:
            messagebox.showerror("Error", "Card not found.")
            return

        uuid = card['scryfall_uuid']
        image_url = get_card_image(uuid)
        if image_url:
            img = download_image(image_url)
            if img:
                self.image_label.configure(image=img)
                self.image_label.image = img
            else:
                messagebox.showerror("Error", "Could not download image.")
        else:
            messagebox.showerror("Error", "Image not found in Scryfall.")

    def analyze_deck(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return

        deck = load_edhrec_deck(filepath)
        missing = compare_with_collection(deck, self.cards)

        if not missing:
            messagebox.showinfo("Great!", "You already have all cards from this deck!")
            return

        window = tk.Toplevel(self)
        window.title("Missing cards")
        window.geometry("600x400")

        tree = ttk.Treeview(window, columns=("Card", "Owned", "Needed", "Missing"), show='headings')
        for col in ("Card", "Owned", "Needed", "Missing"):
            tree.heading(col, text=col)
            tree.column(col, width=140)
        for card in missing:
            tree.insert('', 'end', values=(card['Card'], card['Owned'], card['Needed'], card['Missing']))
        tree.pack(expand=True, fill='both', pady=10)

        def save_csv():
            output = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if output:
                import csv
                with open(output, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['Card', 'Owned', 'Needed', 'Missing'])
                    writer.writeheader()
                    writer.writerows(missing)
                messagebox.showinfo("Saved", "Shopping list saved successfully.")

        save_button = ttk.Button(window, text="Save list as CSV", command=save_csv)
        save_button.pack(pady=5)