from card_database import CardDatabase
from CardGenerator import CardGenerator
# import csv TODO: Create Export as / Import from CSV

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
            sdk_card = self.card_generator.get_card_details(name=card_name, number=card_number, set_total=set_total, promo=is_promo)
            
            # add amount of cards to the database
            for _ in range(int(amount)):
                db_card_id = self.db.add_card(sdk_card)
                print(f"new card id: {db_card_id}")
                card_ids_added.append(db_card_id)
            print(card_ids_added)

        except:
            print("error in Controller.add_to_db_from_input()")
            # print(sdk_card)
            print(f'db_card_id: {db_card_id}, card_name: {card_name}\ncard_number: {card_number}\nset_total: {set_total}\nis_promo: {is_promo}')
            return
        
    def create_deck_from_input(self, deck_name) -> int:
        '''
        tells the db to make a new deck entry
        returns deck_id
        '''
        deck_id = self.db.create_deck(deck_name=deck_name)
        print(f'new deck_id: {deck_id}')
        print(self.db)
        return deck_id
        
    def get_card(self, card_id):
        card = self.db.get_card_by_id(card_id=card_id)
        return {"name": card[1], "number": card[2], "set_total": card[3], "super_type":card[4], "card_type": card[5], "sub_type":card[6]}

    
    def get_cards(self, deck_id=-1, card_type_filter=[]):
        '''
        query database for cards. 
        returns list of dictionaries of unique cards
        '''
        cards = [
                    {"name": row[0],
                    "number": row[1],
                    "set_total": row[2],
                    "super_type": row[3],
                    "card_type": row[4],
                    "sub_type": row[5],
                    "image_path": row[6],
                    "all_card_ids":list(map(int, row[7].split(','))) if row[7] else [],
                    "not_in_deck_ids":list(map(int, row[8].split(','))) if row[8] else []}
                for row in self.db.get_cards_with_detailed_amount(deck_id=deck_id)
                
        ]
        return cards
            
    
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
        print(f'deck_name: {deck_name}')
        print(f'card_info: {card_info}')
        print(f'amount: {amount}')
        deck_id = self.db.get_deck_id_by_name(deck_name)[0]
        if deck_id:
            for _id in card_info["not_in_deck_ids"][:amount]:
                print(f"moving card_id: {_id} to deck_id: {deck_id}")
                self.db.move_card_to_deck(deck_id=deck_id, card_id=_id,count=1)
        else:
            print(f"invalid deck_id: {deck_id}")
        
        # # find all cards with given name, number, set_total -> list of ids
        # deck_id = self.db.get_deck_id_by_name(deck_name)[0]
        # if not deck_id:
        #     print("no deck found")
        #     return
        # card_ids = self.db.get_card_ids_by_name(card_info["name"], card_info["number"], card_info["set_total"])
        # deck_card_ids = self.db.get_deck_card_ids_by_name(card_info["name"], card_info["number"], card_info["set_total"], deck_id=deck_id)

        # print(f'card_ids: {card_ids}')
        # print(f'deck_card_ids: {deck_card_ids}')
        
        # # add amount of ids to deck for each id not in deck.
        # while amount > 0:
        #     for card_id in card_ids:
        #         if card_id not in deck_card_ids:
        
        #             deck_card_ids.append(card_id)
        #             amount -= 1
        #             break

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
            for _id in card_ids[:amount]:
                print(self.db.remove_card_from_deck(deck_id=7, card_id=_id))
            return 
        # view is all cards -> delete from database
        if deck_id == -1:
            for _id in card["not_in_deck_ids"][:amount]:
                print(self.db.delete_card(card_id=_id))
            return

    # def get_cards_in_deck(self, deck_id=-1, card_type_filters=[]):
        # self.cursor.execute("SELECT * FROM deck_cards where deck_id = ?", (deck_id,))
        # deck_name = self.get_deck(deck_id=deck_id)
        # if deck_name is None:
        #     return {}
        
        # cards = self.db.get_cards_in_deck(deck_id=deck_id)
        # if cards is None:
        #     return {}
        # decks = decks[cards] = [
        #     {"id": card_id, "name": name, "number":number, "set_total":set_total, "image_path":image_path, "count": count} for card_id, name, number, set_total, image_path, count in cards
        # ]
        # cards = {
        #     row[0]: {                               # id
        #         "name": row[1],
        #         "number": row[2],
        #         "set_total": row[3],
        #         "super_type": row[4],
        #         "card_type": row[5],
        #         "sub_type": row[6],
        #         "image_url": row[7],
        #         "image_path": row[8]
        #     }
        #     for row in self.db.get_cards_in_deck(deck_id=deck_id)
        # }
        # return cards
        # deck = {
        #     :[
        #             {
        #                 "name": card[2],
        #                 "number": card[3],
        #                 "set_total":card[4],
        #                 "image_path": card[5],
        #                 "super_type": card[6],
        #                 "amount": card[7]
        #             }
        #         ] for card in cards
        # }
        
        # return deck
    # def parse_value(value, value_type):
    #     if value == 'None':
    #         return None
    #     if value_type == int:
    #         return int(value)
    #     if value_type == bool:
    #         return value == 'True'
    #     return value
    
    # def read_file(self, input_file) -> list:
    #     card_list = []
    #     with open(input_file, mode='r', newline='', encoding='utf-8') as file:
    #         csv_reader = csv.DictReader(file)
    #         for row in csv_reader:
    #             parsed_row = {
    #                 'name': row['name'],
    #                 'number': self.parse_value(row['number'], int),
    #                 'set_total': self.parse_value(row['set_total'], int),
    #                 'amount': self.parse_value(row['amount'], int),
    #                 'promo': self.parse_value(row['promo'], bool)
    #             }
    #             card_list.append(parsed_row)
    #     return card_list
