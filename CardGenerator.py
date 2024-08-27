
import os
import requests
from PIL import Image
from io import BytesIO
from pokemontcgsdk import Card

class CardGenerator:

    def get_card_details(self, name, number, set_total=None, promo=False):
        '''
        Query pokemontcg api using pokemontcg sdk.
        Return: CardDBOBj 
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
        sub_type = '_'.join(tcg_card.get("subtypes", ["none"]))
        image_url = tcg_card.get("images", {}).get("large", "none")
        card_type = '_'.join(tcg_card.get("types", ["none"]))
        rarity = tcg_card.get("rarity", "none")

        image_path = self.fetch_card_image(image_url, name, number, set_total) if image_url != "none" else "none"
        set_image_path = self.fetch_set_image(set_image_url, set_name,set_series, set_id) if set_image_url != "none" else "none"


        return {"name":name, 
                "number":number, 
                "set_total":set_total, 
                "super_type":super_type, 
                "card_type":card_type, 
                "sub_type":sub_type, 
                "image_url":image_url, 
                "image_path":image_path,
                "rarity": rarity,
                "set_id":set_id,
                "set_name":set_name,
                "set_series": set_series,
                "set_image_url": set_image_url,
                "set_image_path": set_image_path
            }


    def fetch_card_image(self, url, name, number, set_total):
        '''
        Get image from internet using requests and store the image in some location /Pokemon_Cards/<card_name>/<number>_<set_total>
        '''
        folder_path = os.path.join('Pokemon_Cards', name)
        image_path = os.path.join(folder_path, f'{number}_{set_total}.jpg')
        image_exists = self.does_file_exist(image_path)
        folder_exists = self.create_folder_if_not_exists(folder_path=folder_path) # for cards with same name but different number and set total
        print(f'image exists: {image_exists}, folder exists: {folder_exists}')
        if image_exists and folder_exists:
             return image_path
        print(f"Fetching Card photo from internet for card: {name}, {number}/{set_total}")
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to fetch image: {response.status_code}")
            return None

        img = Image.open(BytesIO(response.content))
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        img.save(image_path)
        
            
        return image_path

    def fetch_set_image(self, url, name, series, set_id):
        '''
        Get image from internet using requests and store the image in some location /Pokemon_Cards/<card_name>/<number>_<set_total>
        '''
        folder_path = os.path.join('Sets', series, name)
        image_path = os.path.join(folder_path, f'{set_id}.jpg')
        image_exists = self.does_file_exist(image_path)
        folder_exists = self.create_folder_if_not_exists(folder_path=folder_path) # for cards with same name but different number and set total
        print(f'image exists: {image_exists}, folder exists: {folder_exists}')
        if image_exists and folder_exists:
             return image_path
        print(f"Fetching photo from internet for set: {series}, {name}, {set_id}")
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to fetch image: {response.status_code}")
            return None

        img = Image.open(BytesIO(response.content))
        if img.mode in ("RGBA", "P"):
            img = img.convert('RGB')
        img.save(image_path)
        
            
        return image_path
    
    @staticmethod
    def does_file_exist(file_path):
        ''' returns whether or not the file exists'''
        exists = os.path.exists(file_path)
        if exists:
            print("Folder already exists")
        return exists
    
    @staticmethod
    def create_folder_if_not_exists(folder_path):
        '''
        returns false if folder exists, else creates new folder and returns true
        '''
        try:
            os.makedirs(folder_path, exist_ok=False)
        except OSError:
            print("Folder already exists")
        print(f"Directory '{folder_path}' is ready.")
        return True