import csv
from CardGenerator import CardGenerator
from card_database import CardDatabase

def restore_to_base() -> None:
    ''' hard code to ensure no loss of v1 decks
    Creates Dark deck 1 via get_card_details() and add_card()
    '''
    db_path = "test_db.db"
    db_manager = CardDeckManager(db_path)
    card_generator = CardGenerator()

    deck_names = ["Dark1", "Water1"]
    dark_deck_id = db_manager.create_deck(deck_names[0])
    water_deck_id = db_manager.create_deck(deck_names[1])
    db_manager.show_decks()
    water_deck = [
        {"name": "Basic Water Energy", "number":3, "set_total":None, "amount":3, "promo": False},
        {"name": "Water Energy", "number":102, "set_total":102, "amount":11, "promo": False},
        {"name": "Basic Psychic Energy", "number":5, "set_total":None, "amount":4, "promo": False},
        {"name": "Psychic Energy", "number":101, "set_total":102, "amount":9, "promo": False},

        {"name": "Articuno", "number":144, "set_total":165, "amount":2, "promo": False},
        {"name": "Espathra", "number":81, "set_total":182, "amount":2, "promo": False},
        {"name": "Flittle", "number":80, "set_total":182, "amount":2, "promo": False},
        {"name": "Golisopod", "number":49, "set_total":182, "amount":3, "promo": False},
        {"name": "Iron Bundle", "number":58, "set_total":None, "amount":1, "promo": True},  
        {"name": "Iron Bundle", "number":56, "set_total":182, "amount":1, "promo": False},
        {"name": "Lapras", "number":16, "set_total":91, "amount":1, "promo": False},
        {"name": "Mantyke", "number":39, "set_total":182, "amount":1, "promo": False},
        {"name": "Mewtwo", "number":150, "set_total":165, "amount":1, "promo": False},
        {"name": "Natu", "number":71, "set_total":182, "amount":2, "promo": False},
        {"name": "Wimpod", "number":48, "set_total":182, "amount":1, "promo": False},
        {"name": "Wimpod", "number":47, "set_total":182, "amount":2, "promo": False},
        {"name": "Xatu", "number":72, "set_total":182, "amount":1, "promo": False},

        {"name": "Bill's Transfer", "number":156, "set_total":165, "amount":2, "promo": False},
        {"name": "Jacq", "number":175, "set_total":198, "amount":1, "promo": False},
        {"name": "Mesagoza", "number":178, "set_total":198, "amount":1, "promo": False},
        {"name": "Nemona", "number":82, "set_total":91, "amount":2, "promo": False},
        {"name": "Nemona's Backpack", "number":83, "set_total":91, "amount":1, "promo": False},
        {"name": "Nest Ball", "number":181, "set_total":198, "amount":1, "promo": False},
        {"name": "Parasol Lady", "number":169, "set_total":182, "amount":1, "promo": False},
        {"name": "Rika", "number":172, "set_total":182, "amount":1, "promo": False},
        {"name": "Tulip", "number":181, "set_total":182, "amount":2, "promo": False},
        {"name": "Youngster", "number":198, "set_total":198, "amount":2, "promo": False}
    ]
    
    # dark_deck = {
    #     1: {"name": "Basic Darkness Energy", "number":7, "set_total":None, "amount":19, "promo": False},
    #     2: {"name": "Basic Psychic Energy", "number":5, "set_total":None, "amount":3, "promo": False},
    #     3: {"name": "Psychic Energy", "number":101, "set_total":102,"amount":3, "promo": False},
    #     4: {"name": "Darkrai", "number":136, "set_total":197,"amount":3, "promo": False},
    #     5: {"name": "Brute Bonnet", "number":123, "set_total":182, "amount":1, "promo": False},
    #     6: {"name": "Hoopa ex", "number":98, "set_total":182, "amount":1, "promo": False},
    #     7: {"name": "Roaring Moon ex", "number":124, "set_total":182, "amount":1, "promo": False},
    #     8: {"name": "Yveltal", "number":118, "set_total":182, "amount":1, "promo": False},
    #     9: {"name": "Fezandipiti", "number":96, "set_total":167, "amount":1, "promo": False},
    #     10: {"name": "Miltank", "number":147, "set_total":182, "amount":1, "promo": False},
    #     11: {"name": "Switch", "number":95, "set_total":102, "amount":3, "promo": False},
    #     12: {"name": "Daisy's Help", "number":158, "set_total":165, "amount":2, "promo": False},
    #     13: {"name": "Professor Sada's Vitality", "number":170, "set_total":182, "amount":1, "promo": False},
    #     14: {"name": "Ancient Booster Energy Capsule", "number":140, "set_total":162, "amount":1, "promo": False},
    #     15: {"name": "Boomerang Energy", "number":166, "set_total":167, "amount":1, "promo": False},
    #     16: {"name": "Mist Energy", "number":161, "set_total":162, "amount":1, "promo": False},
    #     17: {"name": "Energy Switch", "number":173, "set_total":198, "amount":1, "promo": False},
    #     18: {"name": "Paldean Student", "number":85, "set_total":91, "amount":1, "promo": False},
    #     19: {"name": "Leftovers", "number":163, "set_total":165, "amount":1, "promo": False},
    #     20: {"name": "Thorton", "number":167, "set_total":196, "amount":1, "promo": False},
    #     21: {"name": "Hassel", "number":151, "set_total":167, "amount":1, "promo": False},
    #     22: {"name": "Miriam", "number":179, "set_total":198, "amount":1, "promo": False},
    #     23: {"name": "Energy Removal", "number":92, "set_total":102, "amount":1, "promo": False},
    #     24: {"name": "Lana's Aid", "number":155, "set_total":167, "amount":1, "promo": False},
    #     25: {"name": "Cook", "number":147, "set_total":167, "amount":2, "promo": False},
    #     26: {"name": "Energy Switch", "number":173, "set_total":198, "amount":1, "promo": False},
    #     27: {"name": "Letter of Encouragement", "number":189, "set_total":197, "amount":1, "promo": False},
    #     28: {"name": "Grabber", "number":162, "set_total":165, "amount":1, "promo": False},
    #     29: {"name": "Roark", "number":173, "set_total":182, "amount":1, "promo": False},
    #     30: {"name": "Rock Chestplate", "number":192, "set_total":198, "amount":1, "promo": False},
    #     31: {"name": "Kieran", "number":154, "set_total":167, "amount":1, "promo": False},
    #     32: {"name": "Atticus", "number":77, "set_total":91, "amount":1, "promo": False}
    # }

    # Adds dark deck cards to the data base and to deck Dark1
    # for _, card_info in dark_deck.items():
    #     sdk_card = card_generator.get_card_details(name=card_info["name"], number=card_info["number"], set_total=card_info["set_total"], promo=card_info["promo"])
    #     sdk_card_id = db_manager.add_card(sdk_card, card_info["amount"])
    #     db_manager.move_card_to_deck(dark_deck_id, sdk_card_id, card_info["amount"])
    
    for card_info in water_deck:
        sdk_card = card_generator.get_card_details(name=card_info["name"], number=card_info["number"], set_total=card_info["set_total"], promo=card_info["promo"])
        sdk_card_id = db_manager.add_card(sdk_card, card_info["amount"])
        db_manager.move_card_to_deck(water_deck_id, sdk_card_id, card_info["amount"])

