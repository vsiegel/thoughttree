import re
import tkinter as tk
from tkinter import CURRENT, END, INSERT, SEL, WORD, X, SEL_FIRST, SEL_LAST, RAISED, BOTH
from tkinter.scrolledtext import ScrolledText
from tkinter.simpledialog import askstring
from typing import Union

from Cursorline import Cursorline
from FinishReasonIcon import FinishReasonIcon
from Fonts import Fonts
from Notebook import Notebook
from ThoughttreeConfig import conf
from Title import new_child_title, new_sibling_title
from tools import on_event


class Sheet(ScrolledText):

    def __init__(self, master=None, scrollbar=True, autohide=False, width=80, borderwidth=0, padx=0, pady=0, height=0,
                 grow=True, background='white', **kw):
        ScrolledText.__init__(
            self, master, undo=True, wrap=WORD, padx=padx, pady=pady, background=background,
            width=width, height=height, insertwidth=3, font=Fonts.FONT,
            border=0, borderwidth=borderwidth, highlightthickness=0,
            selectbackground="#66a2d4", selectforeground="white", name="st", **kw)

        if scrollbar:
            self.vbar.config(width=18, takefocus=False, borderwidth=2)
        else:
            self.vbar.pack_forget()

        self.file = None
        self.pattern = None
        self.found = None
        self.initially_modified = False

        self.bind('<Prior>', self.jump_to_limit)
        self.bind('<Next>', self.jump_to_limit)
        # self.pack(padx=0, pady=0, fill=X, expand=True)

        name, size = self.cget("font").rsplit(None, 1)
        self.tag_config("assistant", background="#e0e0e0", selectbackground="#4682b4", selectforeground="white")
        self.cursorline = Cursorline(self)
        self.tag_config('bold', font=(name, int(size), "bold"))
        self.tag_config('strikethrough', overstrike=True)
        self.tag_config('found_one', background="#edee21", borderwidth=1, relief=RAISED)
        self.tag_config('found_all', background="#d9d55d")
        self.tag_config('highlight', background="#6cd8ff")
        self.tag_config('semi_highlight', background="#c8e7ff")
        self.tag_config("added", foreground="#9af1a9")
        self.tag_config("deleted", foreground="#f1a8ae")
        self.tag_config('hidden_markup', elide=True, foreground="#ADD8E6")
        self.tag_config('hidden_prompt', elide=True, foreground="#ADD8E6")

        self.old_num_display_lines = 0
        # if grow:
        #     self.bind('<<Modified>>', self.grow_to_displaylines, add=True)


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

    def find(self, pattern=None, start=INSERT):
        if self.tag_ranges(SEL):
            pattern = self.get(SEL_FIRST, SEL_LAST)
        else:
            pattern = askstring("Find", "Search for:", parent=self)
        if pattern:
            self.perform_search(pattern, start)

    def find_next(self):
        if self.found:
            self.perform_search(self.pattern, f"{self.found}+1c")

    def find_previous(self):
        if self.found:
            self.perform_search(self.pattern, self.found, backwards=True)

    def perform_search(self, pattern, start, backwards=False):
        self.found = self.search(pattern, start, exact=True, backwards=backwards)
        if self.found:
            self.mark_set(INSERT, self.found)
            print(f"Found: {self.found}")
        self.pattern = pattern
        self.tag_remove('found_one', "1.0", END)
        if self.found:
            self.tag_add('found_one', self.found, f"{self.found} + {len(self.pattern)} char")


    def transfer_content(self, to_sheet):
        content = self.get("1.0", tk.END)
        to_sheet.insert("1.0", content)

        for tag in self.tag_names():
            ranges = self.tag_ranges(tag)
            for i in range(0, len(ranges), 2):
                to_sheet.tag_add(tag, ranges[i], ranges[i + 1])
                to_sheet.tag_config(tag, **{k: v[4] for k, v in self.tag_config(tag).items() if v[4]})

        for name in self.window_names():
            index = self.index(name)
            window = self.nametowidget(name)
            to_sheet.window_create(index, window=window)



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
        pos = self.vbar.get()
        # print(pos) # "(0.0, 0.0, 0.0, 0.0)"
        top, bottom, *_ = pos
        if e.keysym == 'Prior' and top == 0.0:
            limit = "1.0"
        elif e.keysym == 'Next' and bottom == 1.0:
            limit = tk.END
        else:
            return

        self.mark_set(tk.INSERT, limit)
        self.see(tk.INSERT)


    def undo_separator(self):
        self.edit_separator()

    def bold(self):
        self.tag_selection('bold')


    def strikethrough(self):
        self.tag_selection('strikethrough')

    def remove_tag(self, tag):
        def pairwise(l):
            return list(zip(l[::2], l[1::2]))
        print(f"{self.tag_ranges(tag)}=")
        for span in reversed(pairwise(self.tag_ranges(tag))):
            print(f"+{self.get(*span)=}")
            print(f"+{len(self.get('1.0', 'end'))=}")
            self.delete(*span)
            self.insert(span[0], " ")
            self.edit_undo()
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


    def unbind(self, seq: str, funcid: str) -> None:
        self.bind(seq, re.sub(
            r'^if {"\[' + funcid + '.*$', '', self.bind(seq), flags=re.M
        ))
        self.deletecommand(funcid)
