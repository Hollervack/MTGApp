import csv

def cargar_baraja_edhrec(filepath):
    baraja = {}
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        columnas = [col.strip() for col in reader.fieldnames]

        # Buscar columna correcta
        columna_nombre = next((col for col in columnas if col.lower() in ['card', 'name', 'card name']), None)
        if not columna_nombre:
            raise ValueError("No se encontró ninguna columna válida para el nombre de carta (Card/Name).")

        for row in reader:
            nombre = row[columna_nombre].strip()
            if nombre:
                baraja[nombre] = baraja.get(nombre, 0) + 1
    return baraja

def comparar_con_coleccion(baraja, coleccion):
    cartas_coleccion = {}
    cartas_incompletas = []

    for carta in coleccion:
        nombre = (carta.get('english_card_name') or '').strip()
        if not nombre:
            cartas_incompletas.append(carta)
            continue
        cantidad = carta['quantity']
        cartas_coleccion[nombre] = cartas_coleccion.get(nombre, 0) + cantidad

    # Guardar log de cartas incompletas
    if cartas_incompletas:
        with open('cartas_incompletas_log.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = coleccion[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cartas_incompletas)

    faltantes = []
    for nombre, necesarios in baraja.items():
        en_coleccion = cartas_coleccion.get(nombre, 0)
        if en_coleccion < necesarios:
            faltantes.append({
                'Card': nombre,
                'Owned': en_coleccion,
                'Needed': necesarios,
                'Missing': necesarios - en_coleccion
            })
    return faltantes