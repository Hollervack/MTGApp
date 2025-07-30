from PIL import Image, ImageTk
import requests
import io

def descargar_imagen(url, tamaño=(223, 310)):
    response = requests.get(url)
    if response.status_code == 200:
        img_data = response.content
        image = Image.open(io.BytesIO(img_data)).resize(tamaño)
        return ImageTk.PhotoImage(image)
    return None