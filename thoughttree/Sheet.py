import re
import tkinter as tk
from tkinter import CURRENT, END, INSERT, SEL, WORD, X, SEL_FIRST, SEL_LAST, RIGHT, Y, BOTH, LEFT
from tkinter.scrolledtext import ScrolledText
from tkinter.simpledialog import askstring
from typing import Union

from Cursorline import Cursorline
from FinishReasonIcon import FinishReasonIcon
from Fonts import Fonts
from Notebook import Notebook
from ThoughttreeConfig import conf


class Sheet(ScrolledText):

    def __init__(self, master=None, scrollbar=True, autohide=False, padx=0, pady=0, height=0, grow=True, background='white', **kw):
        ScrolledText.__init__(
            self, master, undo=True, wrap=WORD, padx=padx, pady=pady, background=background,
            width=80, height=height, insertwidth=4, font=Fonts.FONT,
            border=0, borderwidth=0, highlightthickness=0,
            selectbackground="#66a2d4", selectforeground="white", **kw)

        # if autohide:
        #     self.vbar = AutoScrollbar(self.frame)
        # else:
        #     self.vbar = tk.Scrollbar(self.frame)
        # self.vbar.pack(side=RIGHT, fill=Y)
        #
        # self.config(yscrollcommand=self.vbar.set)
        # self.vbar.configure(command=self.yview)

        if scrollbar:
            self.vbar.config(width=18, takefocus=False, borderwidth=2)
        else:
            self.vbar.pack_forget()

        self.scroll_output = conf.scroll_output
        self.file = None

        self.bind('<Prior>', self.jump_to_limit)
        self.bind('<Next>', self.jump_to_limit)
        self.pack(padx=0, pady=0, fill=X, expand=True)

        name, size = self.cget("font").rsplit(None, 1)
        self.tag_config('bold', font=(name, int(size), "bold"))
        self.tag_config('strikethrough', overstrike=True)
        self.tag_config('found_one', background="#345754")
        self.tag_config('found_all', background="#575400")
        self.tag_config('highlight', background="red")
        self.tag_config('semi_highlight', background="#FFCCCB")
        self.tag_config('hidden_markup', elide=True, foreground="light blue")
        self.tag_config("assistant", background="#F0F0F0", selectbackground="#4682b4", selectforeground="white")
        self.tag_config('hidden_prompt', elide=True, foreground="light blue")

        self.old_num_display_lines = 0

    def exec_code_block(self, event=None):
        print(f"exec_code_block")

        code_block_pattern = """('{3}|"{3}|```)python.*\n([\s\S]*?)\\1"""
        code_block_start_pattern =  '("""|' + """'''|```)python.*\n"""
        start = self.search(code_block_start_pattern, INSERT, regexp=True, backwards=True)
        if start:
            print(f"{start=}")
            text = self.get(start, END)
            m = re.search(code_block_pattern, text)
            print(f"{m=}")
            print(f"'{text=}'")
            if m:
                code = m.group(2)
                print(f'Running "{code[:30]=}"')
                print(exec(code))

        Cursorline(self)


    def fork(self, index=INSERT):
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

            sheet = Sheet(notebook, scrollbar=True)
            sheet.insert(END, trailing_text)
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

    def transfer_content(self, to_sheet):
        content = self.get("1.0", tk.END)
        to_sheet.insert("1.0", content)

        for tag in self.tag_names():
            ranges = self.tag_ranges(tag)
            for i in range(0, len(ranges), 2):
                to_sheet.tag_add(tag, ranges[i], ranges[i + 1])
                to_sheet.tag_config(tag, **{k: v[4] for k, v in self.tag_configure(tag).items() if v[4]})

        for name in self.window_names():
            index = self.index(name)
            window = self.nametowidget(name)
            to_sheet.window_create(index, window=window)


    def close_tab(self):

        def selected_sheet(notebook):
            frame_on_tab = notebook.nametowidget(notebook.select())
            sheet = frame_on_tab.winfo_children()[1]
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

    def jump_to_limit(self, e: tk.Event):
        top, bottom = self.vbar.get()
        if e.keysym == 'Prior' and top == 0.0:
            limit = "1.0"
        elif e.keysym == 'Next' and bottom == 1.0:
            limit = tk.END
        else:
            return

        self.mark_set(tk.INSERT, limit)
        self.see(tk.INSERT)

    def grow_to_displaylines(self, event):
        sheet = event.widget
        num_display_lines = sheet.count("1.0", "end", 'displaylines')[0]
        if num_display_lines != self.old_num_display_lines:
            sheet.configure(height=num_display_lines)
            self.old_num_display_lines = num_display_lines
        sheet.edit_modified(False)

    def undo_separator(self):
        self.edit_separator()

    def bold(self):
        self.tag_selection('bold')


    def strikethrough(self):
        self.tag_selection('strikethrough')

    def remove_tag(self, tag):
        def pairwise(list):
            return zip(list[::2], list[1::2])
        print(f"{self.tag_ranges(tag)}=")
        for span in reversed(list(pairwise(self.tag_ranges(tag)))):
            print(f"+{self.get(*span)=}")
            print(f"+{len(self.get('1.0', 'end'))=}")
            self.delete(*span)
            print(f"-{self.get(*span)=}")
            print(f"-{len(self.get('1.0', 'end'))=}")

    def tag_selection(self, tag):
        def min_index(i1, i2):
            if self.compare(i1, '<=', i2):
                return i1
            else:
                return i2

        def max_index(i1, i2):
            if self.compare(i1, '>=', i2):
                return i1
            else:
                return i2

        def range_intersection(ranges, single_range):
            intersections = []
            for index_range in ranges:
                if  self.compare(max_index(index_range[0], single_range[0]), "<", min_index(index_range[1], single_range[1])):
                    intersections.append((max_index(index_range[0], single_range[0]), min_index(index_range[1], single_range[1])))
            return intersections


        if not self.tag_ranges(SEL):
            return
        tag_ranges = self.tag_ranges(tag)
        iters = [iter(tag_ranges)] * 2
        ranges = list(zip(*iters))
        sel = (self.index(SEL_FIRST), self.index(SEL_LAST))
        tag_in_selection = range_intersection(ranges, sel)

        if tag_in_selection:
            self.tag_remove(tag, *sel)
        else:
            self.tag_add(tag, *sel)
