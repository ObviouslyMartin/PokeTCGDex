import sqlite3
import csv
import pandas as pd
import io
from CardGenerator import CardGenerator
import logging
logger = logging.getLogger(__name__)

class CardDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.__create_tables()
        self.__create_indexes()

    def __create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            number INTEGER NOT NULL,
            set_total INTEGER NOT NULL,
            super_type TEXT NOT NULL,
            card_type TEXT,
            sub_type TEXT NOT NULL,
            image_url TEXT NOT NULL,
            image_path TEXT NOT NULL,
            rarity TEXT NOT NULL,
            quantity INTEGER NOT NULL 
        );
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            set_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            series TEXT NOT NULL,
            image_url TEXT NOT NULL,
            image_path TEXT NOT NULL
        );
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            UNIQUE(name)
        );
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS deck_cards (
            deck_id INTEGER,
            card_id INTEGER,
            quantity INTEGER,
            PRIMARY KEY (deck_id, card_id),
            FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE CASCADE,
            FOREIGN KEY (card_id) REFERENCES cards (id) ON DELETE CASCADE
        );
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS set_cards (
            set_id INTEGER,
            card_id INTEGER,
            PRIMARY KEY (set_id, card_id),
            FOREIGN KEY (set_id) REFERENCES sets (id) ON DELETE CASCADE,
            FOREIGN KEY (card_id) REFERENCES cards (id) ON DELETE CASCADE
        );
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS abilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            type TEXT NOT NULL
        );
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS card_abilities (
            card_id INTEGER,
            ability_id INTEGER,
            PRIMARY KEY (ability_id, card_id),
            FOREIGN KEY (ability_id) REFERENCES abilities (id) ON DELETE CASCADE,
            FOREIGN KEY (card_id) REFERENCES cards (id) ON DELETE CASCADE
        );
        ''')
        
        self.conn.commit()
        # self.conn.close()
    
    def __create_indexes(self):
        # Indexes for optimizing queries on commonly searched fields
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_cards_name_number_set ON cards (name, number, set_total);")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_deck_cards_deck_id ON deck_cards (deck_id);")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_deck_cards_card_id ON deck_cards (card_id);")
        self.conn.commit() 
    def close_connection(self):
        '''Close the database connection when no longer needed.'''
        self.conn.close()

    ########################################################
    ''' Add to DB '''
    ########################################################
    def add_card(self, new_card: dict, quantity) -> int:
        ''' 
        add new card or update count if already exists
        returns id of the last accessed id
        '''
        # Insert a new row if the card does not exist <count> times
        card_id = self.__get_card_id_by_name(name=new_card["name"], number=new_card["number"])
        if card_id:
            # Card exists, update the quantity
            return self.__update_card(card_id[0], quantity) 
        else:
            card_id = self.__insert_card(new_card, quantity)
            self.__update_sets(new_card["set_id"], new_card["set_name"], new_card["set_series"], new_card["set_image_url"], new_card["set_image_path"],card_id=card_id)
            if new_card["ability"] is not None:
                self.__update_abilities(new_card["ability"], card_id=card_id)
            self.conn.commit()
            return card_id
        
    def __update_card(self, card_id: int, quantity: int):
        ''' Add new quantity to current quantity '''
        old_q = self.get_quantity(card_id=card_id)
        new_quantity = old_q + (quantity)  # Default to adding one more card #quatity
        self.cursor.execute("UPDATE cards SET quantity = ? WHERE id = ?", (new_quantity, card_id)) #id
        return self.cursor.lastrowid
    
    def __insert_card(self, card: dict, quantity: int):
        ''' Returns ID of new card'''
        self.cursor.execute(
            "INSERT INTO cards (name, number, set_total, super_type, card_type, sub_type, image_url, image_path, rarity, quantity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                card["name"], card["number"], card["set_total"],
                card["super_type"], card["card_type"], card["sub_type"],
                card["image_url"], card["image_path"], card["rarity"],
                quantity
            )
        )
        card_id = self.cursor.lastrowid  # Get the last inserted id
        return card_id
    
    def create_deck(self, deck_name) -> int:
        '''Adds a new deck to the database and returns its ID'''
        deck_id = self.__get_deck_id_by_name(deck_name)
        if deck_id:
            return deck_id
        self.cursor.execute(
            "INSERT INTO decks (name) VALUES (?)", (deck_name,)
        )
        deck_id = self.cursor.lastrowid  # Get the last inserted id
        self.conn.commit()
        return deck_id
      
    
    def __add_ability(self, ability):
        query = """INSERT INTO abilities (name, description, type) VALUES (?, ?, ?)"""
        self.cursor.execute(query, (ability["name"], ability["text"], ability["type"]))
        self.conn.commit()
        return (self.cursor.lastrowid,)
    
    def __assocaite_ability(self,card_id,ability_id):
        self.cursor.execute(
            """INSERT INTO card_abilities (card_id, ability_id) VALUES (?, ?)""",
            (card_id, ability_id)
        )
        self.conn.commit()
        return "Ability added successfully"
    
    def __add_card_to_set(self, set_uid, card_id):

        self.cursor.execute(
            """INSERT INTO set_cards (set_id, card_id) VALUES (?, ?)""",
            (set_uid, card_id)
        )
        
        self.conn.commit()
        return "Card added to set successfully"


    

    ########################################################
    ''' Get things '''
    ########################################################
    def get_cards_with_detailed_amount(self, deck_id=-1, filters=[]):
        """
            Retrieves a list of cards from the cards table and augments each entry with two lists:
            1) all_card_ids: All card_ids that match name, number, and set_total in the cards table.
            2) not_in_deck_ids: All card_ids that match name, number, and set_total and are not associated with any deck.
            
            If a deck_id is provided, filters the cards to those associated with that deck.
        """

        # Common SELECT part of the SQL query
        base_query = """
            SELECT
                cards.name,
                cards.number, 
                cards.set_total,
                cards.super_type,
                cards.card_type,
                cards.sub_type,
                cards.image_path,
                cards.rarity,
                cards.id
            FROM cards
        """
        base_query = self.__apply_filters(base_query, filters)
        # Conditional WHERE clause depending on whether deck_id is provided
        if deck_id == -2:
            query = f"{base_query} AND cards.id NOT IN (SELECT card_id FROM deck_cards) GROUP BY name, number, set_total"
            self.cursor.execute(query)
        elif deck_id == -1:
            # Fetch all cards without deck filtering
            query = f"{base_query} GROUP BY cards.name, cards.number, cards.set_total"
            self.cursor.execute(query)
        else:
            # Fetch cards specifically from the given deck
            query = f"{base_query} JOIN deck_cards ON cards.id = deck_cards.card_id WHERE deck_cards.deck_id = ? GROUP BY cards.name, cards.number, cards.set_total"
            self.cursor.execute(query, (deck_id,))
            

        # Fetch and return results
        results = self.cursor.fetchall()
        return results

    def find_card(self,name, number):
        ''' Returns True or False if the card with the given name and number exists'''
        found = self.__get_card_id_by_name(name=name, number=number)
        if found:
            return True
        return False
    def __get_card_id_by_name(self, name, number):
        '''returns card id of input name and number'''
        # SQL query to fetch the specified card details along with all matching card_ids
        query = """
            SELECT 
                id
            FROM cards
            WHERE name = ? AND number = ?
        """
        self.cursor.execute(query, (name, number))
        
        # Fetch and return results
        result = self.cursor.fetchone()
        return result
    
    
    def get_quantity(self, card_id, deck_id=-1):
        '''Returns quantity of cards in db or cards in a deck if given a deck id '''
        if deck_id==-1:
            self.cursor.execute("SELECT quantity FROM cards WHERE id = ?", (card_id,))
        else:
            self.cursor.execute("SELECT quantity FROM deck_cards WHERE card_id = ? AND deck_id = ?", (card_id, deck_id))
        count = self.cursor.fetchone()
        if count:
            return count[0]
        else:
            return 0
        
    
    def __get_all_card_ids(self)-> tuple | None:
        '''Returns all card ids'''
        self.cursor.execute("SELECT id FROM cards")
        return self.cursor.fetchall()
    
    def __card_exists(self, name=None, number=None, set_total=None, card_id=None) -> tuple | None:
        '''Returns Id and Quantity of the given card'''
        if card_id:
            self.cursor.execute("SELECT id, quantity FROM cards WHERE id = ?", (card_id,))    
        else:    
            self.cursor.execute("SELECT id, quantity FROM cards WHERE name = ? AND number = ? AND set_total = ?", (name, number, set_total))
        result = self.cursor.fetchone()
        return result
    
    def __check_card(self, card_id):
        self.cursor.execute(
            """SELECT * FROM cards WHERE id = ?""",
            (card_id,)
        )
        card_details = self.cursor.fetchone()
        return card_details
    

    def get_decks(self):
        '''
        Gets all deck names and ids in database
        returns list of tuple objects for each deck
        [(id, name),...]
        '''
        self.cursor.execute("SELECT id, name FROM decks")
        decks = self.cursor.fetchall()
        return decks
    
    def find_deck(self, deck_name):
        ''' returns True or False if the deck exists or not'''
        found = self.__get_deck_id_by_name(deck_name=deck_name)
        return found != None
    
    def __get_deck_id_by_name(self, deck_name) -> tuple | None:
        '''returns (id,) of the deck or None if not found'''
        self.cursor.execute("SELECT id FROM decks WHERE name = ?", (deck_name,))
        return self.cursor.fetchone()
    
    def __get_quantity_in_deck(self, deck_id, card_id):
        ''' return tuple of the amount of a specific card in a deck'''
        self.cursor.execute("SELECT quantity FROM deck_cards WHERE deck_id = ? AND card_id = ?", (deck_id, card_id))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0

    
    
    def __get_all_deck_ids(self)-> tuple | None:
        ''' return tuple of all deck ids'''
        self.cursor.execute("SELECT id FROM decks")
        return self.cursor.fetchall()
    
    def __get_deck_size(self, deck_id)-> int:
        '''returns the total number of cards in a deck'''
        self.cursor.execute("SELECT SUM(quantity) as total_cards FROM deck_cards WHERE deck_id = ?", (deck_id,))
        result = self.cursor.fetchone()
        if not result:
            return 0
        if result[0] == None:
            return 0
        return result[0]
    
    def __deck_exists(self, deck_id) -> tuple | None:
        ''' return deck id o'''
        self.cursor.execute("SELECT id FROM decks WHERE id = ?", (deck_id,))
        return self.cursor.fetchone()
    
    
    def get_ability(self, card_id):
        query = """
        SELECT 
            abilities.name, 
            abilities.description
        FROM abilities
        JOIN card_abilities ON card_abilities.ability_id = abilities.id 
        WHERE card_abilities.card_id = ?
        """
        self.cursor.execute(query, (card_id,))
        return self.cursor.fetchone()
    
    def __find_ability(self, name):
        query = """SELECT id FROM abilities WHERE name = ?"""
        self.cursor.execute(query, (name,))
        return self.cursor.fetchone()
    def __find_set(self, set_id):
        self.cursor.execute("""SELECT * from sets where set_id = ?""", (set_id,))
        return self.cursor.fetchone()


    ########################################################
    ''' Remove items '''
    ########################################################

    # def remove_all(self):
    #     inp = input("WARNING: This cannot be undone. Proceed?\nY / N: ")
    #     if inp != 'Y':
    #         print("Aborting...")
    #         return
        
    #     print("Emptying the database...")
    #     cards = [_id[0] for _id in self.__get_all_card_ids()]
    #     decks = [_id[0] for _id in self.__get_all_deck_ids()]
    #     for card in cards:
    #         self.delete_card(card_id=card)
    #     for deck in decks:
    #         self.delete_deck(deck_id=deck)

    def remove_card_from_deck(self, deck_id, card, amount):
        # ensure card exists
        card_id = self.__get_card_id_by_name(name=card["name"], number=card["number"])
        if not card_id: 
            return 0
        quantity = self.get_quantity(card_id=card_id[0], deck_id=deck_id)
        if deck_id!=-1:
            if quantity <= amount:
                # delete all
                self.cursor.execute(
                    "DELETE FROM deck_cards WHERE deck_id = ? AND card_id = ?", (deck_id, card_id[0])
                )
            else:
                new_quantity = quantity - amount
                self.cursor.execute("UPDATE deck_cards SET quantity = ? WHERE deck_id = ? AND card_id = ?", (new_quantity, deck_id, card_id[0]))
        else:
            if quantity <= amount:
                self.cursor.execute("DELETE FROM cards WHERE id = ?", (card_id[0],))
            else:
                new_quantity = quantity - amount
                self.cursor.execute("UPDATE cards SET quantity = ? WHERE id = ?", (new_quantity, card_id[0],))
        self.conn.commit()
        return self.cursor.rowcount  # Returns the number of rows affected
    
    def __delete_card(self, card_id):
        logger.info(f"DB: about to delete {card_id}")
        exists = self.__check_card(card_id=card_id)
        if not exists:
            return 0
        self.cursor.execute(
            "DELETE FROM cards WHERE id = ?", (card_id,)
        )

        self.conn.commit()
        return self.cursor.rowcount  # Returns the number of rows affected

    def delete_deck(self, deck_id):
        exists = self.__check_card(deck_id=deck_id)
        if not exists:
            return 0
        self.cursor.execute(
            "DELETE FROM decks WHERE id = ?", (deck_id,)
        )
        self.conn.commit()
        return self.cursor.rowcount  # Returns the number of rows affected

    ####################
    ''' Update Items '''
    ####################
    def move_card_to_deck(self, deck_name, card, count):
        card_id = self.__get_card_id_by_name(card["name"], card["number"])
        deck_id = self.__get_deck_id_by_name(deck_name)
        if deck_id and card_id:
            logger.info(f"moving card_id: {card_id} to deck_id: {deck_id}")
            return self.__move_card_to_deck(deck_id=deck_id[0], card_id=card_id[0], count=count)
        logger.info(f"Could not move card_id: {card_id} to deck_id: {deck_id}")
        return "Card or Deck not found"
    
    def __move_card_to_deck(self, deck_id, card_id, count):
        
        if not self.__can_add_to_deck(deck_id, card_id, count):
            return "Cannot add more than 4 of the same card or exceed the deck limit of 60 cards"
        card_already_in_deck = self.__get_quantity_in_deck(deck_id,card_id)
        if card_already_in_deck:
            # Card already in the deck, update the quantity
            new_quantity = card_already_in_deck[0] + count
            self.cursor.execute("UPDATE deck_cards SET quantity = ? WHERE deck_id = ? AND card_id = ?", (new_quantity, deck_id, card_id))
        else:
            self.cursor.execute(
                "INSERT INTO deck_cards (deck_id, card_id, quantity) VALUES (?, ?, ?)",
                (deck_id, card_id, count)
            )
        
        self.conn.commit()
        return "Card added successfully"
    
    
    def __update_sets(self, set_id, set_name, set_series, set_image_url, set_image_path, card_id):
        '''
            add new card to a set.
            create new entry for new set or update existing 
        '''
        set_exists = self.__find_set(set_id)
        if set_exists:
            self.__add_card_to_set(set_uid=set_exists[0], card_id=card_id)
            return set_exists
        self.cursor.execute(
            (
            '''
            INSERT INTO sets 
                (set_id, name, series, image_url, image_path) 
                VALUES (?, ?, ?, ?, ?)'''
            ),
            (set_id, set_name, set_series, set_image_url, set_image_path)
        )
        self.conn.commit()
        set_uuid = self.cursor.lastrowid  # Get the last inserted uuid
        return set_uuid
    
    def __update_abilities(self, abilities, card_id):
        # find ability and insert new if not found
        for ability in abilities:
            ability_id = self.__find_ability(ability["name"])
            if not ability_id:
                ability_id = self.__add_ability(ability)
            # associate cards with ability
            self.__assocaite_ability(card_id, ability_id[0])

    
    ########################################################
    ''' Show items '''
    ########################################################

    def __str__(self) -> str:
        # ret_string = self.__show_decks_table() + self.__show_cards_table() 
        # ret_string += f'\nTotal Cards: {self.get_total_card_count()[0]}'
        # ret_string += f'\nTotal Decks: {self.get_total_deck_count()[0]}'
        # # ret_string += self.__show_deck_cards_table(deck_id=1)
        """Displays the structure and contents of all tables in a SQLite database."""
        return self.__display_database_info_pandas_string()

    def __display_database_info_pandas_string(self):
        """Displays the structure and contents of all tables in the SQLite database using pandas and returns the result as a string."""
        output = io.StringIO()

        # Get a list of all tables in the database
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = pd.read_sql(query, self.conn)

        for table_name in tables['name']:
            output.write(f"\nTable: {table_name}\n" + "-" * 40 + "\n")

            # Get the table schema using PRAGMA
            schema = pd.read_sql(f"PRAGMA table_info({table_name})", self.conn)
            output.write("Columns:\n")
            for index, row in schema.iterrows():
                output.write(f"  {row['name']} ({row['type']})\n")

            # Print contents of the table
            table_contents = pd.read_sql(f"SELECT * FROM {table_name}", self.conn)
            if not table_contents.empty:
                output.write("\nContents:\n")

                # Set max column width for display
                pd.set_option('display.max_colwidth', 50)  # Adjust column width to 50 characters
                pd.set_option('display.width', None)  # Use automatic line width detection
                pd.set_option('display.expand_frame_repr', True)  # Disable wrapping of the frame onto multiple lines

                output.write(table_contents.to_string(index=False) + "\n")
            else:
                output.write("  No data\n")

        # Reset display options to default
        pd.reset_option('display.max_colwidth')
        pd.reset_option('display.width', None)  # Use automatic line width detection
        pd.reset_option('display.expand_frame_repr')

        # Get the entire string from StringIO
        contents = output.getvalue()
        output.close()
        return contents
    
    ########################################################
    ''' Private items '''
    ########################################################
    
    
    def __apply_filters(self, base_query, filters):
        if 'name' in filters:
            base_query += f"WHERE cards.name like '%{filters['name']}%'"
        # if 'super_types' in filters:
        #     base_query += f" WHERE cards.super_type IN {self.__format_filter(filters, 'super_types')}"
        # if 'color' in filters and 'sub_type' not in filters:
        #     base_query += f" AND cards.card_type IN {self.__format_filter(filters, 'color')}"
        # elif 'sub_type' in filters and 'color' not in filters:
        #     base_query += f" AND cards.sub_type IN ({self.__format_filter(filters, 'sub_type', comma_list=True)}"
        # elif 'color' in filters and 'sub_type' in filters:
        #     base_query += f" AND (cards.sub_type IN ({self.__format_filter(filters, 'sub_type')} OR cards.card_type IN {self.__format_filter(filters, 'color')})"
        # print(f"base_query: {base_query}")
        return base_query
   
    def __format_filter(self, filters, item, comma_list=False):
        # Retrieve the list of super types from the dictionary or default to an empty list if not present
        
        
        filter_items = filters.get(item, [])
        if comma_list:
            filter_items = filter_items.split(',')
        # Format each element in the list as a quoted string for SQL compatibility
        formatted_types = [f"'{stype}'" for stype in filter_items]

        # Join all formatted elements into a comma-separated string, enclosed in parentheses
        formatted_string = f"({', '.join(formatted_types)})"

        return formatted_string

   
    def __is_energy_card(self, card_id) -> bool:
        '''
            returns is the card_id a basic energy card?
        '''
        self.cursor.execute("Select sub_type, super_type FROM cards WHERE id = ?", (card_id,))
        card = self.cursor.fetchone()
        # print(f'super_type == {super_type[0]}')

        return ("Basic" in card[0]) and (card[1] == "Energy")
    
    def __can_add_to_deck(self, deck_id, card_id, count) -> bool:
        ''' 
            Check if adding to deck exceeds constraints
            Check current total number of cards in the deck
        '''
        # if not self.__deck_exists(deck_id):
        #     return False
        # if not self.__card_exists(card_id=card_id):
        #     return False
        
        deck_size = self.__get_deck_size(deck_id)

        if deck_size + count > 60:
            return False
        
        # Is basic energy?
        if self.__is_energy_card(card_id):
            return True
        
        # Check current number of this card in the deck
        current_card_count = self.__get_quantity_in_deck(deck_id, card_id)
        if current_card_count + count > 4:
            return False

        return True
    
    def to_csv(self):

        self.__generate_cards_csv()
        self.__generate_decks_csv()

    def __generate_cards_csv(self):
        query = """
            SELECT name, number, set_total, COUNT(*) as amount
            FROM cards
            GROUP BY name, number, set_total
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        with open('cards.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['name', 'number', 'set_total', 'amount'])
            writer.writerows(rows)

    def __generate_decks_csv(self):
        # Modified SQL query to include the count of matching cards within each deck
        query = """
            SELECT 
                decks.name as deck_name, 
                cards.name as card_name, 
                cards.number as card_number, 
                cards.set_total as card_set_total,
                COUNT(*) as amount
            FROM deck_cards
            JOIN decks ON deck_cards.deck_id = decks.id
            JOIN cards ON deck_cards.card_id = cards.id
            GROUP BY decks.id, cards.name, cards.number, cards.set_total
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        with open('decks.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['deck_name', 'name', 'number', 'set_total', 'amount'])  # Include the header for amount
            writer.writerows(rows)

if __name__ == '__main__':
    print("nothing to run")