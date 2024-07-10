import customtkinter

class AddCardFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.deck_label = customtkinter.CTkLabel(self, text="Deck ID:")
        self.deck_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.deck_entry = customtkinter.CTkEntry(self)
        self.deck_entry.grid(row=0, column=1, padx=20, pady=10)
        
        self.number_label = customtkinter.CTkLabel(self, text="Number:")
        self.number_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.number_entry = customtkinter.CTkEntry(self)
        self.number_entry.grid(row=1, column=1, padx=20, pady=10)
        
        self.name_label = customtkinter.CTkLabel(self, text="Name:")
        self.name_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.name_entry = customtkinter.CTkEntry(self)
        self.name_entry.grid(row=2, column=1, padx=20, pady=10)
        
        self.set_total_label = customtkinter.CTkLabel(self, text="Set Total:")
        self.set_total_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.set_total_entry = customtkinter.CTkEntry(self)
        self.set_total_entry.grid(row=3, column=1, padx=20, pady=10)
        
        self.rarity_label = customtkinter.CTkLabel(self, text="Rarity:")
        self.rarity_label.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.rarity_entry = customtkinter.CTkEntry(self)
        self.rarity_entry.grid(row=4, column=1, padx=20, pady=10)
        
        self.add_card_button = customtkinter.CTkButton(self, text="Add Card", command=self.add_card_to_deck)
        self.add_card_button.grid(row=5, column=0, columnspan=2, padx=20, pady=10)

    def add_card_to_deck(self):
        deck_id = self.deck_entry.get() 
        number = self.number_entry.get()
        name = self.name_entry.get()
        set_total = self.set_total_entry.get()
        rarity = self.rarity_entry.get()
        
        if not deck_id or not number or not name:
            print("Deck ID, Number, and Name are required.")
            return
        
        try:
            deck_id = int(deck_id)
        except ValueError:
            print("Deck ID must be an integer.")
            return
        
        self.master.db.add_card(name, number, set_total if set_total else None, deck_id, rarity if rarity else None)
        print(f"Card {name} added to deck {deck_id}")