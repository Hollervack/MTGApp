import csv

def load_edhrec_deck(filepath):
    deck = {}
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        columns = [col.strip() for col in reader.fieldnames]

        # Find correct column
        name_column = next((col for col in columns if col.lower() in ['card', 'name', 'card name']), None)
        if not name_column:
            raise ValueError("No valid column found for card name (Card/Name).")

        for row in reader:
            name = row[name_column].strip()
            if name:
                deck[name] = deck.get(name, 0) + 1
    return deck

def compare_with_collection(deck, collection):
    collection_cards = {}
    incomplete_cards = []

    for card in collection:
        name = (card.get('english_card_name') or '').strip()
        if not name:
            incomplete_cards.append(card)
            continue
        quantity = card['quantity']
        collection_cards[name] = collection_cards.get(name, 0) + quantity

    # Save log of incomplete cards
    if incomplete_cards:
        with open('incomplete_cards_log.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = collection[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(incomplete_cards)

    missing = []
    for name, needed in deck.items():
        in_collection = collection_cards.get(name, 0)
        if in_collection < needed:
            missing.append({
                'Card': name,
                'Owned': in_collection,
                'Needed': needed,
                'Missing': needed - in_collection
            })
    return missing