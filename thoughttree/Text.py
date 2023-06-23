import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter.ttk import Notebook

from typing import Union

class Text(tk.scrolledtext.ScrolledText):
    FONT_NAME_MONOSPACE = "monospace"
    FONT_NAME_PROPORTIONAL = "sans-serif"
    FONT = (FONT_NAME_PROPORTIONAL, 11)

    def __init__(self, master=None, text="", scrollbar=True, **kw):
        height = len(text.splitlines())
        background = 'white'
        # background = next_pastel_rainbow_color()
        tk.scrolledtext.ScrolledText.__init__(
            self, master, undo=True, wrap=tk.WORD, padx=0, pady=0, background=background,
            width=80, height=height, insertwidth=4, font=Text.FONT,
            border=0, borderwidth=0, highlightthickness=0,
            selectbackground="#66a2d4", selectforeground="white", **kw)

        if scrollbar:
            self.vbar.config(width=18, takefocus=False, borderwidth=2)
        else:
            self.vbar.pack_forget()

        ttk.Style().layout("NoBorder.TNotebook", [])

        # self.bind("<Control-Alt-plus>", lambda e: self.change_notebook_height(1))
        # self.bind("<Control-Alt-minus>", lambda e: self.change_notebook_height(-1))
        self.bind("<Control-Shift-asterisk>", lambda e: self.change_text_height(1))
        self.bind("<Control-Shift-underscore>", lambda e: self.change_text_height(-1))
        self.bindtags(self.bindtags() + ("last",))
        self.bind_class("last", '<KeyRelease>', lambda e: self.cursorline(e))
        self.bind_class("last", '<Button-1>', lambda e: self.cursorline(e))
        self.bind_class("last", "<FocusIn>", lambda e: self.cursorline(e))
        self.bind_class("last", "<FocusOut>", lambda e: self.cursorline(e, False))
        self.pack(pady=0, fill=tk.X, expand=True)
        self.tag_configure("assistant", background="#F0F0F0", selectbackground="#4682b4", selectforeground="white")
        self.tag_configure('cursorline', background='#FCFAED', foreground="black", selectbackground="#4682b4", selectforeground="white")
        self.insert(tk.END, text)

        # def update_text_height(event=None):
        #     text_height = self.count('1.0', 'end', 'displaylines')[0]
        #     print(text_height)
        #     self.configure(height=text_height)
        #
        # self.bind('<KeyRelease>', update_text_height)


    def cursorline(self, e, add=True):
        if not e.widget.winfo_exists():
            return
        e.widget.tag_remove('cursorline', 1.0, "end")
        if add:
            e.widget.tag_add('cursorline', 'insert display linestart', 'insert display lineend+1c')

    # def change_notebook_height(self, delta):
    #     parent = self.master.focus_get()
    #     while parent and type(parent) not in [Notebook]:
    #         parent = parent.master
    #     if not parent:
    #         return
    #     old_height = parent.cget("height")
    #     self.line_height = tkfont.Font(font=Text.FONT).metrics("linespace")
    #     height = max(old_height + delta * self.line_height, self.line_height)
    #     parent.configure(height=height)

    def change_text_height(self, delta):
        parent = self.master.focus_get()
        while parent and type(parent) != Text:
            parent = parent.master
        if not parent:
            return
        old_height = parent.cget("height")
        # self.line_height = tkfont.Font(font=Text.FONT).metrics("linespace")
        # height = max(old_height + delta * self.line_height, self.line_height)
        parent.configure(height=old_height + delta)


    def fork(self):

        def next_level(hierarchical_id):
            if hierarchical_id:
                hierarchical_id = hierarchical_id.split(' ', 1)[0]
                levels = hierarchical_id.split('.') + ['1']
            else:
                levels = ['1']
            return '.'.join(levels)


        def next_equal(hierarchical_id):
            if hierarchical_id:
                hierarchical_id = hierarchical_id.split(' ', 1)[0]
                levels = hierarchical_id.split('.')
            else:
                levels = ['0']
            levels = levels[:-1] + [str(int(levels[-1]) + 1)]
            return '.'.join(levels)


        def new_sibling(notebook):
            last_tab_label = notebook.tab(len(notebook.tabs()) - 1, "text")
            s = next_equal(last_tab_label)
            return s

        def new_child(parent):
            if parent:
                parent_tab_label = parent.tab(parent.select(), "text")
            else:
                parent_tab_label = ""
            return next_level(parent_tab_label)


        # Get the leading and trailing text and find the parent Notebook
        has_leading_text = bool(self.get("1.0", tk.INSERT).strip())
        trailing_text = self.get(tk.INSERT, tk.END)
        trailing_text = trailing_text.rstrip()
        parent = self.find_parent(Notebook)

        new_notebook = not parent or has_leading_text
        if new_notebook:
            notebook = Notebook(self, height=self.winfo_height(), width=self.winfo_width(), style='NoBorder.TNotebook')
            notebook.enable_traversal()

            text = Text(notebook, trailing_text, scrollbar=True)
            notebook.add(text, text=new_child(parent))
            self.window_create(tk.INSERT, window=notebook)
            self.delete(tk.INSERT, tk.END)
        else:
            notebook = parent
        text = Text(notebook, scrollbar=True)
        notebook.add(text, text=new_sibling(notebook))

        notebook.select(len(notebook.tabs()) - 1)
        text.focus_set()

        return "break"


    def find_parent(self, parentType: type) -> Union["Text", Notebook]:
        parent = self.master
        while parent and type(parent) != parentType:
            parent = parent.master
        return parent


    def history_from_path(self, history=None) :

        parentText: Text = self.find_parent(Text)
        if parentText:
            history = parentText.history_from_path(history)
        else:
            history = history or []
        content = self.dump(1.0, tk.INSERT, text=True, tag=True, window=True)
        section = ""
        role = "user"
        for item in content :
            text = item[1]
            category = item[0]
            if category == "tagon" and text == "assistant":
                section = section.strip()
                history += [{'role' : role, 'content' : section}]
                role = "assistant"
                section = ""
            elif category == "tagoff" and text == "assistant":
                section = section.strip()
                history += [{'role' : role, 'content' : section}]
                role = "user"
                section = ""
            elif category in ["tagon", "tagoff"] and text in ["cursorline", "sel"]:
                pass
            elif category == "text":
                section += text
            elif category == "window":
                pass
                # print(f"{item=}")
                # win_index = item[2]
                # print(f"{self.window_cget(win_index, 'text')=}")
            else:
                print(f"Ignored item: {item}")
        section = section.strip("\n")
        if section != "" :
            history += [{'role' : role, 'content' : section}]
        return history


    def jump_to_similar_line(cls, event=None, direction=1):

        def find_matching_line(target, line_nr_1, lines, direction):
            line_nr_0 = line_nr_1 - 1
            num_lines = len(lines)
            if num_lines == 0:
                return 0
            target = target.strip()
            start = (line_nr_0 + direction) % num_lines
            if direction == 1:
                numbered_lines = list(enumerate(lines[start:] + lines[:start]))
            else:
                numbered_lines = list(enumerate(lines[:start][::-1] + lines[start:][::-1]))
            for i, line in numbered_lines:
                if line.strip() == target:
                    if direction == 1:
                        return ((i + start) % num_lines) + 1
                    else:
                        return ((start - i + num_lines - 1) % num_lines) + 1
            return 0


        text: Text = cls.focus_get()
        cursor_pos = text.index(tk.INSERT)
        line_nr = int(cursor_pos.split('.')[0])
        current_line = text.get(f"{line_nr}.0", f"{line_nr}.end")
        if not current_line.strip():
            return
        lines = text.get(1.0, tk.END).splitlines()
        jump_line = find_matching_line(current_line, line_nr, lines, direction)
        if jump_line:
            jump_index = f"{jump_line}.{0}"
            text.mark_set(tk.INSERT, jump_index)
            text.see(jump_index)



    def close_tab(self):

        def selected_text(notebook):
            frame_on_tab = notebook.nametowidget(notebook.select())
            return frame_on_tab.winfo_children()[1]

        notebook: Notebook = self.find_parent(Notebook)
        if notebook:
            selected = notebook.select()
            notebook.forget(selected)
            if len(notebook.tabs()) > 1:
                notebook.select(max(selected - 1, 0))
                selected_text(notebook).focus_set()
            elif len(notebook.tabs()) == 1:
                string = selected_text(notebook).get('1.0', tk.END)
                parent = self.find_parent(Text)
                index = parent.index("end-2 char")
                parent.delete("end-2 char")
                parent.insert(tk.END, string)
                parent.mark_set(tk.INSERT, index)
                parent.focus_set()
            return "break"


    def close_empty_tab_or_backspace(self):
        notebook: Notebook = self.find_parent(Notebook)
        if notebook:
            insert_index = self.index(tk.INSERT)
            if insert_index == "1.0":
                string_in_tab = self.get('1.0', tk.END).strip()
                if not string_in_tab:
                    self.close_tab()
                    return "break"

        if self.tag_ranges("sel"):
            self.event_generate("<<Clear>>")
        else:
            self.delete(tk.INSERT + " - 1 char", tk.INSERT)
