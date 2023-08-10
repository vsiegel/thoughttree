import tkinter as tk

from Notebook import Notebook
from Sheet import Sheet


class ResizingText(tk.Text):
    def __init__(self, parent, wrap="word", highlightthickness=0, borderwidth=0, padx=0, pady=0, *args, **kw):
        super().__init__(parent, wrap=wrap, highlightthickness=highlightthickness, borderwidth=borderwidth, font=Sheet.FONT,
            padx=padx, pady=pady, *args, **kw)
        self.old_num_lines = 0
        self.bind("<KeyRelease>", self.adjust_height)

        def yscrollcommand(start, stop):
            print(f"Scroll command: ")
            if start != 0.0 or stop != 1.0:
                self.adjust_height()

        self.configure(yscrollcommand=yscrollcommand)

        def on_return(event=None):
            self.insert(tk.INSERT, "\n")
            self.adjust_height()
            return "break"

        # self.bind("<Return>", on_return)
        self.bind("<Configure>", self.adjust_height)
        self.adjust_height()

    # def on_configure(self, event=None): # todo One Return causes 3 adjust_height() and two on_configure()
    #     print("on_configure")
    #     self.adjust_height(event)

    def adjust_height(self, event=None):
        num_lines = self.count("1.0", "end", 'displaylines')[0]
        print(f"adjust_height: {num_lines=}")
        print(f"adjust_height: {self.winfo_height()=}")
        print(f"adjust_height: {self.winfo_reqheight()=}")

        height = self.winfo_height()
        reqheight = self.winfo_reqheight()
        if num_lines != self.old_num_lines or (height > 1 and height != reqheight):
            self.see(tk.INSERT)
            self.old_num_lines = num_lines
            self.configure(height=num_lines)
            print(f"{type(self.master.master)=}")
            if type(self.master.master) is Notebook:
                self.master.master.event_generate("<<NotebookTabChanged>>")
                print(f"<<NotebookTabChanged>>")
