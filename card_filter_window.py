import tkinter as tk
import customtkinter as ctk

class CheckboxDropdown:
    def __init__(self, parent, text="button text", variables={}, command=None):
        # Main button to open the dropdown
        self.main_button = ctk.CTkButton(parent, text=text, command=self.open_dropdown)
        self.main_button.grid(row=0, column=0)

        # Top-level widget (like a new window) that will hold checkboxes
        self.top_level = ctk.CTkToplevel(parent)
        self.top_level.title("Filters")
        print(f'250 / {len(variables)} = {250/len(variables)}')
        self.top_level.geometry(f"200x{27 * len(variables)}")
        # Initially keep it hidden
        self.top_level.withdraw()

        # Place checkboxes inside the top-level window

        self.variables_iter = iter(variables.items())
        # options = 
        last_row = 0
        for i, (type, var) in enumerate(variables.items()):
            chk = ctk.CTkCheckBox(self.top_level, text=type, variable=var, command=command)
            chk.grid(row=i, column=0, sticky='w')
            last_row = i+1
            # self.variables.append(variable)

        # Close button in the dropdown
        close_button = ctk.CTkButton(self.top_level, text="Apply", command=self.close_dropdown)
        close_button.grid(row=last_row)

    def open_dropdown(self):
        self.top_level.deiconify()  # Show the top-level window

    def close_dropdown(self):
        self.top_level.withdraw()  # Hide the top-level window

def this_func():
    print("this func")

def main():
    root = ctk.CTk()
    root.geometry("300x300")
    app = CheckboxDropdown(root, variables=None, command=this_func)
    root.mainloop()

if __name__ == "__main__":
    main()