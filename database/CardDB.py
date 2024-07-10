import sqlite3
from database.CardDBObj import CardGenerator

class CardDatabase:
    def __init__(self, database_path):
        self.conn = sqlite3.connect(database_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
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
                deck_id INTEGER,
                FOREIGN KEY (deck_id) REFERENCES decks(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        self.conn.commit()
    
    # ==================================================================
    ''' Create Operations'''
    # ==================================================================

    def add_deck(self, name):
        try:
            self.cursor.execute('INSERT INTO decks (name) VALUES (?)', (name,))
            self.conn.commit()
            return self.get_deck_id_by_name(name)
        except sqlite3.IntegrityError:
            print(f"Deck with name '{name}' already exists.")
    
    def add_card(self, name, number, set_total=None, deck_id=-1, rarity=None):
        try:
            cg = CardGenerator()
            card = cg.get_card_details(name=name, number=number, set_total=set_total, rarity=rarity)
            return self._insert(card, deck_id)
        except sqlite3.IntegrityError as e:
            print(f"An error occurred: {e}")

    def _insert(self, card, deck_id):
        existing_card = self.find_card(card.name, card.number, card.set_total)
        if existing_card:
            # Insert duplicate entry
            image_url, image_path = existing_card[1], existing_card[2]
            self.cursor.execute('''
                INSERT INTO cards (name, number, set_total, super_type, card_type, sub_type, image_url, image_path, deck_id)
                SELECT name, number, set_total, super_type, card_type, sub_type, ?, ?, ?
                FROM cards
                WHERE name = ? AND number = ? AND set_total = ?
            ''', (image_url, image_path, deck_id, card.name, card.number, card.set_total))
        else:
            # Insert new entry
            self.cursor.execute('''
                INSERT INTO cards (name, number, set_total, super_type, card_type, sub_type, image_url, image_path, deck_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (card.name, card.number, card.set_total, card.super_type, card.card_type, card.sub_type, card.image_url, card.image_path, deck_id))
        self.conn.commit()
        return self.cursor.lastrowid
    
    # ==================================================================
    ''' Read Operations'''
    # ==================================================================

    def find_card(self, name, number, set_total):
        self.cursor.execute('''
            SELECT id, image_url, image_path FROM cards 
            WHERE name = ? AND number = ? AND set_total = ?
        ''', (name, number, set_total))
        return self.cursor.fetchone()


    def get_deck_id_by_name(self, name):
        self.cursor.execute('SELECT id FROM decks WHERE name = ?', (name,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def get_deck_cards(self, deck_id):
        self.cursor.execute('''
            SELECT id, name, image_path 
            FROM cards 
            WHERE deck_id = ?
        ''', (deck_id,))
        return self.cursor.fetchall()

    def get_all_cards_in_deck(self, deckname=None, deck_id=None):
        if deckname:
            deck_id = self.get_deck_id_by_name(deckname)
        if deck_id:
            cards = self.get_deck_cards(deck_id)
            return cards

    def get_all_cards(self):
        self.cursor.execute('SELECT * FROM cards')
        return self.cursor.fetchall()

    def show_decks(self):
        self.cursor.execute('SELECT id, name FROM decks')
        decks = self.cursor.fetchall()
        for deck_id, deck_name in decks:
            self.cursor.execute('SELECT COUNT(*) FROM cards WHERE deck_id = ?', (deck_id,))
            card_count = self.cursor.fetchone()[0]
            print(f"Deck '{deck_name}' (ID: {deck_id}) has {card_count} cards.")

    def get_all_decks(self):
        self.cursor.execute('SELECT * FROM decks')
        return self.cursor.fetchall()

    def print_database_summary(self):
        self.cursor.execute('SELECT COUNT(*) FROM cards')
        total_cards = self.cursor.fetchone()[0]
        self.cursor.execute('SELECT COUNT(*) FROM decks')
        total_decks = self.cursor.fetchone()[0]
        print(f"Total number of cards: {total_cards}")
        print(f"Total number of decks: {total_decks}")
        self.show_decks()

    # ==================================================================
    ''' Update Operations'''
    # ==================================================================
    def update_deck_name(self, deck_id, new_name):
        try:
            self.cursor.execute('UPDATE decks SET name = ? WHERE id = ?', (new_name, deck_id))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print(f"Deck with name '{new_name}' already exists.")
    
    def move_card_to_deck(self, card_id, new_deck_id):
        self.cursor.execute('UPDATE cards SET deck_id = ? WHERE id = ?', (new_deck_id, card_id))
        self.conn.commit()

    # ==================================================================
    ''' Delete Operations '''
    # ==================================================================
    def delete_card(self, card_id):
        self.cursor.execute('DELETE FROM cards WHERE id = ?', (card_id,))
        self.conn.commit()

    def delete_deck(self, deck_id):
        self.cursor.execute('DELETE FROM decks WHERE id = ?', (deck_id,))
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()