def parse_value(value, value_type):
    if value == 'None':
        return None
    if value_type == int:
        return int(value)
    if value_type == bool:
        return value == 'True'
    return value

def read_file(input_file) -> list:
    card_list = []
    with open(input_file, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            parsed_row = {
                'name': row['name'],
                'number': parse_value(row['number'], int),
                'set_total': parse_value(row['set_total'], int),
                'amount': parse_value(row['amount'], int),
                'promo': parse_value(row['promo'], bool)
            }
            card_list.append(parsed_row)
    return card_list

def add_to_db_from_file(db_manager, card_generator, input_file):
    '''read file and store cards in db'''
    card_list = read_file(input_file)
    card_ids_added = []

    for card in card_list:
        print(card)
        sdk_card = card_generator.get_card_details(name=card["name"], number=card["number"], set_total=card["set_total"], promo=bool(card["promo"]))
        for _ in range(card["amount"]):
            sdk_card_id = db_manager.add_card(sdk_card)
        card_ids_added.append(sdk_card_id)
        print(f"card id: {sdk_card_id}")

    # db_manager.show_cards_from_ids(card_ids=card_ids_added)
def add_to_db_from_input(db_manager, card_generator):
    '''read file and store cards in db'''
    card_ids_added = []
    deck_id = manager.get_deck_id_by_name("Dark1")[0]
    sdk_card = card_generator.get_card_details(name="Xerosic's Machinations", number=64, set_total=64, promo=False)
    for _ in range(2):
        sdk_card_id = db_manager.add_card(sdk_card)
        manager.move_card_to_deck(deck_id=deck_id, card_id=sdk_card_id, count=1)
    card_ids_added.append(sdk_card_id)
    print(f"card id: {sdk_card_id}")
def add_cards_to_database(db_manager, card_generator, input_file=None):
    '''Read Cards from csv file and insert then into the database'''
    if input_file:
        add_to_db_from_file(db_manager, card_generator, input_file)

def move_cards_from_input_to_deck(manager, deck_name) -> list:
    deck_id = manager.get_deck_id_by_name(deck_name)[0]
    failed_cards = []
    if not deck_id:
        print("no deck found")
        return
    
    # move cards in db to new deck
    card_id = manager.get_card_id_by_name("Xerosic's Machinations", 64)[0]
    print(card_id)
    # if card_id:
    #     manager.move_card_to_deck(deck_id, card_id, 2)
    # else:
    #     failed_cards.append(("Xero", 64))
        
    # return failed_cards

def move_cards_from_file_to_deck(manager, input_file, deck_name) -> list:
    card_list = read_file(input_file)
    deck_id = manager.get_deck_id_by_name(deck_name)
    failed_cards = []
    if not deck_id:
        deck_id = manager.create_deck(deck_name)
    
    # move cards in db to new deck
    for card in card_list:
        card_id = manager.get_card_id_by_name(card["name"], card["number"])
        if card_id:
            manager.move_card_to_deck(deck_id, card_id[0], card["amount"])
        else:
            failed_cards.append((card["name"], card["number"]))
    return failed_cards
        

def add_cards_to_database(manager, card_generator):
    # add_to_db_from_file(manager, card_generator, "water_deck.csv")
    # add_to_db_from_file(manager, card_generator, "dark_deck.csv")
    # add_to_db_from_file(manager, card_generator, "gardevoir_deck.csv")
    # add_to_db_from_file(manager, card_generator, "basic_energy.csv")
    # move_cards_from_file_to_deck(manager, "water_deck.csv", "Water1")
    # move_cards_from_file_to_deck(manager, "dark_deck.csv", "Dark1")
    move_cards_from_file_to_deck(manager, "gardevoir_deck.csv", "Gardevoir")
    print(manager)

def remove_cards_from_db_test(manager):
    print(manager.show_cards())
    name = "Xerosic's Machinations"
    number = 64
    # set_total = 198
    card_id = manager.get_card_id_by_name(name, number)[0]
    card = manager.get_card_by_id(card_id)
    print(card)
    inp = input("Above card will be deleted, proceed? \nY / N : ")
    if inp != 'Y':
        print("cancelling")
        return
    
    manager.delete_card(card_id)
    print("card deleted")
    print(manager)

def remove_cards_from_deck(manager):
    deck_id = manager.get_deck_id_by_name("Dark1")[0]
    card_name = "Bloodmoon Ursaluna ex"
    card_number = 141
    card_id = manager.get_card_id_by_name(card_name, card_number)[0]
    card = manager.get_card_by_id(card_id)
    print(card)
    inp = input("Above card will be deleted, proceed? \nY / N : ")
    if inp != 'Y':
        print("cancelling")
        return
    
    manager.remove_card_from_deck(deck_id, card_id, 1)
    print("card removed from deck")
    print(manager)


# Model method
class CardModel:
    def __init__(self):
        self.database = CardDatabase("test_db.db")
    def get_cards_raw(self):
        # Fetch cards from database
        return self.database.execute("SELECT id, name, deck_id FROM cards")

# Controller method
class CardController:
    def __init__(self) -> None:
        self.model = CardModel()
    def get_cards_formatted(self):
        cards_raw = self.model.get_cards_raw()
        cards_formatted = {card['id']: card for card in cards_raw}
        return cards_formatted

# View method
class CardView:
    def __init__(self) -> None:
        self.controller = CardController()
    def display_cards(self):
        cards = self.controller.get_cards_formatted()
        for card_id, card_info in cards.items():
            print(f"Card ID: {card_id}, Card Name: {card_info['name']}")

def test(manager):
    card_id = 2
    print(manager.get_card_details_with_similar_cards(card_id=card_id))




# Usage example
if __name__ == '__main__':
    db_path = "test_db.db"
    manager = CardDatabase(db_path)    
    # card_generator = CardGenerator()
    # print(manager)
    # manager.show_cards_in_deck(deck=(7,"water1"))
    test(manager=manager)


'''
1) open packs and add new cards to database -> add_cards_to_database(db_manager, card_generator, deck_name=None, deck_amount=None):
2) give csv of new deck with card name, number, set_total, promo, amount etc
   - find each card and move card x amount to the deck
   - new cards can be included in the cards list, 
        - check db first, then fetch new card


'''