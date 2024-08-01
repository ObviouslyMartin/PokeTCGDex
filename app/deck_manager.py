import customtkinter
import os
from PIL import Image, ImageTk
from database.CardDB import CardDatabase
from utils.cache import DataCache
from collections import defaultdict

class DeckManagerApp(customtkinter.CTk):
    WINDOW_HEIGHT = 720
    WINDOW_WIDTH = 1280

    def __init__(self):
        super().__init__()
        self.title("Deck Manager")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        
        # Determine the path to the database file
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'pokemon_cards.db')

        # Database and Cache
        self.db = CardDatabase(self.db_path)
        self.data_cache = DataCache()
        
        # Set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Load images
        path_to_images = os.path.join(os.path.dirname(__file__), '..', 'assets')
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), path_to_images)
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "logo_crop.png")), size=(150, 150))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "home_large.png")), size=(500, 150))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.deck_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "deck.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "deck.png")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))
        
        # Create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nswe")
        self.navigation_frame.grid_rowconfigure(10, weight=1)
        
        self.logo_label = customtkinter.CTkLabel(self.navigation_frame, image=self.logo_image, text="")
        self.logo_label.grid(row=0, column=0, padx=20, pady=10)

        self.title_label = customtkinter.CTkLabel(self.navigation_frame, text="Poké TCG Dex", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=1, column=0, padx=20, pady=10)

        # Deck List
        self.deck_var = customtkinter.StringVar(value="All Cards")
        self.deck_combobox = customtkinter.CTkComboBox(self.navigation_frame, variable=self.deck_var, values=[], command=self.on_deck_select)
        self.deck_combobox.grid(row=2, column=0, padx=20, pady=10, sticky="nswe")

        self.load_decks()

        # Add Deck Button
        self.add_deck_button = customtkinter.CTkButton(self.navigation_frame, text="Add Deck", command=self.add_deck_popup)
        self.add_deck_button.grid(row=3, column=0, padx=20, pady=10, sticky="s")

        # Main View
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nswe")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Filter Buttons
        self.filter_frame = customtkinter.CTkFrame(self.main_frame)
        self.filter_frame.grid(row=0, column=0, padx=20, pady=10, sticky="we")
        self.filter_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.energy_selected = True
        self.trainer_selected = True
        self.pokemon_selected = True

        self.energy_button = customtkinter.CTkButton(self.filter_frame, text="Energy", command=self.toggle_energy)
        self.energy_button.grid(row=0, column=0, padx=10, pady=5)

        self.trainer_button = customtkinter.CTkButton(self.filter_frame, text="Trainer", command=self.toggle_trainer)
        self.trainer_button.grid(row=0, column=1, padx=10, pady=5)

        self.pokemon_button = customtkinter.CTkButton(self.filter_frame, text="Pokémon", command=self.toggle_pokemon)
        self.pokemon_button.grid(row=0, column=2, padx=10, pady=5)

        self.add_card_button = customtkinter.CTkButton(self.filter_frame, text="Add Card", command=self.add_card_popup)
        self.add_card_button.grid(row=0, column=3, padx=10, pady=5, sticky="e")

        # Card Display Frame
        self.card_display_frame = customtkinter.CTkScrollableFrame(self.main_frame)
        self.card_display_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nswe")
        self.card_display_frame.grid_columnconfigure(0, weight=1)
        self.card_display_frame.grid_rowconfigure(0, weight=1)

        self.selected_deck_id = -1
        self.display_cards()

    def load_decks(self):
        deck_names = ["All Cards"] + [f"{deck[0]}: {deck[1]}" for deck in sorted(self.db.get_all_decks(), key=lambda d: d[1])]
        self.deck_combobox.configure(values=deck_names)

    def on_deck_select(self, selected_deck):
        if selected_deck == "All Cards":
            self.selected_deck_id = None
        else:
            self.selected_deck_id = int(selected_deck.split(":")[0])
        self.display_cards()

    def display_cards(self):
        for widget in self.card_display_frame.winfo_children():
            widget.destroy()
        
        all_cards = self.db.get_all_cards() if self.selected_deck_id is -1 else self.db.get_all_cards_in_deck(deck_id=self.selected_deck_id)
        
        supertypes = []
        if self.energy_selected:
            supertypes.append("Energy")
        if self.trainer_selected:
            supertypes.append("Trainer")
        if self.pokemon_selected:
            supertypes.append("Pokémon")

        if supertypes:
            cards = [card for card in all_cards if card[4].replace("_", "") in supertypes]
        
        card_count = defaultdict(int)

        for card in cards:
            card_count[card[8]] += 1

        row, col = 0, 0
        for image_path, count in card_count.items():
            image = Image.open(image_path)
            photo = customtkinter.CTkImage(image, size=(180, 240))

            card_label = customtkinter.CTkLabel(self.card_display_frame, image=photo)
            card_label.image = photo
            card_label.grid(row=row, column=col, padx=5, pady=5)

            count_label = customtkinter.CTkLabel(self.card_display_frame, text=f"x{count}", font=customtkinter.CTkFont(size=14))
            count_label.grid(row=row+1, column=col, padx=5, pady=5)

            col += 1
            if col >= 5:
                col = 0
                row += 2
        
    def toggle_energy(self):
        self.energy_selected = not self.energy_selected
        self.energy_button.configure(fg_color="blue" if self.energy_selected else "grey75")
        self.display_cards()

    def toggle_trainer(self):
        self.trainer_selected = not self.trainer_selected
        self.trainer_button.configure(fg_color="blue" if self.trainer_selected else "grey75")
        self.display_cards()

    def toggle_pokemon(self):
        self.pokemon_selected = not self.pokemon_selected
        self.pokemon_button.configure(fg_color="blue" if self.pokemon_selected else "grey75")
        self.display_cards()

    def add_deck_popup(self):
        add_deck_window = customtkinter.CTkToplevel(self)
        add_deck_window.title("Add Deck")

        deck_name_label = customtkinter.CTkLabel(add_deck_window, text="Deck Name:")
        deck_name_label.grid(row=0, column=0, padx=10, pady=10)
        deck_name_entry = customtkinter.CTkEntry(add_deck_window)
        deck_name_entry.grid(row=0, column=1, padx=10, pady=10)

        def submit_add_deck():
            deck_name = deck_name_entry.get()
            if deck_name:
                self.db.add_deck(deck_name)
                self.load_decks()
                add_deck_window.destroy()
            else:
                print("Deck name is required")

        submit_button = customtkinter.CTkButton(add_deck_window, text="Add Deck", command=submit_add_deck)
        submit_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    def add_card_popup(self):
        if self.selected_deck_id is None:
            print("Select a deck first")
            return

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
        
        submit_button = customtkinter.CTkButton(add_card_window, text="Add Card", command=self.submit_add_card)
        submit_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def submit_add_card(self):
        name = self.card_name_entry.get()
        number = self.card_number_entry.get()
        set_total = self.set_total_entry.get() if self.set_total_entry.get() else None
        rarity = self.rarity_entry.get() if self.rarity_entry.get() else None

        if name and number:
            self.db.add_card(name, number, set_total, self.selected_deck_id, rarity)
            self.display_cards()
            self.add_card_window.destroy()
        else:
            print("Name and number are required to add a card")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)