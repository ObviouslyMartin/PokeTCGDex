import sqlite3
from CardGenerator import CardGenerator

class CardDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.__create_tables()

    def __create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            card_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            number INTEGER NOT NULL,
            set_total INTEGER NOT NULL,
            super_type TEXT NOT NULL,
            card_type TEXT,
            sub_type TEXT NOT NULL,
            image_url TEXT NOT NULL,
            image_path TEXT NOT NULL
        );
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS decks (
            deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            UNIQUE(name)
        );
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS deck_cards (
            deck_id INTEGER,
            card_id INTEGER,
            PRIMARY KEY (deck_id, card_id),
            FOREIGN KEY (deck_id) REFERENCES decks (deck_id) ON DELETE CASCADE,
            FOREIGN KEY (card_id) REFERENCES cards (card_id) ON DELETE CASCADE
        );
        ''')

        self.conn.commit()
        # self.conn.close()
        
    def close_connection(self):
        '''Close the database connection when no longer needed.'''
        self.conn.close()

    ########################################################
    ''' Add to DB '''
    ########################################################
    def add_card(self, new_card: dict) -> int:
        ''' 
        add new card or update count if already exists
        returns id of the last accessed id
        '''
        # Insert a new row if the card does not exist <count> times
        self.cursor.execute(
            "INSERT INTO cards (name, number, set_total, super_type, card_type, sub_type, image_url, image_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                new_card["name"], new_card["number"], new_card["set_total"],
                new_card["super_type"], new_card["card_type"], new_card["sub_type"],
                new_card["image_url"], new_card["image_path"]
            )
        )
        card_id = self.cursor.lastrowid  # Get the last inserted id
        self.conn.commit()
        return card_id

    def move_card_to_deck(self, deck_id, card_id,count):
        
        if not self.__deck_exists(deck_id):
            return "Deck does not exist"
        if not self.__get_card(card_id):
            return "Card does not exist"

        if not self.__has_sufficient_card_count(card_id, count):
            return "Not enough cards available"

        if not self.__can_add_to_deck(deck_id, card_id, count):
            return "Cannot add more than 4 of the same card or exceed the deck limit of 60 cards"

        self.cursor.execute(
            "INSERT INTO deck_cards (deck_id, card_id) VALUES (?, ?)",
            (deck_id, card_id)
        )
        
        self.conn.commit()
        return "Card added successfully"

    def create_deck(self, deck_name) -> int:
        deck_id = self.get_deck_id_by_name(deck_name)
        if deck_id:
            return deck_id
        self.cursor.execute(
            "INSERT INTO decks (name) VALUES (?)", (deck_name,)
        )
        deck_id = self.cursor.lastrowid  # Get the last inserted id
        self.conn.commit()
        return deck_id
    
    ########################################################
    ''' Get things '''
    ########################################################
    def get_cards_with_detailed_amount(self, deck_id=-1):
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
                GROUP_CONCAT(cards.card_id) as all_card_ids,
                GROUP_CONCAT(CASE WHEN cards.card_id NOT IN (SELECT deck_cards.card_id FROM deck_cards) THEN cards.card_id ELSE NULL END) as not_in_deck_ids
            FROM cards
        """
        
        # Conditional WHERE clause depending on whether deck_id is provided
        if deck_id != -1:
            # Fetch cards specifically from the given deck
            query = f"{base_query} JOIN deck_cards ON cards.card_id = deck_cards.card_id WHERE deck_cards.deck_id = ? GROUP BY cards.name, cards.number, cards.set_total"
            self.cursor.execute(query, (deck_id,))
        else:
            # Fetch all cards without deck filtering
            query = f"{base_query} GROUP BY cards.name, cards.number, cards.set_total"
            self.cursor.execute(query)

        # Fetch and return results
        results = self.cursor.fetchall()
        
        # Process results to ensure NULL values in not_in_deck_ids are handled as empty lists
        processed_results = []
        for row in results:
            # Convert tuple to list for mutable operations
            mutable_row = list(row)
            
            # Add two new attributes by converting CSV string to list of integers, handle NULL cases
            all_card_ids = list(map(int, mutable_row[7].split(','))) if mutable_row[7] else []
            not_in_deck_ids = list(map(int, mutable_row[8].split(','))) if mutable_row[8] else []
            
            # Append new attributes
            mutable_row.append(all_card_ids)
            mutable_row.append(not_in_deck_ids)
            
            # Convert back to tuple if necessary and append to final results
            processed_results.append(tuple(mutable_row))

        return tuple(processed_results)
    def get_standalone_cards_with_amount(self):
        """
        DEPRECATED see get_cards_with_detailed_amount(self, deck_id=-1)
        Retrieves a list of cards from the cards table that are not associated with any deck
        and augments each dictionary with an 'amount' key that lists all card_ids with matching
        name, number, and set_total for standalone cards.
        """
        # Fetch standalone cards not linked to any deck
        self.cursor.execute('''
            SELECT 
                name,
                number, 
                set_total,
                super_type,
                card_type,
                sub_type,
                image_path,
                GROUP_CONCAT(card_id) as card_ids
            FROM cards
            WHERE card_id NOT IN (SELECT card_id FROM deck_cards)
            GROUP BY name, number, set_total
        ''')

        return self.cursor.fetchall()
    
    def get_unique_cards_with_amount(self, deck_id=-1):
        """
        DEPRECATED see get_cards_with_detailed_amount(self, deck_id=-1)

        Retrieves a list of cards from the cards table (filtered by deck_id if provided)
        and augments each dictionary with an 'amount' key that lists all card_ids with matching name, number, and set_total.
        """
        if deck_id != -1:
            # Fetch cards specifically from the given deck -> Total cards in a deck
            self.cursor.execute('''
                SELECT 
                    cards.name, 
                    cards.number, 
                    cards.set_total, 
                    cards.super_type, 
                    cards.card_type, 
                    cards.sub_type, 
                    cards.image_path,
                    GROUP_CONCAT(cards.card_id) as card_ids
                FROM cards
                JOIN deck_cards ON cards.card_id = deck_cards.card_id
                WHERE deck_cards.deck_id = ?
                GROUP BY cards.name, cards.number, cards.set_total
            ''', (deck_id,))
        else:
            # Fetch all cards without deck filtering -> Total cards in the database
            self.cursor.execute('''
                SELECT 
                    name, 
                    number, 
                    set_total,
                    super_type,
                    card_type,
                    sub_type,
                    image_path,
                    GROUP_CONCAT(card_id) as card_ids
                FROM cards
                GROUP BY name, number, set_total
            ''')

        return (self.cursor.fetchall())
     
    def get_decks(self, deck_id=-1):
        '''
        Gets all deck names and ids in database
        returns dictinoary object for each deck
        '''
        if deck_id == -1:
            self.cursor.execute("SELECT deck_id, name FROM decks")
        else:
            self.cursor.execute("SELECT deck_id, name FROM decks where deck_id = ?", (deck_id,))
        decks = self.cursor.fetchall()
        return decks
    
    def get_in_deck_card_ids(self, card, deck_id):
        '''
            returns a tuple of ids that match the given name number and set_total for the given deck id
        '''
        self.cursor.execute(
            """SELECT
                deck_cards.card_id
            FROM deck_cards
            JOIN cards ON deck_cards.card_id = cards.card_id
            WHERE cards.name = ? AND cards.number = ? AND cards.set_total = ? AND deck_cards.deck_id = ?
            """,
            (card["name"], card["number"], card["set_total"], deck_id)
        )
        matching_ids = self.cursor.fetchall()

        return tuple([id[0] for id in matching_ids])

    def get_cards_in_deck(self, deck_id):
        '''
            returns deck name with all cards within the deck.
        '''
        # self.cursor.execute("SELECT * FROM deck_cards where deck_id = ?", (deck_id,))
        # deck = self.cursor.fetchone()
        # if deck is None:
        #     return {}
        # deck_id = deck[0]
        # deck_name = deck[1]
        self.cursor.execute(
            """SELECT
                cards.name AS card_name,
                cards.number,
                cards.set_total,
                cards.super_type,
                cards.card_type,
                cards.sub_type,
                cards.image_path,
                COUNT(*) AS count
            FROM
                deck_cards
            JOIN
                cards ON deck_cards.card_id = cards.card_id
            JOIN
                decks ON deck_cards.deck_id = decks.deck_id
            WHERE
                deck_cards.deck_id = ?
            GROUP BY
                cards.name, cards.number, cards.set_total""",
            (deck_id,)
        )
        deck_cards = self.cursor.fetchall()
        for card in deck_cards:
            print(f'jebi: {card}')
        return deck_cards
        # cards = {
        #     row[0]: {
        #         "name": row[1],
        #         "number": row[2],
        #         "set_total": row[3],
        #         "image_path": row[4],
        #         "count": row[5],
        #         "super_type":row[6]
        #     }
        #     for row in deck_cards
        # }
        # # return cards  
        
        # decks = decks[deck_name] = [
        #     {"id": card_id, "name": name, "number":number, "set_total":set_total, "image_path":image_path, "count": count} for card_id, name, number, set_total, image_path, count in deck_cards
        # ]
        
        # # return decks
    def get_decks_with_cards(self):
        '''Gets all decks and show cards'''
        self.cursor.execute("SELECT * FROM decks")
        decks = {}
        
        for row in self.cursor.fetchall():
            deck_id = row[0]
            deck_name = row[1]
            self.cursor.execute(
                """SELECT
                    cards.card_id,
                    cards.name,
                    cards.number,
                    cards.set_total,
                    cards.image_path,
                    deck_cards.count
                FROM deck_cards
                JOIN cards ON deck_cards.card_id = cards.card_id
                WHERE deck_cards.deck_id = ?""",
                (deck_id,)
            )
            deck_cards = self.cursor.fetchall()
            decks[deck_name] = [
                {"id": card_id, "name": name, "number":number, "set_total":set_total, "image_path":image_path, "count": count} for card_id, name, number, set_total, image_path, count in deck_cards
            ]
        
        return decks
    
    def get_deck_id_by_name(self, deck_name) -> tuple | None:
        self.cursor.execute("SELECT deck_id FROM decks WHERE name = ?", (deck_name,))
        return self.cursor.fetchone()
    
    def get_card_id_by_name(self, name, number) -> int | None:
        self.cursor.execute("SELECT card_id FROM cards WHERE name = ? AND number = ?", (name,number))
        return self.cursor.fetchone()
    def get_card_ids_by_name(self, name, number, set_total, deck_id=-1) -> list | None:
        '''
            returns list of ids that match the given name, number, and set_total
        '''
        if deck_id == -1:
            return self.__get_card_ids_by_name(name, number, set_total)
        return self.__get_deck_card_ids_by_name(name, number, set_total, deck_id)
    def __get_card_ids_by_name(self, name, number, set_total) -> list | None:
        ''' return list of ids from cards table with matching name number and set total'''
        self.cursor.execute("SELECT card_id from cards WHERE name = ? AND number = ? and set_total = ?", (name, number, set_total))
        return [_id[0] for _id in self.cursor.fetchall()]
    def get_deck_card_ids_by_name(self, name, number, set_total, deck_id) -> list | None:
        '''
            returns list of ids that match the given name, number, and set_total given some deck
        '''
        self.cursor.execute(
            """
            SELECT 
                deck_cards.card_id
            FROM deck_cards
            JOIN cards ON deck_cards.card_id = cards.card_id
            JOIN decks ON deck_cards.deck_id = decks.deck_id
            WHERE cards.name = ? AND 
                  cards.number = ? AND 
                  cards.set_total = ? AND 
                  deck_cards.deck_id = ? 
            GROUP BY cards.name, cards.number, cards.set_total
            """,
            (name, number, set_total, deck_id)
        )
        return [_id[0] for _id in self.cursor.fetchall()]
    def get_card_by_id(self,card_id):
        ''''''
        return self.__get_card(card_id=card_id)
    
    def get_total_card_count(self) -> int:
        '''get total number of cards stored'''
        self.cursor.execute("SELECT count(card_id) FROM cards")
        return self.cursor.fetchone()
    
    def get_total_deck_count(self) -> int:
        '''get total number of decks stored'''
        self.cursor.execute("SELECT count(deck_id) FROM decks")
        return self.cursor.fetchone()
    
    ########################################################
    ''' Remove items '''
    ########################################################

    def remove_all(self):
        inp = input("WARNING: This cannot be undone. Proceed?\nY / N: ")
        if inp != 'Y':
            print("Aborting...")
            return
        
        print("Emptying the database...")
        cards = [_id[0] for _id in self.__get_all_card_ids()]
        decks = [_id[0] for _id in self.__get_all_deck_ids()]
        for card in cards:
            self.delete_card(card_id=card)
        for deck in decks:
            self.delete_deck(deck_id=deck)


    def remove_card_from_deck(self, deck_id, card_id):
        # ensure card exists
        exists = self.__get_card(card_id=card_id)
        if exists:
            self.cursor.execute(
                "DELETE FROM deck_cards WHERE deck_id = ? AND card_id = ?", (deck_id, card_id)
            )
            self.conn.commit()
            return self.cursor.rowcount  # Returns the number of rows affected
        return 0
    
    def delete_card(self, card_id):
        print(f"DB: about to delete {card_id}")
        exists = self.__get_card(card_id=card_id)
        if exists:
            return "Card not found"

        self.cursor.execute(
            "DELETE FROM cards WHERE card_id = ?", (card_id,)
        )
        self.cursor.execute(
            "DELETE FROM deck_cards WHERE card_id = ?", (card_id,)
        )

        self.conn.commit()
        return self.cursor.rowcount  # Returns the number of rows affected

    def delete_deck(self, deck_id):
        self.cursor.execute(
            "DELETE FROM deck_cards WHERE deck_id = ?", (deck_id,)
        )
        self.cursor.execute(
            "DELETE FROM decks WHERE deck_id = ?", (deck_id,)
        )
        self.conn.commit()
        return self.cursor.rowcount  # Returns the number of rows affected

    ########################################################
    ''' Show items '''
    ########################################################

    def __str__(self) -> str:
        ret_string = self.__show_decks_table() + self.__show_cards_table() 
        ret_string += f'\nTotal Cards: {self.get_total_card_count()[0]}'
        ret_string += f'\nTotal Decks: {self.get_total_deck_count()[0]}'
        ret_string += self.__show_deck_cards_table(deck_id=1)
        return ret_string
    
    def show_cards(self):
        print(self.__show_cards_table())

    def show_cards_in_deck(self, deck):
        '''Gets all decks and show cards'''
        deck_id = deck[0]
        # self.cursor.execute(
        #     """SELECT
        #         cards.card_id,
        #         cards.name,
        #         cards.number,
        #         cards.set_total,
        #         cards.image_path
        #     FROM deck_cards
        #     JOIN cards ON deck_cards.card_id = cards.card_id
        #     WHERE deck_cards.deck_id = ?""",
        #     (int(deck_id),)
        # )
        # deck_cards = self.cursor.fetchall()
        # for card_id, name, number, set_total, image_path in deck_cards:
        #     card_count = self.__get_card_count(card_id=card_id, deck_id=deck_id)
        #     print(f"id: {card_id}, name: {name}, number:{number}, set_totat:{set_total}, image_path:{image_path}, count: {card_count}")
        self.cursor.execute(
            """SELECT
                 *
             FROM deck_cards
             WHERE deck_cards.deck_id = ?""",
            (int(deck_id),)
        )
        deck_cards = self.cursor.fetchall()
        print(deck_cards)
    def show_all_cards(self):
        cards = self.get_cards()
        for _id, card in cards.items():
            print(f'{card["name"]}, {card["number"]}, {card["set_total"]}, {card["count"]}')
        return cards.keys()
    
    def show_decks_and_cards(self):
        decks = self.get_decks_with_cards()
        for deck, cards in decks.items():
            print(f"deck: {deck}")
            for card in cards:
                print(f'card: {card["id"], card["name"]}, {card["number"]}, {card["set_total"]}, {card["count"]}')

    def show_cards_from_ids(self, card_ids):
        ''' given a list of ids, fetch matching cards and show them'''
        query = "SELECT * FROM cards WHERE card_id IN ({seq})".format(seq=','.join(['?']*len(tuple(card_ids))))
        self.cursor.execute(query, tuple(card_ids))

        rows = self.cursor.fetchall()
        cards = {
            row[0]: {
                "name": row[1],
                "number": row[2],
                "set_total": row[3],
                "super_type": row[4],
                "card_type": row[5],
                "sub_type": row[6],
                "image_url": row[7],
                "image_path": row[8]
            }
            for row in rows
        }
        print(cards)
    
    ########################################################
    ''' Private items '''
    ########################################################
    def __deck_exists(self, deck_id) -> tuple | None:
        self.cursor.execute("SELECT deck_id FROM decks WHERE deck_id = ?", (deck_id,))
        return self.cursor.fetchone()

    # def __get_card(self, card_id)-> tuple | None:
    #     '''returns the matching row if found. else none.'''

    #     self.cursor.execute(
    #         """SELECT 
    #                 *,
    #                 GROUP_CONCAT(card_id) as card_ids
    #             FROM cards
    #             WHERE card_id = ?
    #             GROUP BY name, number, set_total""", (card_id,))
    #     return self.cursor.fetchone()
    def __get_card(self, card_id):
        """
        Retrieves all attributes for a given card_id and a list of all matching card_ids 
        with the same name, number, and set_total.
        """
        # First, fetch the details of the specified card
        self.cursor.execute(
            """SELECT * FROM cards WHERE card_id = ?""",
            (card_id,)
        )
        card_details = self.cursor.fetchone()

        if card_details:
            # Extract name, number, and set_total from the fetched details
            name, number, set_total = card_details[1], card_details[2], card_details[3]
            # print(name, number, set_total)
            # Now fetch all card IDs that have the same name, number, and set_total
            self.cursor.execute(
                """SELECT GROUP_CONCAT(card_id) as card_ids 
                FROM cards 
                WHERE name = ? AND number = ? AND set_total = ?
                GROUP BY name, number, set_total""",
                (name, number, set_total)
            )
            similar_card_ids_result = self.cursor.fetchone()
            similar_card_ids = list(map(int, similar_card_ids_result[0].split(','))) if similar_card_ids_result[0] else []
            
            # Create a new tuple that includes the original card details and the similar_card_ids
            extended_card_details = card_details + (similar_card_ids,)
            return extended_card_details
        else:
            print("No such card found with the given card_id")
            return None
    def __get_deck_card_count(self, deck_id, card_id)-> tuple | None:
        self.cursor.execute("SELECT count FROM deck_cards WHERE deck_id = ? AND card_id = ?", (deck_id, card_id))
        return self.cursor.fetchone()
    
    def __get_card_count(self, card_id, deck_id=None):
        """Counts cards with the same name, number, and set_total as the card with the given card_id.
        If deck_id is provided, counts only within that deck, otherwise counts in all cards."""
        attributes = self.__get_card(card_id)
        if attributes:
            name, number, set_total = attributes[1], attributes[2], attributes[3]
            if deck_id:
                # Count matching cards within the specified deck
                self.cursor.execute('''
                    SELECT COUNT(*) FROM deck_cards
                    JOIN cards ON deck_cards.card_id = cards.card_id
                    WHERE deck_id = ? AND name = ? AND number = ? AND set_total = ?
                    ''', (deck_id, name, number, set_total))
            else:
                # Count matching cards in all cards
                self.cursor.execute('''
                    SELECT COUNT(*) FROM cards
                    WHERE name = ? AND number = ? AND set_total = ?
                    ''', (name, number, set_total))
            count = self.cursor.fetchone()[0]
            return count
    
    def __get_all_card_ids(self)-> tuple | None:
        self.cursor.execute("SELECT card_id FROM cards")
        return self.cursor.fetchall()
    def __get_all_deck_ids(self)-> tuple | None:
        self.cursor.execute("SELECT deck_id FROM decks")
        return self.cursor.fetchall()
    
    def __has_sufficient_card_count(self, card_id, count):
        '''
            Returns if card_id with count can be move to deck
            cannot move 

        '''
        card_total_count = self.__get_card_count(card_id)
        self.cursor.execute("SELECT SUM(count) FROM deck_cards WHERE card_id = ?", (card_id,))
        current_total_count = self.cursor.fetchone()[0] or 0
        return current_total_count + count <= card_total_count
    
    def __get_deck_size(self, deck_id)-> int:
        '''
            returns the number of cards in a deck
        '''
        self.cursor.execute("SELECT Count(*) FROM deck_cards WHERE deck_id = ?", (deck_id,))
        result = self.cursor.fetchone()
        if not result:
            return 0
        return result[0]
    
    def __is_energy_card(self, card_id) -> bool:
        '''
            returns is the card_id an energy card?
        '''
        self.cursor.execute("Select super_type FROM cards WHERE card_id = ?", (card_id,))
        super_type = self.cursor.fetchone()
        # print(f'super_type == {super_type[0]}')
        return super_type[0] == "Energy"
    
    def __can_add_to_deck(self, deck_id, card_id, count) -> bool:
        ''' 
            Check if adding to deck exceeds constraints
            Check current total number of cards in the deck
        '''
        if not self.__deck_exists(deck_id):
            return False
        
        deck_size = self.__get_deck_size(deck_id)

        if deck_size + count > 60:
            return False
        
        if self.__is_energy_card(card_id):
            return True
        
        # Check current number of this card in the deck
        current_card_count = self.__get_deck_card_count(deck_id, card_id) or 0 # TODO: 'or'?
        if current_card_count + count > 4:
            return False

        return True
    
    def __show_decks_table(self)-> str:
        '''
            print decks table
            deck_id: name
        '''
        # print("showing decks")
        query = "SELECT * FROM decks"
        self.cursor.execute(query)
        deck_table = self.cursor.fetchall()
        out_string = ""
        for row in deck_table:
            out_string += f"{row[0]}: {row[1]}\n"
        return out_string
    
    def __show_cards_table(self)-> str:
        '''
            print cards table
            card_id: name, number/set_total, amount: _
        '''
        query = "SELECT * FROM cards"
        self.cursor.execute(query)
        cards_table = self.cursor.fetchall()
        cards = []
        out_string = ""
        for row in cards_table:
            card_id = row[0]
            name = row[1]
            number = row[2]
            set_total = row[3]
            if (name, number, set_total) not in cards:
                cards.append((name, number, set_total))
                out_string += f"{card_id}: {name}, {number}/{set_total}, amount: {self.__get_card_count(card_id=card_id)}\n"
        return out_string
    def __show_deck_cards_table(self, deck_id):
        query = "SELECT * FROM deck_cards where deck_id = ?"
        deck_cards_table = self.cursor.execute(query, (deck_id,))
        out_string = ""
        for row in deck_cards_table:
            out_string += f"{row}\n"
        return out_string
    # def execute(self, query):
        
        
    #     return 

if __name__ == '__main__':
    # db = 'test_db.db'
    db = CardDatabase()