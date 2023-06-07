import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from tkinter import scrolledtext
from tkinter.ttk import Notebook




class Text(tk.scrolledtext.ScrolledText):
    FONT = ("monospace", 10)
    # FONT = ("sans-serif", 11)

    def __init__(self, master=None, text="", scrollbar=True, **kw):
        height = len(text.splitlines())
        background = 'white'
        tk.scrolledtext.ScrolledText.__init__(
            self, master, undo=True, wrap=tk.WORD, padx=0, pady=0, background=background,
            width=80, height=height, insertwidth=4, font=Text.FONT,
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
        self.bind_class("last", '<KeyRelease>', lambda e: self.highlightCurrentLine(e))
        self.bind_class("last", '<Button-1>', lambda e: self.highlightCurrentLine(e))
        self.bind_class("last", "<FocusIn>", lambda e: self.highlightCurrentLine(e))
        self.bind_class("last", "<FocusOut>", lambda e: self.highlightCurrentLine(e, False))
        self.pack(pady=0, fill=tk.X, expand=True)
        self.tag_configure("assistant", background="#F0F0F0", selectbackground="#4682b4", selectforeground="white")
        self.tag_configure('currentLine', background='#FCFAED', foreground="black", selectbackground="#4682b4", selectforeground="white")
        self.insert(tk.END, text)

    def highlightCurrentLine(self, e, add=True):
        if not e.widget.winfo_exists():
            return
        e.widget.tag_remove('currentLine', 1.0, "end")
        if add:
            e.widget.tag_add('currentLine', 'insert display linestart', 'insert display lineend+1c')


    def change_notebook_height(self, delta):
        parent = self.master.focus_get()
        while parent and type(parent) not in [Notebook]:
            parent = parent.master
        if not parent:
            return
        old_height = parent.cget("height")
        height = max(old_height + delta * self.line_height, self.line_height)
        parent.configure(height=height)

    def split_conversation(self):

        def next_equal(hierarchical_id):
            if hierarchical_id:
                levels = hierarchical_id.split('.')
            else:
                levels = ['0']
            # print(f"{levels}")
            levels = levels[:-1] + [str(int(levels[-1]) + 1)]
            return '.'.join(levels)


        def next_level(hierarchical_id):
            if hierarchical_id:
                levels = hierarchical_id.split('.') + ['1']
            else:
                levels = ['1']
            return '.'.join(levels)

        def find_parent_tab_label(child: tk.Widget):
            parent = child
            while parent and type(parent) != Notebook:
                parent = parent.master
            if parent:
                parent: Notebook = parent
                parent_tab_id = parent.select()
                parent_tab_label = parent.tab(parent_tab_id, "text")
                return parent, parent_tab_id, parent_tab_label
            else:
                return None, None, ""

        leading_text = self.get("1.0", tk.INSERT)
        trailing_text = self.get(tk.INSERT, tk.END)
        height, width = self.calc_notebook_size()
        style = ttk.Style()
        style.layout("NoBorder.TNotebook", [])
        parent, parent_tab_id, parent_tab_label = find_parent_tab_label(self)
        new_notebook_needed = not parent or bool(leading_text.strip())
        if new_notebook_needed:
            notebook = Notebook(self, height=height, width=width, style='NoBorder.TNotebook')
            tab_label = next_level(parent_tab_label)
            notebook.add_textbox(tab_label, trailing_text)
        else:
            notebook = parent
        new_txt = Text(notebook, scrollbar=False)
        last_tab_label = notebook.tab(len(notebook.tabs()) - 1, "text")
        notebook.add(new_txt, text=next_equal(last_tab_label))

        notebook.select(len(notebook.tabs()) - 1)
        new_txt.focus_set()
        if new_notebook_needed:
            self.window_create(tk.INSERT, window=notebook)
            self.see(tk.INSERT)
        self.delete(tk.INSERT, tk.END)
        return "break"

    def add_notebook_to_textbox(self, widget, pos):
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
