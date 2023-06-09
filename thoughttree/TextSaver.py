from abc import ABC, abstractmethod

class TextSaver(ABC):

    def __init__(self, widget):
        self.widget = widget

    def text_not_found_error(self):
        pass

    @abstractmethod
    def find_text(self):
        pass

    @abstractmethod
    def find_filename(self):
        pass

    def ask_filename(self, initial_filename):
        return ""

    def write_text(self, text, filename):
        pass

    def save(self):
        text = self.find_text()
        if not text:
            self.text_not_found_error()
            return
        initial_filename = self.find_filename()
        filename = self.ask_filename(initial_filename)
        if not filename:
            return
        self.write_text(text, filename)
