import customtkinter
import os
from PIL import Image
from card_database import CardDatabase
from controller import Controller


# The View
class DeckManagerApp(customtkinter.CTk):
    WINDOW_HEIGHT = 720
    WINDOW_WIDTH = 1280

    def __init__(self):
        super().__init__()
        
        self.title("Deck Manager")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        
        # Determine the path to the database file
        self.db_path = "test_db.db"

        # Database
        self.db = CardDatabase(self.db_path)
        #TODO: uncomment once self.db is replaced with controller logic
        self.controller = Controller()
        
        # Set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        ##############
        ''' Assets '''
        ##############

        # Load images
        path_to_images = "assets"
        image_path = path_to_images
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "logo_crop.png")), size=(150, 150))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "home_large.png")), size=(500, 150))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.deck_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "deck.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "deck.png")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))
        
        ##############
        ''' LAYOUT '''
        ##############

        # Create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nswe")
        self.navigation_frame.grid_rowconfigure(10, weight=1)
        
        self.logo_label = customtkinter.CTkLabel(self.navigation_frame, image=self.logo_image, text="")
        self.logo_label.grid(row=0, column=0, padx=20, pady=10)

        self.title_label = customtkinter.CTkLabel(self.navigation_frame, text="Poké TCG Dex", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=1, column=0, padx=20, pady=10)

        # Deck List Drop Down
        self.deck_var = customtkinter.StringVar(value="All Cards")
        self.deck_combobox = customtkinter.CTkComboBox(self.navigation_frame, variable=self.deck_var, values=[], command=self.on_deck_select)
        self.deck_combobox.grid(row=2, column=0, padx=20, pady=10, sticky="nswe")

        # selected card text
        self.selected_card = ""
        self.selected_card_label = customtkinter.CTkLabel(self.navigation_frame, text=self.selected_card)
        self.selected_card_label.grid(row=7, column=0, padx=10, pady=10)

        # Main View
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nswe")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Filter Buttons
        self.filter_frame = customtkinter.CTkFrame(self.main_frame)
        self.filter_frame.grid(row=0, column=0, padx=20, pady=10, sticky="we")
        self.filter_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.pokemon_check_box = customtkinter.CTkCheckBox(self.filter_frame, text="Pokémon Cards", command=self.toggle_pokemon,)
        self.pokemon_check_box.grid(row=0, column=0, padx=10, pady=5)
        self.energy_check_box = customtkinter.CTkCheckBox(self.filter_frame, text="Energy Cards", command=self.toggle_energy)
        self.energy_check_box.grid(row=0, column=1, padx=10, pady=5)
        self.trainer_check_box = customtkinter.CTkCheckBox(self.filter_frame, text="Trainer Cards", command=self.toggle_trainer)
        self.trainer_check_box.grid(row=0, column=2, padx=10, pady=5)

        # Card Display Frame
        self.card_display_frame = customtkinter.CTkScrollableFrame(self.main_frame)
        self.card_display_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nswe")
        self.card_display_frame.grid_columnconfigure(0, weight=1)
        self.card_display_frame.grid_rowconfigure(0, weight=1)

        self.selected_deck_id = -1

        # self.energy_selected = True
        # self.trainer_selected = True
        # self.pokemon_selected = True
        self.supertypes = []
        self.current_cards = None
        # self.supertypes = ["Energy", "Trainer", "Pokémon"]

        ###############
        ''' BUTTONS '''
        ###############

        # Main View Add Deck Button
        self.add_deck_button = customtkinter.CTkButton(self.navigation_frame, text="Add Deck", command=self.add_deck_popup)
        self.add_deck_button.grid(row=3, column=0, padx=20, pady=10, sticky="s")
        
        # Main view Add Card button
        self.add_card_button = customtkinter.CTkButton(self.navigation_frame, text="Add Card", command=self.add_card_popup)
        self.add_card_button.grid(row=4, column=0, padx=20, pady=5, sticky="s")

        # Main view Move Card to deck button
        self.move_card_to_deck_button = customtkinter.CTkButton(self.navigation_frame, text="Move Card to Deck", command=self.move_card_to_deck_popup)
        self.move_card_to_deck_button.grid(row=5, column=0, padx=20, pady=5, sticky="s")
        
        # Main view Remove Card from deck button
        self.remove_card_to_deck_button = customtkinter.CTkButton(self.navigation_frame, text="Remove Card From Deck", command=self.remove_card_popup)
        self.remove_card_to_deck_button.grid(row=6, column=0, padx=20, pady=5, sticky="s")

        # Main view Import From File Button
        self.import_from_file_button = customtkinter.CTkButton(self.navigation_frame, text="Import From File", command=self.import_from_file_popup)
        self.import_from_file_button.grid(row=7, column=0, padx=20, pady=5, sticky="s")
        
        # load cards and decks
        self.load_decks()
        self.display_cards()

    def load_decks(self):
        deck_names = ["All Cards"] + [f"{deck[0]}: {deck[1]['name']}" for deck in self.controller.get_decks().items()]
        self.deck_combobox.configure(values=deck_names)

    def on_deck_select(self, selected_deck):
        if selected_deck == "All Cards":
            self.selected_deck_id = -1
            self.current_cards = None
        else:
            self.selected_deck_id = int(selected_deck.split(":")[0])
            self.current_cards = None
        self.display_cards()

    def display_cards(self):
        # TODO: not displaying cards for decks
        for widget in self.card_display_frame.winfo_children():
            widget.destroy()
        if not self.current_cards:
            self.current_cards = self.controller.get_cards(deck_id=self.selected_deck_id)

        # print(f'Picku: \n{self.current_cards}')
        row, col = 0, 0
        for card_info in self.current_cards:
            image = Image.open(card_info["image_path"])
            photo = customtkinter.CTkImage(image, size=(180, 240))

            card_label = customtkinter.CTkButton(self.card_display_frame, corner_radius=5, width=180, height=240, image=photo, text="")
            card_label = customtkinter.CTkButton(self.card_display_frame, image=photo, text="", 
                                                command=lambda card=card_info: self.card_picture_press_event(card))
            # card_label.image = photo
            card_label.grid(row=row, column=col, padx=5, pady=5)

            count_label = customtkinter.CTkLabel(self.card_display_frame, text=f"x{len(card_info['all_card_ids'])}", font=customtkinter.CTkFont(size=14))
            count_label.grid(row=row+1, column=col, padx=5, pady=5)

            col += 1
            if col >= 5:
                col = 0
                row += 2
    
    def toggle_energy(self):
        if self.energy_check_box:
            self.supertypes.append("Energy")
        else:
            self.supertypes.remove("Energy")
        
        # self.energy_selected = not self.energy_selected
        self.display_cards()

    def toggle_trainer(self):
        if self.trainer_check_box:
            self.supertypes.append("Trainer")
        else:
            self.supertypes.remove("Trainer")
        # self.trainer_selected = . not self.trainer_selected
        self.display_cards()

    def toggle_pokemon(self):
        if self.pokemon_check_box:
            self.supertypes.append("Pokémon")
        else:
            self.supertypes.remove("Pokémon")
        # self.pokemon_selected = not self.pokemon_selected
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
                # self.db.add_deck(deck_name)
                self.controller.create_deck_from_input(deck_name=deck_name)
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

        self.add_card_window = customtkinter.CTkToplevel(self)
        self.add_card_window.title("Add Card")

        self.card_name_label = customtkinter.CTkLabel(self.add_card_window, text="Card Name:")
        self.card_name_label.grid(row=0, column=0, padx=10, pady=10)
        self.card_name_entry = customtkinter.CTkEntry(self.add_card_window)
        self.card_name_entry.grid(row=0, column=1, padx=10, pady=10)

        self.card_number_label = customtkinter.CTkLabel(self.add_card_window, text="Card Number:")
        self.card_number_label.grid(row=1, column=0, padx=10, pady=10)
        self.card_number_entry = customtkinter.CTkEntry(self.add_card_window)
        self.card_number_entry.grid(row=1, column=1, padx=10, pady=10)

        self.set_total_label = customtkinter.CTkLabel(self.add_card_window, text="Set Total:")
        self.set_total_label.grid(row=2, column=0, padx=10, pady=10)
        self.set_total_entry = customtkinter.CTkEntry(self.add_card_window)
        self.set_total_entry.grid(row=2, column=1, padx=10, pady=10)

        self.is_promo_label = customtkinter.CTkLabel(self.add_card_window, text="Is Promo Card?:")
        self.is_promo_label.grid(row=3, column=0, padx=10, pady=10)
        self.is_promo_entry = customtkinter.CTkEntry(self.add_card_window)
        self.is_promo_entry.grid(row=3, column=1, padx=10, pady=10)
        
        self.amount_to_add_label = customtkinter.CTkLabel(self.add_card_window, text="Amount to add:")
        self.amount_to_add_label.grid(row=4, column=0, padx=10, pady=10)
        self.amount_to_add_entry = customtkinter.CTkEntry(self.add_card_window)
        self.amount_to_add_entry.grid(row=4, column=1, padx=10, pady=10)

        self.submit_button = customtkinter.CTkButton(self.add_card_window, text="Add Card", command=self.add_card_button_press_event)
        self.submit_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
    
    def remove_card_popup(self):
        if self.selected_deck_id is None:
            print("Select a deck first")
            return
        if self.selected_deck_id == -1:
            pass 

        self.remove_card_window = customtkinter.CTkToplevel(self)
        self.remove_card_window.title("Remove Card")

        self.warning_label = customtkinter.CTkLabel(self.remove_card_window, text=f'Are you sure you want to remove?\n{self.selected_card["name"]}, {self.selected_card["number"]}/{self.selected_card["set_total"]}')
        self.warning_label.grid(row=1, column=0, padx=10, pady=10)

        self.amount_to_remove_label = customtkinter.CTkLabel(self.remove_card_window, text="Amount to remove:")
        self.amount_to_remove_label.grid(row=2, column=0, padx=10, pady=10)
        self.amount_to_remove_entry = customtkinter.CTkEntry(self.remove_card_window)
        self.amount_to_remove_entry.grid(row=2, column=1, padx=10, pady=10)

        self.warning_confirmation_button = customtkinter.CTkButton(self.remove_card_window, text="Confirm", command=self.remove_card_button_press_event)
        self.warning_confirmation_button.grid(row=3, column=0, padx=10, pady=10)
        

    def move_card_to_deck_popup(self):
        if self.selected_card is None:
            print("Select a card first")
            return

        self.move_card_window = customtkinter.CTkToplevel(self)
        self.move_card_window.title("Move Card")

        self.warning_label = customtkinter.CTkLabel(self.move_card_window, text=f'Are you sure you want to move?\n{self.selected_card["name"]}, {self.selected_card["number"]}/{self.selected_card["set_total"]}')
        self.warning_label.grid(row=1, column=0, padx=10, pady=10)

        self.deck_name_label = customtkinter.CTkLabel(self.move_card_window, text="Deck Name:")
        self.deck_name_label.grid(row=2, column=0, padx=10, pady=10)

        self.deck_name_entry = customtkinter.CTkEntry(self.move_card_window)
        self.deck_name_entry.grid(row=2, column=1, padx=10, pady=10)
        
        self.amount_to_add_label = customtkinter.CTkLabel(self.move_card_window, text="Amount to add:")
        self.amount_to_add_label.grid(row=3, column=0, padx=10, pady=10)

        self.amount_to_add_entry = customtkinter.CTkEntry(self.move_card_window)
        self.amount_to_add_entry.grid(row=3, column=1, padx=10, pady=10)

        self.submit_button = customtkinter.CTkButton(self.move_card_window, text="Confirm", command=self.move_card_to_deck_confirm_button_press_event)
        self.submit_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
    
    def import_from_file_popup(self):
        self.import_file_window = customtkinter.CTkToplevel(self)
        self.import_file_window.title("Import From File")


        self.card_file_name_label = customtkinter.CTkLabel(self.import_file_window, text="Card File Name:")
        self.card_file_name_label.grid(row=1, column=0, padx=10, pady=10)

        self.card_file_name_entry = customtkinter.CTkEntry(self.import_file_window)
        self.card_file_name_entry.grid(row=1, column=1, padx=10, pady=10)

        self.deck_file_name_label = customtkinter.CTkLabel(self.import_file_window, text="Deck File Name:")
        self.deck_file_name_label.grid(row=2, column=0, padx=10, pady=10)

        self.deck_file_name_entry = customtkinter.CTkEntry(self.import_file_window)
        self.deck_file_name_entry.grid(row=2, column=1, padx=10, pady=10)

        self.import_button = customtkinter.CTkButton(self.import_file_window, text="Import", command=self.file_import_confirm_button_press_event)
        self.import_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def add_card_button_press_event(self):
        ''' 
        notifies controller that we have input ready for a new card to be added 
        '''
        name = self.card_name_entry.get()
        number = self.card_number_entry.get()
        set_total = self.set_total_entry.get() if self.set_total_entry.get() else None
        amount = self.amount_to_add_entry.get() if self.amount_to_add_entry.get() else 1
        is_promo = self.is_promo_entry.get() if self.is_promo_entry.get() else False

        if name and number:
            self.controller.add_to_db_from_input(card_name=name, card_number=number, set_total=set_total, amount=amount, is_promo=is_promo)
            self.current_cards = None
            self.display_cards()
        else:
            print("Name and number are required to add a card")

    def move_card_to_deck_confirm_button_press_event(self):
        '''
            tells controller to add selected card to given deck name
        '''
        deck_name = self.deck_name_entry.get()
        card = self.selected_card
        amount = self.amount_to_add_entry.get()
        self.controller.move_card_to_deck(deck_name, card, int(amount))
        self.display_cards()
        self.move_card_window.destroy()

    def remove_card_button_press_event(self):
        deck_id = self.selected_deck_id
        amount = int(self.amount_to_remove_entry.get())
        self.controller.remove_card(deck_id=deck_id, card=self.selected_card, amount=amount)
        self.selected_card = None
        self.current_cards = None
        self.display_cards()
        self.remove_card_window.destroy()

    def file_import_confirm_button_press_event(self):
        card_file_name = self.card_file_name_entry.get()
        deck_file_name = self.deck_file_name_entry.get()

        if not card_file_name and not deck_file_name:
            print("missing file names")
            self.remove_card_window.destroy()
            return

        if card_file_name:
            self.controller.load_cards_from_csv(csv_file="card_input_csvs/"+card_file_name)

        if deck_file_name:
            self.controller.load_decks_from_csv(csv_file="card_input_csvs/"+deck_file_name)
        self.current_cards = None
        self.display_cards()
        self.import_file_window.destroy()
    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def card_picture_press_event(self, card_info):
        print(card_info)
        self.selected_card = card_info
        self.selected_card_label.configure(text=f'{self.selected_card["name"]}, {self.selected_card["number"]}/{self.selected_card["set_total"]}') if self.selected_card else ""

if __name__ == '__main__':
    dma = DeckManagerApp()
    dma.mainloop()