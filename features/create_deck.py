import customtkinter
from PIL import Image, ImageTk

class CreateDeckFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        
        self.deck_select_label = customtkinter.CTkLabel(self, text="Select Deck:")
        self.deck_select_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.selected_card_label = customtkinter.CTkLabel(self, text="Selected Card: ")
        self.selected_card_label.grid(row=4, column=0, padx=20, pady=10, sticky="w")

        self.deck_options = [f"{deck[0]}: {deck[1]}" for deck in self.master.db.get_all_decks()]
        self.deck_var = customtkinter.StringVar(value=self.deck_options[0] if self.deck_options else "")
        self.deck_select_menu = customtkinter.CTkOptionMenu(self, variable=self.deck_var, values=self.deck_options)
        self.deck_select_menu.grid(row=0, column=1, padx=20, pady=10)

        self.view_deck_button = customtkinter.CTkButton(self, text="View Deck", command=self.view_deck_event)
        self.view_deck_button.grid(row=0, column=2, padx=20, pady=10)

        self.add_card_button = customtkinter.CTkButton(self, text="Add Card", command=self.add_card_event)
        self.add_card_button.grid(row=0, column=3, padx=20, pady=10)

        self.remove_card_button = customtkinter.CTkButton(self, text="Remove Card", command=self.remove_card_event)
        self.remove_card_button.grid(row=0, column=4, padx=20, pady=10)

        self.delete_deck_button = customtkinter.CTkButton(self, text="Delete Deck", command=self.delete_deck_event)
        self.delete_deck_button.grid(row=0, column=5, padx=20, pady=10)

        # Create a scrollable frame for the card grid
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, width=700, height=500)
        self.scrollable_frame.grid(row=1, column=0, rowspan=3, columnspan=6, padx=20, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_rowconfigure(0, weight=1)

        self.selected_card_id = None  # To keep track of the selected card for removal
        self.view_deck_event()

    def view_deck_event(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        selected_deck = self.deck_var.get()
        deck_id = selected_deck.split(":")[0].strip()
        cards_in_deck = self.master.db.get_deck_cards(deck_id)

        # Update deck select label with total number of cards
        self.deck_select_label.configure(text=f"Total cards in deck: {len(cards_in_deck)}")
        
        card_counts = {}
        for card in cards_in_deck:
            card_id, card_name, image_path = card
            if image_path not in card_counts:
                card_counts[image_path] = (1, card_id)
            else:
                card_counts[image_path] = (card_counts[image_path][0] + 1, card_id)
                
        row, col = 0, 0
        for image_path, (count, card_id) in card_counts.items():
            image = Image.open(image_path)
            photo = customtkinter.CTkImage(image, size=(190, 250))
            
            card_image_label = customtkinter.CTkLabel(self.scrollable_frame, image=photo)
            card_image_label.image = photo  # Keep a reference to avoid garbage collection
            card_image_label.grid(row=row, column=col, padx=5, pady=5)
            card_image_label.bind("<Button-1>", lambda e, id=card_id: self.select_card(id))
            
            count_label = customtkinter.CTkLabel(self.scrollable_frame, text=str(count))
            count_label.grid(row=row+1, column=col, padx=5, pady=5)
            
            col += 1
            if col > 4:  # Adjust number of columns as needed
                col = 0
                row += 2

    def select_card(self, card_id):
        self.selected_card_id = card_id
        self.selected_card_label.configure(text=f"Selected Card: {self.selected_card_id}")
        print(f"Selected card ID: {card_id}")

    def add_card_event(self):
        selected_deck = self.deck_var.get()
        deck_id = int(selected_deck.split(":")[0].strip())

        # Logic to add a card (pop up a new window to take card details as input)
        add_card_window = customtkinter.CTkToplevel(self)
        add_card_window.title("Add Card")

        card_name_label = customtkinter.CTkLabel(add_card_window, text="Card Name:")
        card_name_label.grid(row=0, column=0, padx=10, pady=10)
        card_name_entry = customtkinter.CTkEntry(add_card_window)
        card_name_entry.grid(row=0, column=1, padx=10, pady=10)

        card_number_label = customtkinter.CTkLabel(add_card_window, text="Card Number:")
        card_number_label.grid(row=1, column=0, padx=10, pady=10)
        card_number_entry = customtkinter.CTkEntry(add_card_window)
        card_number_entry.grid(row=1, column=1, padx=10, pady=10)

        set_total_label = customtkinter.CTkLabel(add_card_window, text="Set Total:")
        set_total_label.grid(row=2, column=0, padx=10, pady=10)
        set_total_entry = customtkinter.CTkEntry(add_card_window)
        set_total_entry.grid(row=2, column=1, padx=10, pady=10)

        rarity_label = customtkinter.CTkLabel(add_card_window, text="Rarity:")
        rarity_label.grid(row=3, column=0, padx=10, pady=10)
        rarity_entry = customtkinter.CTkEntry(add_card_window)
        rarity_entry.grid(row=3, column=1, padx=10, pady=10)

        collection_count_label = customtkinter.CTkLabel(add_card_window, text="Collection Count:")
        collection_count_label.grid(row=3, column=0, padx=10, pady=10)
        collection_count_entry = customtkinter.CTkEntry(add_card_window)
        collection_count_entry.grid(row=3, column=1, padx=10, pady=10)

        def submit_add_card():
            name = card_name_entry.get()
            number = card_number_entry.get()
            set_total = set_total_entry.get() if set_total_entry.get() else None
            rarity = rarity_entry.get() if rarity_entry.get() else None
            collection_count = collection_count_entry.get() if collection_count_entry.get() else None
            if name and number:
                for _ in range(0,int(collection_count)):
                    self.master.db.add_card(name=name, number=number, set_total=set_total, deck_id=deck_id, rarity=rarity)
                self.view_deck_event()  # Refresh the deck view
                add_card_window.destroy()
            else:
                print("Name and number are required to add a card")

        submit_button = customtkinter.CTkButton(add_card_window, text="Add Card", command=submit_add_card)
        submit_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def remove_card_event(self):
        if self.selected_card_id:
            self.master.db.move_card_to_deck(self.selected_card_id, -1)
            self.selected_card_id = None
            self.view_deck_event()  # Refresh the deck view
        else:
            print("No card selected to remove")

    def delete_deck_event(self):
        selected_deck = self.deck_var.get()
        deck_id = int(selected_deck.split(":")[0].strip())
        self.master.db.delete_deck(deck_id)
        self.update_deck_options()
        self.view_deck_event()  # Refresh the deck view