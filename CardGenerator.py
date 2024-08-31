
import os
import requests
from PIL import Image
from io import BytesIO
from pokemontcgsdk import Card

class CardGenerator:

    def get_card_details(self, name, number, set_total=None, promo=False):
        '''
            Query pokemontcg api using pokemontcg sdk.
            Return: dictionary representation of card information 
        '''
        if set_total is not None:
            query = f'name:"{name}" number:{number} set.printedTotal:{set_total}'
        elif "Energy" in name and promo == False:
            query = f'name:"{name}" number:{number}'
        elif promo:
            query = f'name:"{name}" number:{number} rarity:promo'
        else:
            raise ValueError("Invalid input parameters")

        try:
            tcg_card = Card.where(q=query)[0].to_dict()
        except:
            print(f"failed to find {name}, {number}")
            return {}
        
        set_id = tcg_card.get("set", {}).get("id", "none")
        set_name = tcg_card.get("set", {}).get("name", "none")
        set_series = tcg_card.get("set", {}).get("series", "none")
        set_image_url = tcg_card.get("set", {}).get("images", {}).get("logo", "none")
        set_total = tcg_card.get("set", {}).get("printedTotal", "none")
        super_type = tcg_card.get("supertype", ["none"])
        sub_type = ','.join(tcg_card.get("subtypes", ["none"]))
        image_url = tcg_card.get("images", {}).get("large", "none")
        card_type = ','.join(tcg_card.get("types", ["none"]))
        rarity = tcg_card.get("rarity", "Common")
        ability = tcg_card.get("abilities", None) # list of dicts
        image_path = self.__fetch_image(url=image_url,card_name=name, card_number=number, card_set_total=set_total) if image_url != "none" else "none"
        set_image_path = self.__fetch_image(url=set_image_url, set_name=set_name, set_series=set_series, set_id=set_id) if set_image_url != "none" else "none"


        return {"name":name, 
                "number":number, 
                "set_total":set_total, 
                "super_type":super_type, 
                "card_type":card_type, 
                "sub_type":sub_type, 
                "image_url":image_url, 
                "image_path":image_path,
                "rarity": rarity,
                "ability":ability,
                "set_id":set_id,
                "set_name":set_name,
                "set_series": set_series,
                "set_image_url": set_image_url,
                "set_image_path": set_image_path
            }


    def __fetch_image(self, url: str | None = None, card_name: str | None = None, card_number: str | None = None, card_set_total: str | None = None, set_name: str | None = None, set_series: str | None = None, set_id: str | None = None):
        '''
            Generate image paths for set image and card image. 
            return image path str
        '''
        if card_name is not None:
            folder_path = os.path.join('Pokemon_Cards', card_name)
            image_path = os.path.join(folder_path, f'{card_number}_{card_set_total}.jpg')
        elif set_name is not None:
            folder_path = os.path.join('Sets', set_series, set_name)
            image_path = os.path.join(folder_path, f'{set_id}.jpg')
        
        image_exists = self.does_file_exist(image_path)
        folder_exists = self.create_folder_if_not_exists(folder_path=folder_path) # for cards with same name but different number and set total

        if image_exists and folder_exists:
            print(f'image exists: {image_exists}, folder exists: {folder_exists}')
            return image_path
        
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to fetch image: {response.status_code}")
            return None
        
        self.save_image(response.content, image_path=image_path)
            
        return image_path

    @staticmethod
    def does_file_exist(file_path):
        ''' returns whether or not the file exists'''
        exists = os.path.exists(file_path)
        if exists:
            print(f"File at {file_path} already exists")
        return exists
    
    @staticmethod
    def create_folder_if_not_exists(folder_path):
        ''' returns false if folder exists, else creates new folder and returns true '''
        try:
            os.makedirs(folder_path, exist_ok=False)
        except OSError:
            print("Folder already exists")
        print(f"Directory '{folder_path}' is ready.")
        return True
    
    def save_image(self, content, image_path):
        img = Image.open(BytesIO(content))
        if img.mode in ("RGBA", "P"):
            img = img.convert('RGB')
        img.save(image_path)