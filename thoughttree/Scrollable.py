import tkinter as tk
from tkinter import ttk

from Notebook import Notebook
from ResizingText import ResizingText


class Scrollable(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.frame = tk.Frame(self.canvas, bg="white")
        self.frame_id = self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.frame.bind("<Configure>", self.update_scrollregion)
        self.canvas.bind("<Configure>", self.update_frame_width)

    def update_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_frame_width(self, event):
        self.canvas.itemconfig(self.frame_id, width=event.width)


def main():
    from UI import UI
    root = UI()
    root.geometry("500x500")

    scrollable = Scrollable(root)
    scrollable.pack(fill="both", expand=True)

    text = ResizingText(scrollable.frame)
    text.pack(fill="both", expand=True)

    notebook = Notebook(scrollable.frame)
    notebook.pack(fill="both", expand=True, side="left", anchor="nw") # , sticky="ew")  # Add sticky="ew"

    text_tab1 = ResizingText(notebook)
    text_tab2 = ResizingText(notebook)
    notebook.add(text_tab1, text="Tab 1")
    notebook.add(text_tab2, text="Tab 2")


    def update_notebook_height(event):
        notebook = event.widget
        current_tab = notebook.nametowidget(notebook.select())
        current_tab.update_idletasks()
        notebook.configure(height=current_tab.winfo_reqheight())

    notebook.bind("<<NotebookTabChanged>>", update_notebook_height)

    root.mainloop()

if __name__ == "__main__":
    main()
