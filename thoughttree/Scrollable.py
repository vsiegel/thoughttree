import tkinter as tk
from tkinter import ttk

from Notebook import Notebook


class Scrollable(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.frame = tk.Frame(self.canvas, background="white")
        self.frame_id = self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.frame.bind("<Configure>", self.update_scrollregion)
        self.canvas.bind("<Configure>", self.update_frame_width)

    def update_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_frame_width(self, event):
        self.canvas.itemconfig(self.frame_id, width=event.width)


class AutoResizingText(tk.Text):
    def __init__(self, parent, wrap="word", highlightthickness=0, borderwidth=0, *args, **kwargs):
        super().__init__(parent, wrap=wrap, highlightthickness=highlightthickness, borderwidth=borderwidth, *args, **kwargs)
        self.bind("<KeyRelease>", self.adjust_height)

        def on_return(event=None):
            self.insert(tk.INSERT, "\n")
            self.adjust_height()
            return "break"
        self.bind("<Return>", on_return)

        self.old_num_lines = 0
        self.adjust_height()

    def adjust_height(self, event=None):
        num_lines = self.count("1.0", "end", 'displaylines')[0]
        if num_lines != self.old_num_lines:
            print(f"Change {self.old_num_lines} -> {num_lines}")
            self.old_num_lines = num_lines
            self.configure(height=num_lines)
            if type(self.master) is ttk.Notebook:
                self.master.event_generate("<<NotebookTabChanged>>")



def update_notebook_height(event):
    notebook = event.widget
    current_tab = notebook.nametowidget(notebook.select())
    current_tab.update_idletasks()
    notebook.configure(height=current_tab.winfo_reqheight())

# def create_tab(notebook):
#     tab = tk.Frame(notebook)
#     notebook.add(tab, text=f"Tab {len(notebook.tabs()) + 1}")
#     text = AutoResizingText(tab, notebook, wrap="word")
#     text.pack(fill="both", expand=True, padx=1, pady=1)
#     notebook.bind("<<NotebookTabChanged>>", update_notebook_height)
#     return tab

def main():
    from UI import UI
    root = UI()
    root.geometry("500x500")

    scrollable = Scrollable(root)
    scrollable.pack(fill="both", expand=True)

    text = AutoResizingText(scrollable.frame)
    text.pack(fill="both", expand=True)

    notebook = Notebook(scrollable.frame)
    notebook.pack(fill="both", expand=True, side="left", anchor="nw") # , sticky="ew")  # Add sticky="ew"

    text_tab1 = AutoResizingText(notebook)
    text_tab2 = AutoResizingText(notebook)
    notebook.add(text_tab1, text="Tab 1")
    notebook.add(text_tab2, text="Tab 2")

    notebook.bind("<<NotebookTabChanged>>", update_notebook_height)

    root.mainloop()

if __name__ == "__main__":
    main()
