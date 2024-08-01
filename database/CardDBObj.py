from pokemontcgsdk import Card
import os
import requests
from PIL import Image
from io import BytesIO

class CardDBObj:
    def __init__(self, name, number, set_total, card_type, super_type="none", sub_type="none", image_url="none", image_path="none"):
        self.name = name
        self.number = number
        self.set_total = set_total
        self.super_type = super_type
        self.card_type = card_type
        self.sub_type = sub_type
        self.image_url = image_url
        self.image_path = image_path

    def __str__(self):
        return (f"Card(Name: {self.name},\nNumber: {self.number},\nSet Total: {self.set_total},"
                f"\nType: {self.card_type},\nSub Type: {self.sub_type},\nImage path: {self.image_path})")

class CardGenerator:

    def get_card_details(self, name, number, set_total=None, rarity=None):
        '''
        Query pokemontcg api using pokemontcg sdk.
        Return: CardDBOBj 
        '''
        if set_total is not None:
            query = f'name:"{name}" number:{number} set.printedTotal:{set_total}'
        elif "Energy" in name and rarity is None:
            query = f'name:"{name}" number:{number}'
        elif rarity == "promo" or rarity == "Promo":
            query = f'name:"{name}" number:{number} rarity:{rarity}'
        else:
            raise ValueError("Invalid input parameters")

        tcg_card = Card.where(q=query)[0].to_dict()

        set_total = tcg_card.get("set", {}).get("printedTotal", "none")
        super_type = tcg_card.get("supertype", ["none"])
        sub_type = '_'.join(tcg_card.get("subtypes", ["none"]))
        image_url = tcg_card.get("images", {}).get("large", "none")
        card_type = '_'.join(tcg_card.get("types", ["None"]))

        image_path = self.fetch_card_image(image_url, name, number, set_total)[1] if image_url != "none" else "none"

        return CardDBObj(name=name, number=number, set_total=set_total, super_type=super_type, card_type=card_type, sub_type=sub_type, image_url=image_url, image_path=image_path)


    def fetch_card_image(self, url, name, number, set_total):
        '''
        Get image from internet using requests and store the image in some location /Pokemon_Cards/<card_name>/<number>_<set_total>
        '''
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to fetch image: {response.status_code}")
            return None, None

        img = Image.open(BytesIO(response.content))
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        folder_path = os.path.join('Pokemon_Cards', name)
        self.create_folder_if_not_exists(folder_path)
        image_path = os.path.join(folder_path, f'{number}_{set_total}.jpg')

        img.save(image_path)
        return img, image_path

    @staticmethod
    def _create_folder_if_not_exists(folder_path):
        '''
        create a folder at some given path if one doesnt exist already
        '''
        os.makedirs(folder_path, exist_ok=True)
        print(f"Directory '{folder_path}' is ready.")