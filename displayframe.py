import customtkinter
from PIL import Image, ImageTk

class DisplayFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, parent, callback, **kwargs):
        super().__init__(parent, **kwargs)
        self.items = []
        self.callback = callback
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(10, weight=1)
        self.total_cards = 0

    def update_items(self, items):
        """
        Update the frame with new items to display.
        :param items: List of dictionaries, each containing item data.
        """
        self.clear_items()
        self.items = items
        # self.callback = callback
        self.display_items()

    def clear_items(self):
        """ Clear all widgets from the frame. """
        for widget in self.winfo_children():
            widget.destroy()

    def display_items(self):
        row, col = 0,0
        num_cards = 0
        target_dimension = 210  # Targeting a width or height of 240 pixels
        for item_info in self.items:
            image = Image.open(item_info["image_path"])
            photo_width, photo_height = self.__resize_image(original_width=image.width, original_height=image.height, target_dimension=target_dimension, scale_factor=1.2)
            photo = customtkinter.CTkImage(image, size=(photo_width, photo_height))
            item_button = customtkinter.CTkButton(self, 
                                                  image=photo, 
                                                  text=f"x{item_info['quantity']}", 
                                                  command=lambda item=item_info: self.callback(item), 
                                                  fg_color="transparent", hover_color="blue", 
                                                  anchor="N")
            item_button.image = photo  # keep a reference!
            item_button.grid(row=row, column=col, padx=5, pady=5)

            # count_label = customtkinter.CTkLabel(self, text=, font=customtkinter.CTkFont(size=14))
            # count_label.grid(row=row+1, column=col, padx=5, pady=5)
            num_cards += item_info['quantity']
            
            col += 1
            if col >= 5:
                col = 0
                row += 2

        self.total_cards = num_cards

    def __resize_image(self, original_width, original_height, target_dimension, is_width=True, scale_factor=1.0):
        """
        Resize the image while maintaining aspect ratio.
        
        Parameters:
            original_width (int): The original width of the image.
            original_height (int): The original height of the image.
            target_dimension (int): Target size of the width or height.
            is_width (bool): True if target_dimension is width, False if height.
            scale_factor (float): Multiplier to adjust the final size, default is 1.0.

        Returns:
            tuple: New size of the image as (width, height).
        """
        if is_width:
            # Calculate the ratio based on the width
            ratio = target_dimension / original_width
        else:
            # Calculate the ratio based on the height
            ratio = target_dimension / original_height
        
        # Calculate new dimensions
        new_width = int(original_width * ratio * scale_factor)
        new_height = int(original_height * ratio * scale_factor)
        
        return new_width, new_height

    def get_card_quantity(self):
        return self.total_cards