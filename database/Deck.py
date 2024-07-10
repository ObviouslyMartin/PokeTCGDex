class DeckDBObj:
    def __init__(self, name, number, set_total, card_type, sub_type, image_url, image_path, deck_id=None):
        self.name = name
        
    def __str__(self):
        return (f"Deck(Name: {self.name})")
