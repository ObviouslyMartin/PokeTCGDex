import customtkinter
import os
from PIL import Image
from database.CardDB import CardDatabase
from utils.cache import DataCache
from features.scrollable_frames import ScrollableLabelButtonFrame

class App(customtkinter.CTk):
    WINDOW_HEIGHT = 720
    WINDOW_WIDTH = 1280

    def __init__(self):
        super().__init__()
        self.title("Card Collection")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        
        # Determine the path to the database file
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'pokemon_cards.db')

        # Database and Cache
        self.db = CardDatabase(self.db_path)
        self.data_cache = DataCache()
        
        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # load images
        path_to_images = os.path.join(os.path.dirname(__file__), '..', 'assets')
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), path_to_images)
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "logo_crop.png")), size=(26, 26))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "home_large.png")), size=(500, 150))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.deck_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "deck.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "deck.png")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))
        
        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)
        
        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text=" Poké TCG Dex", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)
        
        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")
        
        self.create_deck_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Decks",
                                                          fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                          image=self.deck_image, anchor="w", command=self.create_deck_event)
        self.create_deck_button.grid(row=2, column=0, sticky="ew")
        
        self.add_card_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Add Card",
                                                       fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       image=self.add_user_image, anchor="w", command=self.add_card_event)
        self.add_card_button.grid(row=3, column=0, sticky="ew")
        
        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")
        
        # create frames
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame_large_image_label = customtkinter.CTkLabel(self.home_frame, text="", image=self.large_test_image)
        self.home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10)
        
        self.create_deck_frame = None
        self.add_card_frame = None


        self.scrollable_deck_view_frame = ScrollableLabelButtonFrame(master=self.home_frame, width=self.WINDOW_WIDTH/2, command=self.view_card_event, corner_radius=0,label_text="All Decks")
        self.scrollable_deck_view_frame.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        for deck in self.db.get_all_decks():  # add items with images
            self.scrollable_deck_view_frame.add_item(f"{deck[0]}: {deck[1]}")
        # create scrollable label and button frame
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        self.scrollable_card_view_frame = ScrollableLabelButtonFrame(master=self.home_frame, width=self.WINDOW_WIDTH/2, command=self.view_card_event, corner_radius=0,label_text="All Cards")
        self.scrollable_card_view_frame.grid(row=2, column=0, padx=0, pady=0, sticky="nsew")
        for card in self.db.get_all_cards():  # add items with images
            self.scrollable_card_view_frame.add_item(f"{card[0]}: {card[1]}", image=customtkinter.CTkImage(Image.open(os.path.join("", card[8]))))

        

        # select default frame
        self.select_frame_by_name("home")
    
    def home_button_event(self):
        self.select_frame_by_name("home")

    def view_card_event(self, other_item):
        print("this is view card event")
        print(f"this is other item: {other_item}")

    def create_deck_event(self):
        from features.create_deck import CreateDeckFrame
        if self.create_deck_frame is None:
            self.create_deck_frame = CreateDeckFrame(self)
        self.select_frame_by_name("create_deck")
    
    def add_card_event(self):
        from features.add_card import AddCardFrame
        if self.add_card_frame is None:
            self.add_card_frame = AddCardFrame(self)
            print("called addCardFrame")
        self.select_frame_by_name("add_card")
    
    def select_frame_by_name(self, name):
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.create_deck_button.configure(fg_color=("gray75", "gray25") if name == "create_deck" else "transparent")
        self.add_card_button.configure(fg_color=("gray75", "gray25") if name == "add_card" else "transparent")
        
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()

        if name == "create_deck":
            self.create_deck_frame.grid(row=0, column=1, sticky="nsew")
        else:
            if self.create_deck_frame:
                self.create_deck_frame.grid_forget()

        if name == "add_card":
            self.add_card_frame.grid(row=0, column=1, sticky="nsew")
        else:
            if self.add_card_frame:
                self.add_card_frame.grid_forget()
    
    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

if __name__ == "__main__":
    app = App()
    app.mainloop()