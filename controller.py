
from card_database import CardDatabase
from CardGenerator import CardGenerator
import csv

class Controller:
    def __init__(self) -> None:
        self.db = CardDatabase("test_db.db")
        self.card_generator = CardGenerator()

    def add_to_db_from_input(self, card_name, card_number, set_total, amount, is_promo=False) -> None:
        '''
            Finds the card from the given input and tells the database to store the card
            Input from: DeckManagerApp.add_card_button_press_event()
        '''
        card_ids_added = [] # for reference regarding added cards
        # Find card from sdk and then store in databse, input might be incorrect yielding no sdk_card
        try:
            # query pokemon tcg sdk
            sdk_card = self.card_generator.get_card_details(name=card_name, number=card_number, set_total=set_total, promo=bool(is_promo))
            if not sdk_card:
                print(f"contoller.add_to_db_from_input :: bad input\n{card_name}, {card_number}/{set_total}")
                return 
            
            # add amount of cards to the database
            for _ in range(int(amount)):
                db_card_id = self.db.add_card(sdk_card)
                print(f"new card id: {db_card_id}")
                card_ids_added.append(db_card_id)
            return card_ids_added

        except Exception as e:
            print("error in Controller.add_to_db_from_input()")
            print(f"Exception: {e}")
            return card_ids_added
        
    def create_deck_from_input(self, deck_name) -> int:
        '''
            tells the db to make a new deck entry
            returns deck_id
        '''
        deck_id = self.db.create_deck(deck_name=deck_name)
        print(f'new deck_id: {deck_id}')
        return deck_id
        
    def get_card(self, card_id):
        card = self.db.get_card_by_id(card_id=card_id)
        return {"name": card[1], "number": card[2], "set_total": card[3], "super_type":card[4], "card_type": card[5], "sub_type":card[6], "rarity":card[9]}
    
    def get_cards(self, deck_id=-1, filters=[]):
        '''
            Query database for cards. 
            returns list of dictionaries of unique cards
        '''
        db_cards = self.db.get_cards_with_detailed_amount(deck_id=deck_id, filters=filters)
        cards = [
                    {
                        "name": row[0],
                        "number": row[1],
                        "set_total": row[2],
                        "super_type": row[3],
                        "card_type": row[4],
                        "sub_type": row[5],
                        "image_path": row[6],
                        "all_card_ids":row[7],
                        "not_in_deck_ids":row[8],
                        "rarity":row[9],
                        "ability":self.get_ability(card_id=row[10])
                    }
                    for row in db_cards
                ]
        return sorted(cards, key=lambda card: card["name"])
            
    def get_decks(self,deck_id=-1):
        '''
        query database for decks
        returns dict of decks
        '''
        decks = {
            row[0]:{
                "name": row[1]
            }
            for row in (self.db.get_decks(deck_id=deck_id))
        }
        return decks
    
    def move_card_to_deck(self, deck_name, card_info, amount):

        deck_id = self.db.get_deck_id_by_name(deck_name)[0]
        if deck_id:
            for _id in card_info["not_in_deck_ids"][:amount]:
                print(f"moving card_id: {_id} to deck_id: {deck_id}")
                self.db.move_card_to_deck(deck_id=deck_id, card_id=_id, count=1)
        else:
            print(f"invalid deck_id: {deck_id}")
        

    def remove_card(self, deck_id, card, amount):
        '''
            removes card_ids from decks or from the database entirely
        '''
        print("in controller remove_card()")
        print(f'deck_id: {deck_id}')
        print(f'card: {card}')

        if deck_id != -1:
            # only remove from deck
            card_ids = self.db.get_in_deck_card_ids(card=card,deck_id=deck_id) # tuple of matching cards in deck
            print(f'card ids in deck {card_ids}')
            for _id in card_ids[:amount]:
                print(self.db.remove_card_from_deck(deck_id=deck_id, card_id=_id))
            return 
        # view is all cards -> delete from database
        if deck_id == -1:
            for _id in card["not_in_deck_ids"][:amount]:
                print(self.db.delete_card(card_id=_id))
            return
    
    
    def load_cards_from_csv(self, csv_file='cards.csv'):
        '''
            import cards from csv. 
            name,number,set_total,amount
        '''
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name=row['name']
                number=row['number']
                set_total=row['set_total'] if row['set_total'] != "None" else None
                amount=row['amount']
                try:
                    promo=row['promo']
                except KeyError:
                    promo=False
                
                    
                self.add_to_db_from_input(card_name=name, card_number=number, set_total=set_total, amount=amount, is_promo=promo)
    
    def load_decks_from_csv(self, csv_file='decks.csv'):
        '''
            for each card, find the card in the databse using the csv to get atributes (mimic clicking on a card)
            then pass that card_info to self.move_card_to_deck
        '''
        print(f'in controller load_decks csv_file: {csv_file}')
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                db_card = self.db.get_card_info_by_name(name=row['name'], number=row['number'])
                card_info = {
                    "name": db_card[0],
                    "number": db_card[1],
                    "set_total": db_card[2],
                    "super_type": db_card[3],
                    "card_type": db_card[4],
                    "sub_type": db_card[5],
                    "image_path": db_card[6],
                    "all_card_ids": db_card[7],
                    "not_in_deck_ids":db_card[8]
                    }
                deck_exists = self.db.get_deck_id_by_name(row['deck_name'])
                if not deck_exists:
                    print(f"deck name: {row['deck_name']} does not exist. Creating new deck...")
                    self.db.create_deck(deck_name=row['deck_name'])
                print(f"moving {card_info['name']}, {card_info['number']}/{card_info['set_total']} to deck: {row['deck_name']}")
                self.move_card_to_deck(deck_name=row['deck_name'], card_info=card_info, amount=int(row['amount']))

    def get_ability(self, card_id):
       
        ability = self.db.get_ability(card_id=card_id)
        if ability is None:
            return None
        
        ret_ability = {
            "name":ability[0],
            "description":ability[1]
        }
        return ret_ability