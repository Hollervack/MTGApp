import csv
import requests

def completar_nombres_con_scryfall(input_csv='cartas_incompletas_log.csv', output_csv='cartas_corregidas.csv'):
    cartas_corregidas = []

    with open(input_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        fieldnames = reader.fieldnames
        for row in reader:
            uuid = row.get('scryfall_uuid', '').strip()
            if uuid:
                nombre_ingles = obtener_nombre_desde_scryfall(uuid)
                if nombre_ingles:
                    row['english_card_name'] = nombre_ingles
            cartas_corregidas.append(row)

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(cartas_corregidas)

    print(f"✔ Cartas corregidas guardadas en '{output_csv}'.")

def obtener_nombre_desde_scryfall(uuid):
    try:
        url = f'https://api.scryfall.com/cards/{uuid}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'name' in data:
                return data['name']
            elif 'card_faces' in data:
                return data['card_faces'][0]['name']
    except Exception as e:
        print(f"Error al obtener carta con UUID {uuid}: {e}")
    return None

if __name__ == '__main__':
    completar_nombres_con_scryfall()