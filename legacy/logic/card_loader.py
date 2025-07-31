import csv

def cargar_cartas(path='data/databaseMTG.csv'):
    cartas = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            row['quantity'] = int(row['quantity']) if row['quantity'] else 0
            cartas.append(row)
    return cartas