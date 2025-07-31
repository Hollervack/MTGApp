import requests

def get_card_image(uuid):
    url = f"https://api.scryfall.com/cards/{uuid}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'image_uris' in data:
            return data['image_uris']['normal']
        elif 'card_faces' in data:
            return data['card_faces'][0]['image_uris']['normal']
    return None