import tkinter as tk
from tkinter import ACTIVE, LEFT, BOTH, scrolledtext, INSERT, SEL, END, ttk
from tkinter.simpledialog import Dialog
from tkinter.scrolledtext import ScrolledText


class ListDialog(tk.simpledialog.Dialog):
    def __init__(self, items, title=None, parent=None):
        self.items = items
        super().__init__(parent, title)

    def grab_set(self):
        pass

    def wait_window(self, window = None):
        pass

    def body(self, parent):

        frame = tk.Frame(self)
        frame.pack(expand=True, fill='both')

        tree = ttk.Treeview(frame, columns=('Event', 'Key'), show='', height=30)
        tree.column("Event", width=300)
        tree.column("Key", width=200)
        # tree.heading('Event', text='Event')
        # tree.heading('Key', text='Key')
        tree.column('Event', anchor='e')  # right justify the first column

        # tree.bind("<FousOut>")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)

        for key, values in self.items.items():
            tree.insert('', 'end', values=values)

        tree.pack(expand=True, fill='both')
        tree.focus(tree.get_children()[0])
        return frame

    def buttonbox(self):
        box = tk.Frame(self)

        button = tk.Button(box, text="Close", width=10, command=self.ok, default=ACTIVE)
        button.pack(side=LEFT, padx=20, pady=20)

        self.pack_slaves()[0].pack(fill=BOTH, expand=True, padx=25, pady=25) # hack to repack dialog content to expand

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    def on_out(event):
        print(event.widget)
    root.bind("<FocusOut>", on_out)
    def on_in(event):
        print(event.widget)
    root.bind("<FocusIn>", on_in)

    root.attributes("-topmost", True)
    items = {
        "a": (1,2),
        "b": (3,4),
        "c": (5,6),
    }
    ListDialog(items, title="Test List")
