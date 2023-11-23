import threading
import tkinter as tk
from tkinter import ttk
from typing import Callable

import customtkinter as ctk

from best_formation import main as formation_main
from player import main as player_main, player_all_roles
from reader import main as reader_main, gather_all_roles
from staff import main as staff_main
from utils.role_config import TeamConfig

config = TeamConfig.read_config()
selectable_teams = list(config.keys())


def threaded(func):
    def wrap(data: "Data", *args, **kwargs):
        print(f"---------------- {func.__name__} ----------------")
        threading.Thread(func(data, *args, **kwargs))
        data.save.set(False)
        return
    return wrap


class Data:
    def __init__(self):
        self.save = tk.BooleanVar()
        self.team = tk.StringVar()

    @threaded
    def player_in_team(self):
        player_main(team=self.team.get(), save=self.save.get())

    @threaded
    def best_roles(self):
        player_all_roles(team=self.team.get())

    @threaded
    def read_players(self):
        reader_main(team=self.team.get(), save=self.save.get())

    @threaded
    def read_all_roles(self):
        gather_all_roles(team=self.team.get())

    @threaded
    def best_formation(self):
        formation_main(team=self.team.get())

    @threaded
    def staff(self):
        staff_main()


def execute_command():
    # selected_file = file_var.get()
    # selected_team = team_var.get()
    # args = {
    #     "team": selected_team,
    #     "save": save_var.get(),
    #     "args": MockClass(False)
    # }

    # print("-------", selected_file, " for ", selected_team, "---------")
    # selectable_files[selected_file](**args)
    print("a")


def create_app():
    app = ctk.CTk()
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app.attributes('-topmost', True)
    app.title("FM23 Utils")

    data = Data()

    # Create a button row at the top
    data_frame = create_data_frame(app, data)
    data_frame.pack(side=tk.TOP, fill=tk.X)

    reader_frame = get_reader_frame(app, data)
    reader_frame.pack(side=tk.LEFT, fill='x')

    parser_frame = get_parser_frame(app, data)
    parser_frame.pack(side=tk.RIGHT, fill='x')

    return app


def get_parser_frame(app: ctk.CTk, data: Data) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(app)
    button = tk.Label(frame, text="From File", background="antiquewhite3")
    button.pack(pady=10, expand=True, fill='x')
    for text, command in (
            ("Players in Team", data.read_players),
            ("Best Roles", data.read_all_roles),
            ("Best Formation", data.best_formation),
            ("Staff evaluation", data.staff)
    ):
        pack_button(frame, text, command)
    return frame


def get_reader_frame(app: ctk.CTk, data: Data) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(app)
    button = tk.Label(frame, text="From Screenshot", background="antiquewhite3")
    button.pack(pady=10, expand=True, fill='x')
    for text, command in (("Player in Team", data.player_in_team), ("Best Roles", data.best_roles)):
        pack_button(frame, text, command)
    return frame


def pack_button(frame: ctk.CTkFrame, text: str, command: Callable):
    button = tk.Button(frame, text=text, command=command, background="antiquewhite4")
    button.pack(pady=10)


def create_data_frame(app: ctk.CTk, data: Data) -> ctk.CTkFrame:
    data_frame = ctk.CTkFrame(app)

    team_selection = ttk.Combobox(data_frame, textvariable=data.team, values=selectable_teams)
    team_selection.pack(side=tk.LEFT, padx=10)
    data.team.set(selectable_teams[0])
    save_selection = ttk.Checkbutton(data_frame, text="Save", variable=data.save, onvalue=True, offvalue=False)
    save_selection.pack(side=tk.LEFT, padx=10)

    return data_frame


if __name__ == "__main__":
    create_app().mainloop()
