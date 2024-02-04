import tkinter as tk
from tkinter import ttk, BOTH, LEFT, RIGHT, VERTICAL, NW, Y, X, INSERT, CURRENT, TOP

import tools


class EventRecorder:
    def __init__(self, w: tk.Widget):
        self.widget = w
        self.events = []

        def on_key(event):
            print(f"{event}")
            self.events.append(event)
        self.widget.bind_all("<Key>", self.record, add=True)


    def record(self, event):
        if event.type == tk.EventType.KeyPress:
            print(f"record: <KeyPress-{event.keysym}>", flush=True)
        else:
            print(f"record: {event}", flush=True)

