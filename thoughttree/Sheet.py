import tkinter as tk
from tkinter import CURRENT, END, INSERT, SEL, WORD, X, SEL_FIRST, SEL_LAST
from tkinter import scrolledtext
from tkinter.font import Font
from typing import Union

from Cursorline import Cursorline
from FinishReasonIcon import FinishReasonIcon
from Notebook import Notebook
from ThoughttreeConfig import conf


class Sheet(tk.scrolledtext.ScrolledText):
    FONT_NAME_MONOSPACE = "monospace"
    FONT_NAME_PROPORTIONAL = "sans-serif"
    FONT = (FONT_NAME_PROPORTIONAL, 11)

    def __init__(self, master=None, text="", scrollbar=True, padx=0, pady=0, height=0, **kw):
        height = height or len(text.splitlines())
        background = 'white'
        # background = next_pastel_rainbow_color()
        tk.scrolledtext.ScrolledText.__init__(
            self, master, undo=True, wrap=WORD, padx=padx, pady=pady, background=background,
            width=80, height=height, insertwidth=4, font=Sheet.FONT,
            border=0, borderwidth=0, highlightthickness=0,
            selectbackground="#66a2d4", selectforeground="white", **kw)


        def jump_to_limit(e: tk.Event):
            top, bottom = self.vbar.get()
            if e.keysym == 'Prior' and top == 0.0:
                limit = "1.0"
            elif e.keysym == 'Next' and bottom == 1.0:
                limit = tk.END
            else:
                return

            self.mark_set(tk.INSERT, limit)
            self.see(tk.INSERT)


        if scrollbar:
            self.vbar.config(width=18, takefocus=False, borderwidth=2)
        else:
            self.vbar.pack_forget()

        self.scroll_output = conf.scroll_output


        self.bind('<Prior>', jump_to_limit)
        self.bind('<Next>', jump_to_limit)
        self.pack(pady=0, fill=X, expand=True)

        name, size = self.cget("font").rsplit(None, 1)
        self.tag_configure('bold', font=(name, int(size), "bold"))
        self.tag_configure('strikethrough', overstrike=True)
        self.tag_configure("assistant", background="#F0F0F0", selectbackground="#4682b4", selectforeground="white")


        Cursorline(self)
        self.insert(END, text)


    def undo_separator(self):
        self.edit_separator()

    def bold(self):
        self.toggle_tag('bold')


    def strikethrough(self):
        self.tag_selection('strikethrough')


    def tag_selection(self, tag):
        if self.tag_nextrange(tag, SEL_FIRST, SEL_LAST) or self.tag_prevrange(tag, SEL_FIRST, SEL_LAST):
            self.tag_remove(tag, SEL_FIRST, SEL_LAST)
        else:
            self.tag_add(tag, SEL_FIRST, SEL_LAST)


    def toggle_tag(self, tag):
        selected = self.tag_ranges("sel")
        if selected:
            tagged = self.tag_nextrange(tag, SEL_FIRST, SEL_LAST)
            if tagged:
                self.tag_remove(tag, *tagged)
            else:
                self.tag_add(tag, SEL_FIRST, SEL_LAST)


    def transfer_content(self, to_sheet):
        content = self.get("1.0", tk.END)
        to_sheet.insert("1.0", content)

        # self.compare('2.0', '<=', END)

        for tag in self.tag_names():
            ranges = self.tag_ranges(tag)
            for i in range(0, len(ranges), 2):
                to_sheet.tag_add(tag, ranges[i], ranges[i + 1])
                to_sheet.tag_config(tag, **{k: v[4] for k, v in self.tag_configure(tag).items() if v[4]})

        for name in self.window_names():
            index = self.index(name)
            window = self.nametowidget(name)
            to_sheet.window_create(index, window=window)


    def fork(self, index=INSERT, root=False):
        index = self.index(index)

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


        def new_sibling(sibling_notebook):
            last_tab_label = sibling_notebook.tab(len(sibling_notebook.tabs()) - 1, "text")
            return next_equal(last_tab_label)

        def new_child(parent):
            if parent:
                parent_tab_label = parent.tab(parent.select(), "text")
            else:
                parent_tab_label = ""
            return next_level(parent_tab_label)


        has_leading_text = bool(self.get("1.0", index).strip())
        trailing_text = self.get(index, END)
        trailing_text = trailing_text.rstrip()
        parent = self.find_parent(Notebook)

        new_notebook = not parent or has_leading_text
        if new_notebook:
            notebook = Notebook(self, height=self.winfo_height(), width=self.winfo_width())

            sheet = Sheet(notebook, trailing_text, scrollbar=True)
            notebook.add(sheet, text=new_child(parent))
            self.window_create(index, window=notebook)
            self.delete(index + "+1char", END)
        else:
            notebook = parent
        sheet = Sheet(notebook, scrollbar=True)
        notebook.add(sheet, text=new_sibling(notebook))

        notebook.select(len(notebook.tabs()) - 1)
        sheet.focus_set()

        return "break"


    def find_parent(self, parentType: type) -> Union["Sheet", Notebook]:
        parent = self.master
        while parent and type(parent) != parentType:
            parent = parent.master
        return parent


    def history_from_path(self, history=None) :

        parentText: Sheet = self.find_parent(Sheet)
        if parentText:
            history = parentText.history_from_path(history)
        else:
            history = history or []
        content = self.dump(1.0, END, text=True, tag=True, window=True)
        section = ""
        role = "user"
        for item in content :
            text = item[1]
            designation = item[0]
            if designation == "tagon" and text == "assistant":
                # section = section.strip()
                history += [{'role' : role, 'content' : section}]
                role = "assistant"
                section = ""
            elif designation == "tagoff" and text == "assistant":
                # section = section.strip()
                history += [{'role' : role, 'content' : section}]
                role = "user"
                section = ""
            elif designation in ["tagon", "tagoff"] and text in ["cursorline", "sel"]:
                pass
            elif designation == "text":
                section += text
            elif designation == "window":
                pass
            else:
                print(f"Ignored item: {item}")
        section = section.strip("\n")
        if section != "" :
            history += [{'role' : role, 'content' : section}]
        return history


    def jump_to_similar_line(self, event=None, direction=1):

        def find_similar_line(target, line_nr_1, lines, direction):
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


        sheet: Sheet = self.focus_get()
        print(f"{sheet == self}")
        cursor_pos = sheet.index(INSERT)
        line_nr = int(cursor_pos.split('.')[0])
        current_line = sheet.get(f"{line_nr}.0", f"{line_nr}.end")
        if not current_line.strip():
            return
        lines = sheet.get(1.0, END).splitlines()
        jump_line = find_similar_line(current_line, line_nr, lines, direction)
        if jump_line:
            jump_index = f"{jump_line}.{0}"
            sheet.mark_set(INSERT, jump_index)
            sheet.see(jump_index)



    def close_tab(self):

        def selected_sheet(notebook):
            frame_on_tab = notebook.nametowidget(notebook.select())
            sheet = frame_on_tab.winfo_children()[1]
            print(f"{sheet == self}")
            return sheet

        notebook: Notebook = self.find_parent(Notebook)
        if notebook:
            selected = notebook.index(CURRENT)
            notebook.forget(selected)
            if len(notebook.tabs()) > 1:
                notebook.select(max(selected - 1, 0))
                selected_sheet(notebook).focus_set()
            elif len(notebook.tabs()) == 1:
                string = selected_sheet(notebook).get('1.0', END)
                parent = self.find_parent(Sheet)
                parent.delete("end-2 char", "end-1 char") # delete notebook window
                parent.insert(END, string)
                parent.mark_set(INSERT, "end-1 char")
                parent.focus_set()
            return "break"


    def close_empty_tab_or_backspace(self):
        if self.index(INSERT) == "1.0" and not self.tag_ranges(SEL):
            notebook: Notebook = self.find_parent(Notebook)
            if notebook:
                string_in_tab = self.get('1.0', END).strip()
                if not string_in_tab:
                    self.close_tab()
            return "break"
        else:
            self.delete(INSERT + "-1c")


    def delete(self, index1=INSERT, index2=None):

        def is_icon(element):
            designation, value, index = element
            return designation == "window" and isinstance(self.nametowidget(value), FinishReasonIcon)

        if self.tag_ranges(SEL):
            self.event_generate("<<Clear>>")
        else:
            if index2:
                super().delete(index1, index2)
            else:
                dump = self.dump(index1, all=True)
                if any([element[0] == "text" or is_icon(element) for element in dump]):
                    super().delete(index1)

