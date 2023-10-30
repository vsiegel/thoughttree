import tkinter as tk
import os
from pathlib import Path
from tkinter import messagebox

class SyncedFile(tk.Text):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def insert_file(self, index, file_path):
        if not os.path.isfile(file_path):
            messagebox.showerror("Error", "File does not exist")
            return

        file_name = os.path.basename(file_path)
        self.insert(index, file_name)
        self.mark_set("file_start", index)
        self.mark_set("file_end", "{}+{}c".format(index, len(file_name)))
        self.tag_add("file", "file_start", "file_end")
        self.tag_config("file", elide=True)
        self.tag_bind("file", "<Double-1>", lambda e: self.open_file(file_path))

    def open_file(self, file_path):
        with open(file_path, "r") as f:
            content = f.read()

        self.tag_config("file", elide=False)
        self.insert("file_end", "\n" + content)
        self.tag_config("file", elide=True)

root = tk.Tk()
text = SyncedFile(root, width=40, height=10)
text.pack()
text.insert_file("1.0", Path.home() /"ttt/example.txt")
root.mainloop()
