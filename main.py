# from app.app import App
from app.deck_manager import DeckManagerApp
if __name__ == "__main__":
    # app = App()
    # app.mainloop()
    dm = DeckManagerApp()
    dm.mainloop()