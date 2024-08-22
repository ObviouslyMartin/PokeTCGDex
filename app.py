import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter
from db_manager import CardDeckManager  # Assuming your backend class is imported
from PIL import Image

class ScrollableLabelButtonFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command = command
        self.radiobutton_variable = customtkinter.StringVar()
        self.label_list = []
        self.button_list = []

    def add_item(self, item, image=None):
        label = customtkinter.CTkLabel(self, text=item, image=image, compound="left", padx=5, anchor="w")
        button = customtkinter.CTkButton(self, text="Command", width=100, height=24)
        if self.command is not None:
            button.configure(command=lambda: self.command(item))
        label.grid(row=len(self.label_list), column=0, pady=(0, 10), sticky="w")
        button.grid(row=len(self.button_list), column=1, pady=(0, 10), padx=5)
        self.label_list.append(label)
        self.button_list.append(button)

    def remove_items(self):
        for label, button in zip(self.label_list, self.button_list):
            # if item == label.cget("text"):
            label.destroy()
            button.destroy()
            self.label_list.remove(label)
            self.button_list.remove(button)
            return
# class CardDeckApp:
#     def __init__(self, master):
#         self.master = master
#         self.master.title('Card Deck Manager')

#         self.db_manager = CardDeckManager('test_db.db')  # Provide your actual database path

#         self.frame = tk.Frame(self.master)
#         self.frame.pack(padx=10, pady=10)

#         self.deck_label = tk.Label(self.frame, text="Select Deck:")
#         self.deck_label.pack()

#         self.deck_listbox = tk.Listbox(self.frame, height=10, width=50, exportselection=False)
#         self.deck_listbox.pack()

#         self.refresh_decks_button = tk.Button(self.frame, text="Refresh Decks", command=self.refresh_decks)
#         self.refresh_decks_button.pack(pady=5)

#         self.show_cards_button = tk.Button(self.frame, text="Show Cards in Deck", command=self.show_cards)
#         self.show_cards_button.pack(pady=5)

#         self.add_deck_button = tk.Button(self.frame, text="Add New Deck", command=self.add_deck)
#         self.add_deck_button.pack(pady=5)

#         self.remove_deck_button = tk.Button(self.frame, text="Remove Selected Deck", command=self.remove_deck)
#         self.remove_deck_button.pack(pady=5)

#         self.cards_frame = tk.Frame(self.master)
#         self.cards_frame.pack(padx=10, pady=10)

#         self.cards_label = tk.Label(self.cards_frame, text="Cards in Deck:")
#         self.cards_label.pack()

#         self.cards_listbox = tk.Listbox(self.cards_frame, height=10, width=50, exportselection=False)
#         self.cards_listbox.pack()

#         self.add_card_button = tk.Button(self.cards_frame, text="Add Card to Deck", command=self.add_card_to_deck)
#         self.add_card_button.pack(pady=5)

#         self.remove_card_button = tk.Button(self.cards_frame, text="Remove Card from Deck", command=self.remove_card_from_deck)
#         self.remove_card_button.pack(pady=5)

#         self.refresh_decks()

#     def refresh_decks(self):
#         self.deck_listbox.delete(0, tk.END)
#         decks = self.db_manager.get_decks()
#         for deck in decks:
#             self.deck_listbox.insert(tk.END, deck)

#     def show_cards(self):
#         selected_deck = self.deck_listbox.get(tk.ANCHOR)
#         if selected_deck:
#             self.cards_listbox.delete(0, tk.END)
#             deck_cards = self.db_manager.get_decks().get(selected_deck, [])
#             for card in deck_cards:
#                 self.cards_listbox.insert(tk.END, f"{card['name']} (Count: {card['count']})")

#     def add_deck(self):
#         deck_name = simpledialog.askstring("Input", "Enter new deck name:")
#         if deck_name:
#             self.db_manager.create_deck(deck_name)
#             self.refresh_decks()

#     def remove_deck(self):
#         selected_deck = self.deck_listbox.get(tk.ANCHOR)
#         if selected_deck:
#             self.db_manager.delete_deck(selected_deck)
#             self.refresh_decks()

#     def add_card_to_deck(self):
#         selected_deck = self.deck_listbox.get(tk.ANCHOR)
#         if not selected_deck:
#             messagebox.showerror("Error", "No deck selected")
#             return

