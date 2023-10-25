import tkinter as tk
from tkinter import ttk, BOTH, LEFT, RIGHT, VERTICAL, NW, Y, X, INSERT, CURRENT, TOP

import tools



class EventPlayer:
    def __init__(self, w: tk.Widget):
        self.widget = w

        def lines(n: int) -> str:
            """:return: str - n lines with the numbers to str 0 to (n-1) with newlines between"""
            return "\n".join(list(map(str, range(n))))


        # events = "\n".join([chr(i) for i in range(50, 70)])
        # events = [chr(i) for i in range(65, 85)]
        # events = [4, 5, 6, 7]
        # events = lines(15)
        # events = (["<X>", "<Right>", "<Y>",])
        events = (["a", "b", "c", "\n", "a", "<b>", "c", "\n", "foo", "bar", 500, "a", "bbbb", ])
                  # + ["<<Undo>>"] * 5 + ["<<Redo>>"] * 5)
        # events = ["a", "b"]

        def ttt():
            w.event_generate("<Key-i>")
            # widget.event_generate("<Right>")
            w.update_idletasks()
            w.update()
            w.event_generate("<Key-x>")

        # root.after(1000, lambda : self.play(events))
        # self.widget.bind("<Key>", lambda e: print(e.__dict__), add=True)
        self.widget.bind("<Escape>", lambda e: self.widget.winfo_toplevel().destroy())
        self.widget.bind("<Control-t>", lambda e: ttt())
        self.widget.bind("<Alt-a>", lambda e: w.event_generate("<a>"))
        self.widget.bind("<Alt-b>", lambda e: w.event_generate("<b>"))
        self.widget.bind("<Control-Alt-Shift-P>", lambda e: self.play(events))
        # self.widget.bind("<FocusIn>", lambda e: self.play(events))
        # tools.bind_all_events(self.widget)

    def generate(self, event):
        w = self.widget
        print(f"-{w.index(INSERT)} {event=}")
        w.event_generate(event, state=16, x=0, y=0)
        w.update()
        w.update_idletasks()
        print(f"+{w.index(INSERT)} {event=}")


    def play(self, events, start=0):
        print(f"play: {start} {events=}", flush=True)
        for i, event in enumerate(events):
            if event == "\n":
                event = "<Return>"
            if type(event) is str and event.startswith("<") and event.endswith(">"):
                self.generate(event)
            elif type(event) is str:
                self.word(event)
            elif type(event) is int:
                root.after(event, lambda: self.play(events[i+1:]))
                return
            else:
                self.generate(event)
            root.after(100, lambda: self.play(events[i+1:]))
            return


    def word(self, word: str):
        for char in word:
            self.generate(f"{char}")
            # self.generate(f"<Key-{char}>")
        # self.generate("<space>")


if __name__ == "__main__":

    root = tk.Tk()
    f = tk.Frame(root)
    f.pack(fill="both", expand=True)

    t = tk.Text(f, undo=True)
    # print(t.event_info())
    t.pack(fill="both", expand=True)
    t.focus_set()

    EventPlayer(t)
    def on_first_configure(e):
        t.event_generate("<Control-Alt-Shift-P>")
        t.unbind("<Configure>")

    t.bind("<Configure>", on_first_configure)

    root.mainloop()
