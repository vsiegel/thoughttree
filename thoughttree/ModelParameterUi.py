from tkinter import SUNKEN

from LabeledEntry import LabeledEntry


class ModelParameterUi():
    def __init__(self):
        self.defaults = {"bd": 1, "relief": SUNKEN}

        pass

    def get_parameter_editor(self):
        return None

class TopPParameterUi(ModelParameterUi):
    def __init__(self):
        super().__init__()

    def validate(self, entry_value):
        try:
            value = float(entry_value)
            if 0 <= value <= 2:
                return True
            else:
                return False
        except ValueError:
            return False

    def get_parameter_editor(self):
        self.temperature_label = LabeledEntry(self, "Temp.:", entry_width=3, validatecommand=self.validate, **self.defaults)




