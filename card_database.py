import sqlite3
import csv
import pandas as pd
import io
import logging
logger = logging.getLogger(__name__)

class CardDatabase():
    def __init__(self, db_path:str):
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
            tcg_set_id TEXT NOT NULL,
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
        ''') # quantity here is per card, id 1 can have 4 (deck_cards.quantity) and 6 cards.quantity
             # total cards in deck count will be generated as needed
        
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

    def __create_indexes(self):
        # Indexes for optimizing queries on commonly searched fields
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_cards_name_number_set ON cards (name, number, set_total);")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_deck_cards_deck_id ON deck_cards (deck_id);")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_deck_cards_card_id ON deck_cards (card_id);")
        self.conn.commit() 

    def close_connection(self):
        '''Close the database connection when no longer needed.'''
        self.conn.close()

    def manage_card(self, card_info: dict, quantity: int):
        """ Manage card insertion or update in one function. """
        try:
            # Check if card already exists
            card_id = self.__get_card_id_by_name(card_info["name"], card_info["number"])
            if card_id:
                self.__update_card_quantity(card_id, quantity, increment=True)
            else:
                card_id = self.__insert_card(card_info, quantity)
                self.__manage_related_data(card_info, card_id)
            self.conn.commit()
            return card_id
        except Exception as e:
            logger.error(f"Failed to manage card: {e}")
            self.conn.rollback()
    def __manage_related_data(self, card_info: dict, card_id: int):
        """ Manage sets and abilities related to the new card """
        if "set_id" in card_info: # set_id is always present, the value is None or populated
            self.__manage_sets(card_info, card_id)
        if card_info["ability"] is not None: # ability is always present, the value is None or populated
            self.__manage_abilities(card_info["ability"], card_id)

    def manage_deck(self, deck_name: str, card: dict = None, quantity: int = 0):
        """ Manages deck creation and card addition in one function. """
        try:
            deck_id = self.__get_deck_id_by_name(deck_name)
            if not deck_id:
                deck_id = self.__insert_deck(deck_name)
            
            if card and quantity > 0:
                card_id = self.__get_card_id_by_name(card["name"], card["number"])
                if not card_id:
                    card_id = self.__insert_card(card_info=card, quantity=quantity)
                self.__move_card_to_deck(deck_id, card_id, quantity)
            self.conn.commit()
            return deck_id, card_id
        except Exception as e:
            logger.error(f"Failed to manage deck: {e}")
            self.conn.rollback()

    def __manage_sets(self, card:dict, card_id:int) -> int:
        '''
            add new card to a set.
            create new entry for new set or update existing 
            returns last row id
        '''
        set_id = self.__get_set_id_by_name(set_name=card["set_name"], set_series=card["set_series"])
        if not set_id:
            set_id = self.__insert_set(card=card) 
        
        self.__add_card_to_set(card_id=card_id, set_uid=set_id) 
        
        self.conn.commit()
        set_uuid = self.cursor.lastrowid  # Get the last inserted set uuid 
        return set_uuid
    
    def __manage_abilities(self, abilities, card_id:int):
        for ability in abilities:
            ability_exists = self.__get_ability_id_by_name(ability["name"]) # ability is a list... TODO: Confirm only Pokemon Break and V - Union
            if not ability_exists:
                ability_id = self.__insert_ability(ability)
            self.__assocaite_ability(card_id, ability_id)

    def __assocaite_ability(self,card_id:int, ability_id:int):
        self.cursor.execute(
            """INSERT INTO card_abilities (card_id, ability_id) VALUES (?, ?)""",
            (card_id, ability_id)
        )
        self.conn.commit()
        return "Ability added successfully"
    
    def __insert_ability(self, ability) -> int | None:
        query = """INSERT INTO abilities (name, description, type) VALUES (?, ?, ?)"""
        self.cursor.execute(query, (ability["name"], ability["text"], ability["type"]))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def __get_ability_id_by_name(self, name:str) -> int | None:
        query = """SELECT id FROM abilities WHERE name = ?"""
        self.cursor.execute(query, (name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    
    def __insert_set(self, card: dict) -> int:
        """ Inserts a new set and returns the card ID. """
        self.cursor.execute("""
            INSERT INTO sets 
                (tcg_set_id, name, series, image_url, image_path) 
            VALUES (?, ?, ?, ?, ?)""",
            (card["set_id"], card["set_name"], card["set_series"], card["set_image_url"], card["set_image_path"])
        )
        return self.cursor.lastrowid

    def __add_card_to_set(self, set_uid:int, card_id:int) -> None:
        """
            insert new row in set_cards table
        """
        self.cursor.execute(
            """INSERT INTO set_cards (set_id, card_id) VALUES (?, ?)""",
            (set_uid, card_id)
        )
        
        self.conn.commit()
    
    def __insert_card(self, card: dict, quantity: int) -> int:
        """ Inserts a new card and returns the card ID. """
        self.cursor.execute("""
            INSERT INTO cards 
            (name, number, set_total, super_type, card_type, sub_type, image_url, image_path, rarity, quantity) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (card["name"], card["number"], card["set_total"],
            card["super_type"], card["card_type"], card["sub_type"],
            card["image_url"], card["image_path"], card["rarity"], quantity))
        return self.cursor.lastrowid

    def __update_card_quantity(self, card_id: int, quantity: int, increment=False) -> None:
        """ Updates the card's quantity. """
        if increment:
            self.cursor.execute("UPDATE cards SET quantity = quantity + ? WHERE id = ?", (quantity, card_id))
        else:
            self.cursor.execute("UPDATE cards SET quantity = ? WHERE id = ?", (quantity, card_id))
 
    def __get_set_id_by_name(self, set_name: str, set_series: str) -> int | None:
        ''' returns interanl uuid of given Pokémon TCG set name and series name'''
        self.cursor.execute("""SELECT id from sets where name = ? AND series = ?""", (set_name, set_series))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    
    def __insert_deck(self, deck_name: str) -> int | None:
        """ Inserts a new deck and returns the deck ID. """
        self.cursor.execute("INSERT INTO decks (name) VALUES (?)", (deck_name,))
        return self.cursor.lastrowid
    def get_card_info_by_name(self, name, number=None, set_total=None):
        self.cursor.execute("""SELECT * FROM cards where name = ? AND number = ? """, (name, number))
        result = self.cursor.fetchall()
        return result


    def __get_card_id_by_name(self, name:str, number:str) -> int | None:
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
        if result:
            return result[0]
        else:
            return None
    
    def __get_deck_id_by_name(self, deck_name:str) -> int | None:
        '''returns (id,) of the deck or None if not found'''
        self.cursor.execute("SELECT id FROM decks WHERE name = ?", (deck_name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    
    def __move_card_to_deck(self, deck_id:int, card_id:int, count:int) -> int | None:
        
        if not self.__can_add_to_deck(deck_id, card_id, count):
             logger.warning("Cannot add more than 4 of the same card or exceed the deck limit of 60 cards")
             return None
        quantity_in_deck = self.__get_quantity_in_deck(deck_id,card_id)
        if quantity_in_deck > 0:
            # Card already in the deck, update the quantity
            new_quantity = quantity_in_deck + count
            self.cursor.execute("UPDATE deck_cards SET quantity = ? WHERE deck_id = ? AND card_id = ?", (new_quantity, deck_id, card_id))
        else:
            self.cursor.execute(
                "INSERT INTO deck_cards (deck_id, card_id, quantity) VALUES (?, ?, ?)",
                (deck_id, card_id, count)
            )
        self.conn.commit()
        return self.cursor.lastrowid
    def __can_add_to_deck(self, deck_id:int, card_id:int, count:int) -> bool:
        ''' 
            Check if adding to deck exceeds constraints
            Check current total number of cards in the deck
        '''
        
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
    
    def __get_deck_size(self, deck_id: int)-> int:
        '''returns the total number of cards in a deck'''
        self.cursor.execute("SELECT SUM(quantity) FROM deck_cards WHERE deck_id = ?", (deck_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0] if result[0] is not None else 0
        else:
            return 0
    
    def __is_energy_card(self, card_id: int) -> bool:
        '''
            returns true if card_id a basic energy card
        '''
        self.cursor.execute("Select sub_type, super_type FROM cards WHERE id = ?", (card_id,))
        card = self.cursor.fetchone()
        # print(f'super_type == {super_type[0]}')

        return ("Basic" in card[0]) and (card[1] == "Energy")

    def __get_quantity_in_deck(self, deck_id: int, card_id:int) -> int:
        ''' return  the amount of a specific card in a deck'''
        self.cursor.execute("SELECT quantity FROM deck_cards WHERE deck_id = ? AND card_id = ?", (deck_id, card_id))
        result = self.cursor.fetchone()
        if result:
            return result[0] if result[0] is not None else 0
        else:
            return 0
    
    def get_cards_with_detailed_amount(self, deck_id=None, filters=[]):
        """
            Retrieves a list of cards from the cards table and augments each entry with two lists:
            1) all_card_ids: All card_ids that match name, number, and set_total in the cards table.
            2) not_in_deck_ids: All card_ids that match name, number, and set_total and are not associated with any deck.
            
            If a deck_id is provided, filters the cards to those associated with that deck.
        """

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
        base_query = self.__apply_filters(base_query, filters, deck_id)

        if deck_id == -2: # depreacted..
            query = f"{base_query} AND cards.id NOT IN (SELECT card_id FROM deck_cards) GROUP BY cards.name, cards.number, cards.set_total"
            # print(f'deck id: {deck_id}, query: {query}')
            self.cursor.execute(query)
        elif deck_id == None:
            # Fetch all cards without deck filtering
            base_query += " GROUP BY cards.name, cards.number, cards.set_total"
            print(f'deck id: {deck_id}, query: {base_query}')
            self.cursor.execute(base_query)
        else:
            # Fetch cards specifically from the given deck
            query = f"{base_query} \n JOIN deck_cards ON cards.id = deck_cards.card_id \n WHERE deck_cards.deck_id = ? \n GROUP BY cards.name, cards.number, cards.set_total"
            # print(f'deck id: {deck_id}, query: {query}')
            self.cursor.execute(query, (deck_id,))
        
        results = self.cursor.fetchall()
        return results
    
    def __apply_filters(self, base_query, filters, deck_id):
        if 'name' in filters:
            base_query += f" WHERE cards.name like '%{filters['name']}%'"
        if 'super_types' in filters:
            base_query += f" WHERE cards.super_type IN {self.__format_filter(filters, 'super_types')}"
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
    def get_decks(self):
        '''
        Gets all deck names and ids in database
        returns list of tuple objects for each deck
        [(id, name),...]
        '''
        self.cursor.execute("SELECT id, name FROM decks")
        decks = self.cursor.fetchall()
        return decks
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
    #####################################
    ''' Update quantity / Remove Items'''
    #####################################
    def manage_card_removal(self, card_info: dict, quantity: int, deck_id=None):
        """ 
            Manages the removal of cards from decks or completely from the database.

            Returns: 
        """
        try:
            card_id = self.__get_card_id_by_name(card_info["name"], card_info["number"])
            if not card_id:
                logger.error("Card does not exist.")
                return 0
            
            if deck_id is not None:
                # Remove from specified deck
                self.__remove_card_from_deck(deck_id, card_id, quantity)
            else:
                # Update or remove card completely from database
                self.__remove_card_completely(card_id, quantity)

            self.conn.commit()
        except Exception as e:
            logger.error(f"Error managing card removal: {e}")
            self.conn.rollback()

    def __remove_card_from_deck(self, deck_id: int, card_id: int, quantity: int):
        """ Removes or adjusts the quantity of a card in a specific deck. """
        current_quantity = self.get_quantity(card_id, deck_id)
        new_quantity = max(current_quantity - quantity, 0)
        if new_quantity > 0:
            self.cursor.execute("UPDATE deck_cards SET quantity = ? WHERE deck_id = ? AND card_id = ?", (new_quantity, deck_id, card_id))
        else:
            self.cursor.execute("DELETE FROM deck_cards WHERE deck_id = ? AND card_id = ?", (deck_id, card_id))
        logger.info("Updated card quantity in deck.")

    def __remove_card_completely(self, card_id: int, quantity: int):
        """ Removes a certain quantity or deletes the card completely if the quantity drops to zero. """
        current_quantity = self.get_quantity(card_id)
        new_quantity = max(current_quantity - quantity, 0)
        if new_quantity > 0:
            self.cursor.execute("UPDATE cards SET quantity = ? WHERE id = ?", (new_quantity, card_id))
        else:
            self.cursor.execute("DELETE FROM cards WHERE id = ?", (card_id,))
            self.cursor.execute("DELETE FROM deck_cards WHERE card_id = ?", (card_id,))  # Ensure all deck references are removed
            self.cursor.execute("DELETE FROM set_cards WHERE card_id = ?", (card_id,))  # Ensure all deck references are removed
            self.cursor.execute("DELETE FROM card_abilities WHERE card_id = ?", (card_id,))  # Ensure all deck references are removed
        logger.info("Card removed or quantity updated.")

    def get_quantity(self, card_id: int, deck_id: int | None =None) -> int:
        """ Retrieves the quantity of a card either in general or from a specific deck. """
        if deck_id != None:
            self.cursor.execute("SELECT quantity FROM deck_cards WHERE card_id = ? AND deck_id = ?", (card_id, deck_id))
        else:
            self.cursor.execute("SELECT quantity FROM cards WHERE id = ?", (card_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0
    
    def get_total_cards(self) -> int:
        """Returns the total count of cards in the database"""
        self.cursor.execute("""SELECT Sum(quantity) FROM cards""")
        result = self.cursor.fetchone()
        return result[0] if result else 0
    
    def __str__(self) -> str:
        # ret_string = self.__show_decks_table() + self.__show_cards_table() 
        # ret_string += f'\nTotal Cards: {self.get_total_card_count()[0]}'
        # ret_string += f'\nTotal Decks: {self.get_total_deck_count()[0]}'
        # # ret_string += self.__show_deck_cards_table(deck_id=1)
        """Displays the structure and contents of all tables in a SQLite database."""
        return self.__display_database_info_pandas_string()

    def __display_database_info_pandas_string(self) -> str:
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

    def to_csv(self):

        self.__generate_cards_csv()
        self.__generate_decks_csv()

    def __generate_cards_csv(self):
        query = """
            SELECT name, number, set_total, quantity as amount
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
                deck_cards.quantity as amount
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