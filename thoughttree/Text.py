import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from tkinter import scrolledtext


class Notebook(ttk.Notebook):
    def __init__(self, master=None, **kw):
        ttk.Notebook.__init__(self, master, padding=(0, 4, 0, 0), **kw)

    def find_parent_tab_label(self, txt):
        parent = txt
        while parent and type(parent) not in [Notebook]:
            parent = parent.master
        if parent:
            parent: Notebook = parent
            tab_id = parent.select()
            old_tab_label = parent.tab(tab_id, "text")
        else:
            old_tab_label = ""
        return old_tab_label

    def add_textbox_to_notebook(self, old_tab_label, i, text=""):
        if old_tab_label:
            tab_label = f"{old_tab_label}.{i}"
        else:
            tab_label = f"{i}"
        txt = Text(self, text, scrollbar=False)
        self.add(txt, text=tab_label)
        return txt


class Text(tk.scrolledtext.ScrolledText):
    FONT = ("monospace", 10)
    # FONT = ("sans-serif", 11)

    def __init__(self, master=None, text="", scrollbar=True, **kw):
        height = len(text.splitlines())
        tk.scrolledtext.ScrolledText.__init__(
            self, master, undo=True, wrap=tk.WORD, padx=1, pady=1,
            width=80, height = height, insertwidth=4, font=Text.FONT,
            border=0, borderwidth=0, highlightthickness=0,
            selectbackground="#66a2d4", selectforeground="white", **kw)

        self.line_height = tkfont.Font(font=Text.FONT).metrics("linespace")
        if scrollbar:
            self.vbar.config(width=18, takefocus=False, borderwidth=2)
        else:
            self.vbar.pack_forget()

        self.bind("<Control-Alt-plus>", lambda e: self.change_notebook_height(1))
        self.bind("<Control-Alt-minus>", lambda e: self.change_notebook_height(-1))
        self.bind("<Control-Shift-asterisk>", lambda e: self.change_notebook_height(10))
        self.bind("<Control-Shift-underscore>", lambda e: self.change_notebook_height(-10))
        self.bindtags(self.bindtags() + ("last",))
        self.bind_class("last", '<KeyRelease>', lambda _: self.highlightCurrentLine())
        self.bind_class("last", '<Button-1>', lambda _: self.highlightCurrentLine())
        self.bind_class("last", "<FocusIn>", lambda _: self.highlightCurrentLine())
        self.bind_class("last", "<FocusOut>", lambda _: self.highlightCurrentLine(False))
        self.pack(pady=0, fill=tk.X, expand=True)
        self.tag_configure("assistant", background="#F0F0F0", selectbackground="#4682b4", selectforeground="white")
        self.tag_configure('currentLine', background='#FCFAED', foreground="black", selectbackground="#4682b4", selectforeground="white")
        self.insert(tk.END, text)

    def highlightCurrentLine(self, add=True):
        if not self.winfo_exists():
            return
        self.tag_remove('currentLine', 1.0, "end")
        if add:
            self.tag_add('currentLine', 'insert display linestart', 'insert display lineend+1c')


    def change_notebook_height(self, delta):
        parent = self.master.focus_get()
        while parent and type(parent) not in [Notebook]:
            parent = parent.master
        if not parent:
            return
        old_height = parent.cget("height")
        height = max(old_height + delta * self.line_height, self.line_height)
        parent.configure(height=height)

    def branch_conversation(self):
        height, width = self.calc_notebook_size()
        notebook = Notebook(self, height=height, width=width)
        old_tab_label = Notebook.find_parent_tab_label(notebook, self)
        notebook.add_textbox_to_notebook(old_tab_label, 1, "Text that was replaced by this widget")
        notebook.add_textbox_to_notebook(old_tab_label, 2, "")
        self.add_notebook_to_textbox(notebook)

    def add_notebook_to_textbox(self, widget, pos="insert"):
        self.insert(pos, '\n')
        self.window_create(pos, window=widget)
        self.see(pos)

    def calc_notebook_size(self):
        twidth = self.winfo_width()
        width = (twidth - 0)
        char_width = tkfont.Font(font=self.cget("font")).measure('0')
        width -= width % char_width
        height = int(self.winfo_height() * 2 / 3)
        return height, width

    def chat_history_from_textboxes(self, history=None) :
        def print_window_objects():
            window_objects = self.window_names()
            for window_object in window_objects:
                print(type(window_object))
                print(window_object)

        # print_window_objects()
        history = history or []
        content = self.dump(1.0, tk.END, text=True, tag=True, window=True)
        section = ""
        for item in content :
            if item[0] == "tagon" and item[1] == "assistant":
                section = section.strip()
                history += [{'role' : 'user', 'content' : section}]
                section = ""
            elif item[0] == "tagoff" and item[1] == "assistant":
                section = section.strip()
                history += [{'role' : 'assistant', 'content' : section}]
                section = ""
            elif item[0] in ["tagon", "tagoff"] and item[1] in ["currentLine"]:
                pass
            elif item[0] == "text":
                section += item[1]
            elif item[0] == "window":
                pass
                # print(f"{item=}")
                # win_index = item[2]
                # print(f"{self.window_cget(win_index, 'text')=}")
            else:
                print(f"Ignored item: {item}")
        section = section.strip("\n")
        if section != "" :
            if history[-1]['role'] == "user" :
                history += [{'role' : 'assistant', 'content' : section}]
            elif history[-1]['role'] in ["assistant", "system"] :
                history += [{'role' : 'user', 'content' : section}]
        return history
