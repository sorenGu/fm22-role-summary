import subprocess
import sys
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from reader import main as reader_main
from player import main as player_main
from staff import main as staff_main
from utils.role_config import RoleConfig


class MockClass:

    def __init__(self, return_value):
        self.return_value = return_value

    def __getattr__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            return self.return_value


selectable_files = {
    "player": player_main,
    "reader": reader_main,
    "staff": staff_main
}

config = RoleConfig.read_config()
selectable_teams = list(config["teams"].keys())


def execute_command():
    selected_file = file_var.get()
    selected_team = team_var.get()
    args = {
        "team": selected_team,
        "save": save_var.get(),
        "args": MockClass(False)
    }

    print("-------", selected_file, " for ", selected_team, "---------")
    selectable_files[selected_file](**args)


app = ctk.CTk()
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
app.attributes('-topmost', True)
app.title("FM23 Utils")

# Create a button row at the top
button_frame = ctk.CTkFrame(app)
button_frame.pack(side=tk.TOP, fill=tk.X)

file_var = tk.StringVar()
file_selection = ttk.Combobox(button_frame, textvariable=file_var, values=list(selectable_files.keys()))
file_selection.current(0)
file_selection.pack(side=tk.LEFT, padx=10)

team_var = tk.StringVar()
team_selection = ttk.Combobox(button_frame, textvariable=team_var, values=selectable_teams)
team_selection.current(0)
team_selection.pack(side=tk.LEFT, padx=10)

save_var = tk.BooleanVar()
save_selection = ttk.Checkbutton(button_frame, text="Save", variable=save_var, onvalue = True, offvalue = False)
save_selection.pack(side=tk.LEFT, padx=10)

add_button = tk.Button(button_frame, text="Execute", command=execute_command)
add_button.pack(side=tk.RIGHT, padx=10)


if __name__ == "__main__":
    app.mainloop()
