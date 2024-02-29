import re
import tkinter as tk

import tools


class EventPlayer:
    def __init__(self, widget: tk.Widget, events=None, file=None):
        self.widget = widget

        # events = "\n".join([chr(i) for i in range(50, 70)])
        # events = [chr(i) for i in range(65, 85)]
        # events = [4, 5, 6, 7]
        # events = lines(15)
        # events = (["<X>", "<Right>", "<Y>",])
        # events = (["a", "b", "c", "\n", "a", "<b>", "c", "\n", "foo", "bar", 500, "a", "bbbb", ])
                  # + ["<<Undo>>"] * 5 + ["<<Redo>>"] * 5)
        events = events or []
        if file:
            self.widget.after_idle(lambda: self.play_file(file))
        else:
            self.widget.after_idle(lambda: self.play(events))

        # self.widget.bind("<Escape>", lambda e: self.widget.winfo_toplevel().destroy())
        self.widget.bind("<F12>", lambda e: self.play(events))
        # self.widget.bind("<Alt-a>", lambda e: w.event_generate("<a>"))
        # self.widget.bind("<Alt-b>", lambda e: w.event_generate("<b>"))
        # self.widget.bind("<Control-Alt-Shift-P>", lambda e: self.play(events))

        def on_key_press(event):
            print(f"{event=} on {event.widget}")
        if not widget.winfo_toplevel().bind("<Key>"):
            widget.winfo_toplevel().bind("<Key>", on_key_press, add=True)
            widget.winfo_toplevel().bind("<Control-Key>", on_key_press, add=True)
            widget.winfo_toplevel().bind("<Shift-Key>", on_key_press, add=True)
        # widget.winfo_toplevel().bind("<Key>", on_key_press, add=True)

    def generate(self, event):
        w = self.widget
        # print(f"-{w.index(INSERT)} {event=}")


        Shift = 1
        Control = 4
        Alt = 8
        modifiers = {"Shift": Shift, "Control": Control, "Alt": Alt}

        state = 0
        if len(event) == 1 and event.isupper() or event in "°!\"§$%&/()=?`*';:_>":
            state |= Shift
        for name, code in modifiers.items():
            if event.find(name) >= 0:
                state |= code

        w.event_generate(event, state=state, x=0, y=0)
        w.update()
        w.update_idletasks()
        # print(f"+{w.index(INSERT)} {event=}")


    def play(self, events):
        # print(f"play: {start} {events=}", flush=True)
        for i, event in enumerate(events):
            if event == "\n":
                event = "<Return>"
            if isinstance(event, str) and event.startswith("<") and event.endswith(">"):
                self.generate(event)
            elif isinstance(event, str):
                self.word(event)
            elif type(event) is int:
                self.widget.after(event, lambda: self.play(events[i+1:]))
            else:
                self.generate(event)

    def play_file(self, events_file):
        with open(events_file) as f:
            event_text = f.read()
        keystrokes_newlines_chars_pattern = "<[A-Z][^<\s]+>|\\n|."
        events = re.findall(keystrokes_newlines_chars_pattern, event_text)
        self.play(events)


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
    # t.bind("<Configure>", on_first_configure)
    tools.escapable(root)
    root.mainloop()
