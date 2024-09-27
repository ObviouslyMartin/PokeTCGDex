
# from card_database import CardDatabase
from card_database import CardDatabase
from CardGenerator import CardGenerator
import csv
import logging
import time
logger = logging.getLogger(__name__)
SLEEP_LENGTH = 2
class Controller:
    def __init__(self, db_path) -> None:
        self.db = CardDatabase(db_path=db_path)
        self.card_generator = CardGenerator()

    def add_to_db_from_input(self, card_name, card_number, set_total, amount, is_promo=False, deck_id=None) -> None:
        '''
            Finds the card from the given input and tells the database to store the card
            Input from: DeckManagerApp.add_card_button_press_event()
        '''

        logging.debug(f'fetching {card_name}, {card_number}/{set_total} from SDK')
        sdk_card = self.card_generator.get_card_details(name=card_name, number=card_number, set_total=set_total, promo=bool(is_promo))
        if not sdk_card:
            logging.debug(f'Could not fetch {card_name}, {card_number}/{set_total} from SDK')
            print(f"contoller.add_to_db_from_input :: bad input\n{card_name}, {card_number}/{set_total}")
            return
        
        # add amount of cards to the database
        logging.debug(f'Adding {card_name}, {card_number}/{set_total} to database')
        if deck_id:
            deck_id, db_card_id = self.db.manage_deck(deck_name=deck_id)
        else:
            db_card_id = self.db.manage_card(card_info=sdk_card, quantity=int(amount))
        return db_card_id
        
    def create_deck_from_input(self, deck_name) -> int:
        '''
            tells the db to make a new deck entry
            returns deck_id
        '''
        deck_id = self.db.manage_deck(deck_name=deck_name)
        logger.info(f'new deck_id: {deck_id}')
        return deck_id

    
    def get_cards(self, deck_id=None, filters=[]):
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
                        "rarity":row[7],
                        "ability":self.get_ability(card_id=row[8]),
                        "quantity":self.db.get_quantity(deck_id=deck_id, card_id=row[8])
                    }
                    for row in db_cards
                ]
        return sorted(cards, key=lambda card: card["name"])
            
    def get_decks(self):
        '''
        query database for decks
        returns dict of decks
        '''
        decks = {
            row[0]:{
                "name": row[1]
            }
            for row in (self.db.get_decks())
        }
        return decks
    
    def move_card_to_deck(self, deck_name, card_info, amount):
        return self.db.manage_deck(deck_name=deck_name, card=card_info, quantity=amount)
        
    
    def remove_card(self, deck_id, card, amount):
        '''
            removes card_ids from decks or from the database entirely
        '''
        if deck_id != None:
            removed = self.db.manage_card_removal(deck_id=deck_id, card_info=card, quantity=amount)
        else:
            removed = self.db.manage_card_removal(card_info=card, quantity=amount)
        logger.info(f'removed {removed} from deck')
    
    def load_cards_from_csv(self, csv_file='cards.csv'):
        '''
            import cards from csv. 
            name,number,set_total,amount
        '''
        # Count the number of lines in the CSV file
        with open(csv_file, 'r', encoding='utf-8') as file:
            total_lines = len(file.readlines())
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
                if total_lines >= 30:
                    time.sleep(2)
    def load_decks_from_csv(self, csv_file='decks.csv'):
        '''
            for each card, find the card in the databse using the csv to get atributes (mimic clicking on a card)
            then pass that card_info to self.move_card_to_deck
        '''
        print(f'in controller load_decks csv_file: {csv_file}')
        with open(csv_file, 'r', encoding='utf-8') as file:
                total_lines = len(file.readlines())
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                db_card = self.db.get_card_info_by_name(name=row["name"], number=row["number"])
                if not db_card:
                    # create new card and then move to deck
                    try:
                        promo=row['promo']
                    except KeyError:
                        promo=False
                    db_card = self.add_to_db_from_input(card_name=row['name'], card_number=row['number'], set_total=row['set_total'], amount=row['amount'], is_promo=promo)
                    if total_lines>=30:
                        time.sleep(1)

                print(f"moving {row['name']}, {row['number']}/{row['set_total']} to deck: {row['deck_name']}")
                self.db.manage_deck(deck_name=row['deck_name'], card={"name": row['name'], "number":row['number']}, quantity=int(row['amount']))

    def get_ability(self, card_id):
       
        ability = self.db.get_ability(card_id=card_id)
        if ability is None:
            return None
        
        ret_ability = {
            "name":ability[0],
            "description":ability[1]
        }
        return ret_ability

    def export_db(self):
        self.db.to_csv()