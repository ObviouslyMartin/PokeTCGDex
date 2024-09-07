import customtkinter
from card_filter_window import CheckboxDropdown
import os
from PIL import Image
from controller import Controller
import logging
logger = logging.getLogger(__name__)
# The View
class DeckManagerApp(customtkinter.CTk):
    WINDOW_HEIGHT = 1169
    WINDOW_WIDTH = 1800
   
    def __init__(self, db_path):
        super().__init__()
        
        self.title("Deck Manager")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        
        self.controller = Controller(db_path)
        
        # Set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.selected_deck_id = -1
        self.current_cards = None

        self.load_assets()

        self.create_main_frame()
        self.create_navigation_frame()
        self.create_filter_frame()
        
        # load cards and decks
        self.load_decks()
        self.display_cards()

    ##############
    ''' Assets '''
    ##############
    def load_assets(self):
        # Load images

        image_path = "assets"
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

    def create_main_frame(self):
        # Main View
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nswe")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Card Display Frame
        self.card_display_frame = customtkinter.CTkScrollableFrame(self.main_frame)
        self.card_display_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nswe")
        self.card_display_frame.grid_columnconfigure(10, weight=1)
    
    def create_filter_frame(self):
         # Filter Buttons and Info
        self.filter_frame = customtkinter.CTkFrame(self.main_frame)
        self.filter_frame.grid(row=0, column=0, padx=20, pady=10, sticky="we")
        self.filter_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # search box
        self.search_box = customtkinter.CTkEntry(master=self.filter_frame, width=280, placeholder_text="Search Cards...", )
        self.search_box.grid(row=0,column=2, sticky='w')
        self.search_button = customtkinter.CTkButton(self.filter_frame, width=70, text="Search", command=self.display_cards)
        self.search_button.grid(row=0,column=3, sticky='w')
        # total cards count     
        self.total_cards_label = customtkinter.CTkLabel(self.filter_frame, text=0)
        self.total_cards_label.grid(row=0,column=4, sticky='w')
        self.create_filter_options()
        self.create_filter_buttons()

    def create_navigation_frame(self):
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
        self.selected_card_label.grid(row=8, column=0, padx=10, pady=10)
        
        self.create_navigation_buttons()

    ######################
    ''' Filter Options '''
    ######################
    def create_filter_options(self):
        # Checkbox options
        self.special_filters = { #sdk_card["abilities"]
            'Ability': customtkinter.BooleanVar(),
        }
        self.supertypes_filter = { # sdk_card["supertypes"]
            'Energy': customtkinter.BooleanVar(),
            'Trainer': customtkinter.BooleanVar(),
            'Pokémon': customtkinter.BooleanVar(),
        }
        self.cardtype_filter = { # sdk_card["sub_types"]
            # 'Basic': customtkinter.BooleanVar(),
            # 'Special': customtkinter.BooleanVar(),
            # 'Stage 1': customtkinter.BooleanVar(),
            # 'Stage 2': customtkinter.BooleanVar(),
            # 'Item': customtkinter.BooleanVar(),
            # 'Supporter': customtkinter.BooleanVar(),
            # 'Stadium': customtkinter.BooleanVar(),
            # 'Pokémon Tool': customtkinter.BooleanVar(),
        }
        self.cardcolor_filter = { # sdk_card["card_types"]
            'Colorless': customtkinter.BooleanVar(),
            'Darkness': customtkinter.BooleanVar(),
            'Fighting': customtkinter.BooleanVar(),
            'Fire': customtkinter.BooleanVar(),
            'Grass': customtkinter.BooleanVar(),
            'Lightning': customtkinter.BooleanVar(),
            'Metal': customtkinter.BooleanVar(),
            'Psychic': customtkinter.BooleanVar(),
            'Water': customtkinter.BooleanVar(),
        }
    ###############
    ''' BUTTONS '''
    ###############
    def create_navigation_buttons(self):
        button_configs = [
            ("Add Deck", self.add_deck_popup, 3),
            ("Add Card", self.add_card_popup, 4),
            ("Move Card to Deck", self.move_card_to_deck_popup, 5),
            ("Remove Card From Deck", self.remove_card_popup, 6),
            ("Import From File", self.import_from_file_popup, 7),
            ("Export To File", self.controller.export_db, 8),
        ]
        for text, command, row in button_configs:
            self.create_button(self.navigation_frame, text, command, row, 0, sticky='s')

    def create_button(self, frame, text, command, row, column, pady=10, padx=20, sticky=""):
        button = customtkinter.CTkButton(frame, text=text, command=command)
        button.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
        return button
    
    def create_filter_buttons(self):
        # apply filters button 
        self.filters_button = CheckboxDropdown(self.filter_frame, text="Apply Filters", variables=self.special_filters | self.supertypes_filter | self.cardcolor_filter| self.cardtype_filter, command=self.display_cards)

    #####################
    ''' Functionality '''
    #####################
    def load_decks(self):
        deck_names = ["-1: All Cards"] + [f"{deck[0]}: {deck[1]['name']}" for deck in self.controller.get_decks().items()]
        self.deck_combobox.configure(values=deck_names)

    def on_deck_select(self, selected_deck):
        self.selected_deck_id = int(selected_deck.split(":")[0])
        self.current_cards = None
        self.display_cards()

    def __get_filters(self):
        # special = [type for type, var in self.special_filters.items() if var.get()]
        # super_types = [type for type, var in self.supertypes_filter.items() if var.get()]
        # color = [type for type, var in self.cardcolor_filter.items() if var.get()]
        # sub_type = [type for type, var in self.cardtype_filter.items() if var.get()]
        name = self.search_box.get()
        print(name)
        ret_filters = {}
        # if len(special) != 0:
        #     ret_filters["special"] = special
        # if len(super_types) != 0:
        #     ret_filters["super_types"] = super_types
        # if len(color) != 0:
        #     ret_filters["color"] = color
        # if len(sub_type) != 0:
        #     ret_filters ["sub_type"] = sub_type
        if name:
            ret_filters["name"] = name
        return ret_filters
        

    def display_cards(self):
        for widget in self.card_display_frame.winfo_children():
            self.total_cards_label.configure(text=0)
            widget.destroy()
        selected_filters = self.__get_filters()

        # if not self.current_cards:
        self.current_cards = self.controller.get_cards(deck_id=self.selected_deck_id, filters=selected_filters)

        self.__display_cards(filtered_cards=self.current_cards)

    def __display_cards(self, filtered_cards):
        row, col = 0, 0
        num_cards = 0
        for card_info in filtered_cards:
            image = Image.open(card_info["image_path"])
            photo = customtkinter.CTkImage(image, size=(230, 300))

            card_label = customtkinter.CTkButton(self.card_display_frame, corner_radius=5, width=180, height=240, image=photo, text="")
            card_label = customtkinter.CTkButton(self.card_display_frame, image=photo, text="", 
                                                command=lambda card=card_info: self.card_picture_press_event(card))
            card_label.grid(row=row, column=col, padx=5, pady=5)

            count_label = customtkinter.CTkLabel(self.card_display_frame, text=f"x{card_info['quantity']}", font=customtkinter.CTkFont(size=14))
            count_label.grid(row=row+1, column=col, padx=5, pady=5)
            num_cards += card_info['quantity']
            self.total_cards_label.configure(text=num_cards)
            col += 1
            if col >= 6:
                col = 0
                row += 2


    #################
    ''' UI Events '''
    #################

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

        self.create_button(add_deck_window, "Add Deck", command=submit_add_deck, row=1, column=1, padx=10, pady=10)
        # submit_button = customtkinter.CTkButton(add_deck_window, text="Add Deck", command=submit_add_deck)
        # submit_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

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

        self.added_card_label = customtkinter.CTkLabel(self.add_card_window, text="")
        self.added_card_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10)
    
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
            new_ids = self.controller.add_to_db_from_input(card_name=name, card_number=number, set_total=set_total, amount=amount, is_promo=is_promo)
            self.current_cards = None
            self.added_card_label.configure(text=f'Successfully added:\n{name}, {number}/{set_total}\nAmount: x{amount}')
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
        self.current_cards = None
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
            logger.warning(f'card file name and deck file name are empty')
            self.remove_card_window.destroy()
            return

        if card_file_name:
            self.controller.load_cards_from_csv(csv_file="card_input_csvs/"+card_file_name+'.csv')

        if deck_file_name:
            self.controller.load_decks_from_csv(csv_file="card_input_csvs/"+deck_file_name+'.csv')
        self.current_cards = None
        self.load_decks()
        self.display_cards()
        self.import_file_window.destroy()
        
    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def card_picture_press_event(self, card_info):
        print(card_info)
        self.selected_card = card_info
        self.selected_card_label.configure(text=f'{self.selected_card["name"]}, {self.selected_card["number"]}/{self.selected_card["set_total"]}') if self.selected_card else ""

if __name__ == '__main__':
    print("run with main.py")