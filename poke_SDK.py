from pokemontcgsdk import Card
from pokemontcgsdk import Set
# from pokemontcgsdk import Type
# from pokemontcgsdk import Supertype
# from pokemontcgsdk import Subtype
# from pokemontcgsdk import Rarity
import requests
from PIL import Image
from io import BytesIO


# find card by ID
def find_card(id='sv1-1'):
    card = Card.find(id)
    url = card.images.large
    show_image(url, 1)

def show_image(imageUrl, num):
    
    def fetch_image(url):
        response = requests.get(url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            # Convert image mode to 'RGB' if it's 'RGBA'
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            return img
        else:
            print(f"Failed to fetch image: {response.status_code}")
            return None

    # Example usage
    image = fetch_image(imageUrl)
    if image:
        # image.show()  # This will open the image
        image.save(f'card_{num}.jpg')

# find_card()
def get_all_sets():
    sets = Set.all()
    # print(sets)
    print(Set.where(q='name:Obsidian'))
    # card = Set.find('')
    # print(card)
    # Filter sets
    # sets = Set.where(q='name:Obsidian Flames')
    # print(sets)
    # Get a specific page of data
    # sets = Set.where(page=2, pageSize=10)
    
# get_all_sets()
    

def get_cards_in_set(query=''):
    cards = Card.where(q=query)
    for card in cards:
        print(card.name)
# get_cards_in_set('set.name:Obsidian supertype:pokemon')

def get_card(name=''):
    card = Card.where(q='name:charmander')[0].to_dict() 
    print(card.to_dict())
    return 
    
# get_card()
def query_cards(query='') -> list:
    # get pokemn cards from pokemon sdk
    return Card.where(q=query)

def get_all_sets():

    all_sets =  Set.all()
    for s in all_sets:
        if "Scarlet" in s.series:
            print(s.name)

def fetch_my_pokemon_cards() -> list:
    # get pokemn cards from pokemon sdk
    my_cards = Card.where(q='subtypes:Electric set.series:Scarlet')[0].to_dict()
    # print(f'cards: {len(my_cards)}')
    print(my_cards)


# fetch_my_pokemon_cards()

def test_retrieve():
    query = f'supertype:"Energy" subtypes:"Basic"'
    card_list = [card.to_dict()for card in Card.where(q=query)]
    for card in card_list:
        print(card)

test_retrieve()
