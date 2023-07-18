import tkinter as tk

from Menu import Menu
from Text import Text
from menu_help import menu_help


class ModelsMenu(Menu):
    def __init__(self, parent, thoughttree, label):
        super().__init__(parent, label, menu_help=menu_help, tearoff=False)
        self.ui = thoughttree

        self.fixed_model_menu_items = -1
        self.add_separator()
        self.item("Reload available models", None, self.load_available_models)


    def load_available_models(self, event=None):
        if self.fixed_model_menu_items == -1:
            self.fixed_model_menu_items = self.index(tk.END) + 1
        present_items = self.index(tk.END) + 1
        if present_items > self.fixed_model_menu_items:
            self.delete(0, present_items - self.fixed_model_menu_items - 1)
        for i, model_name in enumerate(self.ui.model.get_available_models()):
            if model_name == "gpt-4":
                key = "<Control-Alt-Key-4>"
            elif model_name == "gpt-3.5-turbo":
                key = "<Control-Alt-Key-3>"
            else:
                key = None
            command = lambda e, m=model_name: self.ui.set_model(m)
            self.item(model_name, key, command, index=i)
