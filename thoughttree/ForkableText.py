import tkinter as tk

from Notebook import Notebook
from ResizingText import ResizingText


class ForkableText(tk.Frame):
    def __init__(self, parent):
        super().__init__()

        self.sheet = ResizingText(parent)
        self.sheet.pack(fill="both", expand=True)
        self.sheet.insert(tk.END, "This is a test\n" * 5)

        self.notebook = Notebook(parent)
        self.notebook.pack(fill="both", expand=True)
        self.bind_all("<Control-o>", self.step2)


    def step2(self, event=None):

        def update_notebook_height(event):
            notebook = event.widget
            current_tab = notebook.nametowidget(notebook.select())
            current_tab.update_idletasks()
            notebook.configure(height=current_tab.winfo_reqheight())

        print("Step 2")
        text_tab1 = ResizingText(self.notebook)
        text_tab2 = ResizingText(self.notebook)
        self.notebook.add(text_tab1, text="Tab 1")
        self.notebook.add(text_tab2, text="Tab 2")
        self.notebook.bind("<<NotebookTabChanged>>", update_notebook_height)
        return "break"
