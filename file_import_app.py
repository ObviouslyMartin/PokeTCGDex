import customtkinter as ctk

class file_import_box():
    def __init__(self, parent, geometry='700x450'):
        self.top_level = ctk.CTkToplevel(parent)
        self.title("Import From File")
        self.geometry(geometry)

        self.my_text = ctk.CTkLabel(self, width=600, height=300)
        self.my_text.pack(pady=20)

        self.my_button = ctk.CTkButton(self, text="Open File", command=self.file)
        self.my_button.pack(pady=20)

    def file(self):
        self.my_file = ctk.filedialog.askopenfilename(initialdir="/Users/martinplut/Documents/Projects/CardManager/card_input_csvs", title="Select a File", filetypes=(("CSV Files", "*.csv"),))

        # check if file selected
        if self.my_file:
            #open and read here
            self.my_text.insert(ctk.END, self.my_file)        

if __name__ == '__main__':
    app = file_import_box() 
    app.mainloop()