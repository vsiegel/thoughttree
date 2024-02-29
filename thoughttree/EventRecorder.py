import tkinter as tk
from tkinter import ttk, BOTH, LEFT, RIGHT, VERTICAL, NW, Y, X, INSERT, CURRENT, TOP


import tools


class EventRecorder:
    def __init__(self, w: tk.Widget):
        self.widget = w
        self.events = []

        def on_key(event):
            print(f"{event=}")
            self.events.append(event)

        # toplevel = self.widget.winfo_toplevel()
        # bindtags = list(toplevel.bindtags())
        # bindtags.insert(0, "EventRecorder")
        # toplevel.bindtags(bindtags)
        # toplevel.bind_class("EventRecorder", "<Key>", self.record, add=True)
        self.widget.bind("<Key>", self.record, add=True)


    def record(self, event: tk.EventType.KeyPress):
        if event.type == tk.EventType.KeyPress:
            print(f"record: {event.state} {event.keysym} {event.keycode}   {event}", flush=True)
        else:
            print(f"record: {event}", flush=True)


if __name__ == "__main__":

    root = tk.Tk()
    f = tk.Frame(root)
    f.pack(fill="both", expand=True)
    t = tk.Text(f, undo=True)
    t.pack(fill="both", expand=True)
    t.focus_set()

    top = tk.Toplevel(root)
    t = tk.Text(top, undo=True)
    t.pack(fill="both", expand=True)

    # print(t.event_info())

    EventRecorder(t)
    def on_first_configure(e):
        t.event_generate("<Control-Alt-Shift-P>")
        t.unbind("<Configure>")
    # t.bind("<Configure>", on_first_configure)
    tools.escapable(root)
    root.mainloop()
