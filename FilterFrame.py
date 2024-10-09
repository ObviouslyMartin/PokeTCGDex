import customtkinter as customtkinter
from card_filter_window import CheckboxDropdown

class FilterFrame(customtkinter.CTkFrame):
    def __init__(self, parent, command, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.parent = parent
        self.command = command
        self.total_cards_label = customtkinter.CTkLabel(self, text=0)
        self.total_cards_label.grid(row=0, column=3, sticky='w')
        self.create_filter_buttons()
        self.create_search_box()

    def create_search_box(self):
        self.search_box = customtkinter.CTkEntry(self, width=280, placeholder_text="Search Cards...")
        self.search_box.grid(row=0, column=1, sticky='w')
        self.search_button = customtkinter.CTkButton(self, width=70, text="Search", command=self.command)
        self.search_button.grid(row=0, column=1, sticky='w', padx=290)

    def create_filter_buttons(self):
        self.create_filter_options()
        self.filters_button = CheckboxDropdown(self, text="Apply Filters",
                                               variables=self.special_filters | self.supertypes_filter | self.cardcolor_filter | self.cardtype_filter | self.rarity_filter,
                                               command=self.command)    
        
    def get_filters(self):
        special = [type for type, var in self.special_filters.items() if var.get()]
        super_types = [type for type, var in self.supertypes_filter.items() if var.get()]
        color = [type for type, var in self.cardcolor_filter.items() if var.get()]
        sub_type = [type for type, var in self.cardtype_filter.items() if var.get()]
        rarity = [type for type, var in self.rarity_filter.items() if var.get()]
        name = self.search_box.get() 
        ret_filters = {}
        if len(special) != 0:
            ret_filters["special"] = special
        if len(super_types) != 0:
            ret_filters["super_types"] = super_types
        if len(color) != 0:
            ret_filters["color"] = color
        if len(rarity) != 0:
            ret_filters["rarity"] = rarity
        if len(sub_type) != 0:
            ret_filters ["sub_type"] = sub_type
        if name:
            ret_filters["name"] = name
        return ret_filters

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
            'Basic': customtkinter.BooleanVar(),
            'Special': customtkinter.BooleanVar(),
            'Stage 1': customtkinter.BooleanVar(),
            'Stage 2': customtkinter.BooleanVar(),
            'Item': customtkinter.BooleanVar(),
            'Supporter': customtkinter.BooleanVar(),
            'Stadium': customtkinter.BooleanVar(),
            'Pokémon Tool': customtkinter.BooleanVar(),
        }
        self.cardcolor_filter = { # sdk_card["card_types"]
            'Colorless': customtkinter.BooleanVar(),
            'Darkness': customtkinter.BooleanVar(),
            'Dragon': customtkinter.BooleanVar(),
            'Fighting': customtkinter.BooleanVar(),
            'Fire': customtkinter.BooleanVar(),
            'Grass': customtkinter.BooleanVar(),
            'Lightning': customtkinter.BooleanVar(),
            'Metal': customtkinter.BooleanVar(),
            'Psychic': customtkinter.BooleanVar(),
            'Water': customtkinter.BooleanVar(),
        }
        # rarities = self.controller.get_rarities()
        # self.rarity = dict()
        # for rarity in rarities:
        #     self.rarity[rarity[0]] = customtkinter.BooleanVar()
        self.rarity_filter = { # sdk_card["card_types"]
            'Common': customtkinter.BooleanVar(),
            'Uncommon': customtkinter.BooleanVar(),
            'Rare': customtkinter.BooleanVar(),
            'Double Rare': customtkinter.BooleanVar(),
            'Ultra Rare': customtkinter.BooleanVar(),
            'Hyper Rare': customtkinter.BooleanVar(),
            'Illustration Rare': customtkinter.BooleanVar(),
            'Special Illustration Rare': customtkinter.BooleanVar(),
            'Rare Holo': customtkinter.BooleanVar(),
            'Rare Holo V': customtkinter.BooleanVar(),
            'Rare Holo VSTAR': customtkinter.BooleanVar(),
            'Rare Holo VMAX': customtkinter.BooleanVar(),
            'Promo': customtkinter.BooleanVar(),
            'Shiny Rare': customtkinter.BooleanVar(),
            'ACE SPEC Rare': customtkinter.BooleanVar(),
        }
    