#         card_id = simpledialog.askinteger("Input", "Enter Card ID:")
#         if card_id is None:
#             return

#         count = simpledialog.askinteger("Input", "Enter count of cards to add:")
#         if count is None:
#             return

#         result = self.db_manager.add_card_to_deck(selected_deck, card_id, count)
#         if result == "Card added successfully":
#             messagebox.showinfo("Success", result)
#             self.show_cards()
#         else:
#             messagebox.showerror("Error", result)

#     def remove_card_from_deck(self):
#         selected_deck = self.deck_listbox.get(tk.ANCHOR)
#         if not selected_deck:
#             messagebox.showerror("Error", "No deck selected")
#             return

#         selected_card_info = self.cards_listbox.get(tk.ANCHOR)
#         if not selected_card_info:
#             messagebox.showerror("Error", "No card selected")
#             return

#         card_id = int(selected_card_info.split()[0])  # Assuming the card ID is the first item in the listbox entry
#         count = simpledialog.askinteger("Input", "Enter count of cards to remove:")
#         if count is None:
#             return

#         result = self.db_manager.remove_card_from_deck(selected_deck, card_id, count)
#         if isinstance(result, int) and result > 0:
#             messagebox.showinfo("Success", "Card removed successfully")
#             self.show_cards()
#         else:
#             messagebox.showerror("Error", "Failed to remove card")

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = CardDeckApp(root)
#     root.mainloop()
#     app.db_manager.close_connection()

class CardDeckApp:
    def __init__(self, master):
        self.master = master
        self.master.title('Card Deck Manager')
        self.db_manager = CardDeckManager('test_db.db')

        self.frame = tk.Frame(self.master)
        self.frame.pack(padx=10, pady=10)

        self.deck_label = tk.Label(self.frame, text="Select Deck:")
        self.deck_label.pack()

        self.deck_listbox = tk.Listbox(self.frame, height=10, width=50, exportselection=False)
        self.deck_listbox.pack()
        self.deck_listbox.bind("<<ListboxSelect>>", self.show_cards)

        self.refresh_decks_button = tk.Button(self.frame, text="Refresh Decks", command=self.refresh_decks)
        self.refresh_decks_button.pack(pady=5)

        self.add_deck_button = tk.Button(self.frame, text="Add New Deck", command=self.add_deck)
        self.add_deck_button.pack(pady=5)

        self.remove_deck_button = tk.Button(self.frame, text="Remove Selected Deck", command=self.remove_deck)
        self.remove_deck_button.pack(pady=5)

        # Use the ScrollableLabelButtonFrame
        self.cards_frame = ScrollableLabelButtonFrame(self.master, command=self.card_command)
        self.cards_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_decks()

    def card_command(self, item):
        messagebox.showinfo("Action", f"Command executed for {item}")

    def show_cards(self, event=None):
        self.cards_frame.remove_items()
        selected_deck = self.deck_listbox.get(tk.ANCHOR)
        if selected_deck:
            deck_cards = self.db_manager.get_decks().get(selected_deck, [])
            row, col = 0, 0
            for card in deck_cards:
                print(card)
                image_path = card["image_path"]
                image = Image.open(image_path)
                photo = customtkinter.CTkImage(image, size=(180, 240))

                card_label = customtkinter.CTkLabel(self.cards_frame, image=photo)
                card_label.image = photo
                card_label.grid(row=row, column=col, padx=5, pady=5)

                count_label = customtkinter.CTkLabel(self.cards_frame, text=f"x{card['count']}", font=customtkinter.CTkFont(size=14))
                count_label.grid(row=row+1, column=col, padx=5, pady=5)

                col += 1
                if col >= 5:
                    col = 0
                    row += 2

    def refresh_decks(self):
        self.deck_listbox.delete(0, tk.END)
        decks = self.db_manager.get_decks()
        for deck in decks:
            self.deck_listbox.insert(tk.END, deck)

    def add_deck(self):
        deck_name = simpledialog.askstring("Input", "Enter new deck name:")
        if deck_name:
            self.db_manager.create_deck(deck_name)
            self.refresh_decks()

    def remove_deck(self):
        selected_deck = self.deck_listbox.get(tk.ANCHOR)
        if selected_deck:
            self.db_manager.delete_deck(selected_deck)
            self.refresh_decks()

if __name__ == "__main__":
    root = customtkinter.CTk()
    app = CardDeckApp(root)
    root.mainloop()