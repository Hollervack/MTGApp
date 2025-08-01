import csv

def load_cards(path='data/databaseMTG.csv'):
    cards = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            row['quantity'] = int(row['quantity']) if row['quantity'] else 0
            cards.append(row)
    return cards