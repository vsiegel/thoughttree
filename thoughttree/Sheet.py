import difflib
import re
import tkinter as tk
from os.path import exists
from tkinter import END, INSERT, SEL, WORD, SEL_FIRST, SEL_LAST, RAISED, SOLID
from tkinter.scrolledtext import ScrolledText
from tkinter.simpledialog import askstring

from Cursorline import Cursorline
from FinishReasonIcon import FinishReasonIcon
from Fonts import Fonts
from Keys import Keys
from LineHandling import LineHandling

OUTPUT = "output"

# added_colors = {"foreground": "#77ee77"}
# deleted_colors = {"foreground": "#ee7777"}
added_colors = {"background" : "#9af1a9"}
deleted_colors = {"background": "#f1a8ae"}


class Sheet(ScrolledText, LineHandling):

    def __init__(self, master=None, scrollbar=True, name="s", wrap=WORD, width=80, borderwidth=0,
                 highlightthickness=1, highlightcolor="lightgray", padx=0, pady=0, height=0, background='white', text="", **kw):
        ScrolledText.__init__(
            self, master, undo=True, wrap=wrap, padx=padx, pady=pady, background=background,
            width=width, height=height, insertwidth=3, font=Fonts.FONT,
            border=0, borderwidth=borderwidth, highlightthickness=highlightthickness, highlightcolor=highlightcolor, highlightbackground="white",
            selectbackground="#66a2d4", selectforeground="white", name=name, **kw)
        self.frame.widgetName = "stf"

        if scrollbar:
            self.vbar.config(width=18, takefocus=False, borderwidth=2)
        else:
            self.vbar.pack_forget()

        self.file = None
        self.pattern = None
        self.found = None
        self.initially_modified = False

        Keys.configure_text_keys(self)

        self.bind('<Prior>', self.jump_to_limit)
        self.bind('<Next>', self.jump_to_limit)
        # self.pack(padx=0, pady=0, fill=X, expand=True)

        name, size = self.cget("font").rsplit(None, 1)
        self.tag_config("assistant", background="#e8e8e8", selectbackground="#4682b4", selectforeground="white")
        self.cursorline = Cursorline(self)
        self.tag_config('bold', font=(name, int(size), "bold"))
        self.tag_config('strikethrough', overstrike=True)
        self.tag_config('found_one', background="#f3eb24", borderwidth=1, relief=RAISED)
        self.tag_config('found_all', background="#d9d55d")
        self.tag_config('highlight', background="#6cd8ff")
        self.tag_config('semi_highlight', background="#c8e7ff")
        self.tag_config('hidden_markup', elide=True, foreground="#E0E0E0")
        self.tag_config('hidden_prompt', elide=True, foreground="#E0E0E0")
        self.tag_config("mask", borderwidth=2, relief=SOLID, foreground="#D0D0D0")

        self.tag_config("added", **added_colors)
        self.tag_config("deleted", **deleted_colors)
        for tag in ["added", "deleted"]:
            self.tag_bind(tag, "<Button-1>", lambda event: self.elide_other(True, event))
            self.tag_bind(tag, "<ButtonRelease-1>", lambda event: self.elide_other(False, event))


        self.mark_set(OUTPUT, "1.0")
        self.mark_gravity(OUTPUT, tk.RIGHT)

        self.old_num_display_lines = 0
        if text:
            self.insert(END, text)


    def insert_file(self, index, file):
        if file and exists(file):
            with open(file, mode="r", encoding="utf-8") as f:
                self.insert(index, f.read())


    def run_code_block(self, event=None):
        code_block_start_pattern =  '("""|' + """'''|```)python.*\n"""
        code_block_pattern = """('{3}|"{3}|```)python.*\n([\s\S]*?)\\1"""
        start = self.search(code_block_start_pattern, INSERT, regexp=True, backwards=True)
        if start:
            text = self.get(start, END)
            m = re.search(code_block_pattern, text)
            if m:
                code = m.group(2)
                names = dict()
                print(f'Executing code block ("{code[:50]}"):')
                exec(code, names, names)
                print(f'Code block finished.')

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
        content = self.get("1.0", 'end-1c')
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


    def undo_separator(self):
        self.edit_separator()

    def bold(self):
        self.toggle_tag('bold')

    def strikethrough(self):
        self.toggle_tag('strikethrough')

    def role(self, role):
        pass
        # self.toggle_tag('strikethrough')

    def delete_tagged(self, tag):
        def pairwise(l):
            return list(zip(l[::2], l[1::2]))
        for span in reversed(pairwise(self.tag_ranges(tag))):
            self.delete(*span)
            self.insert(span[0], " ")
            self.edit_undo()

    def toggle_tag(self, tag):
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


    def unbind(self, seq: str, funcid: str=None):
        if funcid:
            self.bind(seq, re.sub(
                r'^if {"\[' + funcid + '.*$', '', self.bind(seq), flags=re.M
            ))
            self.deletecommand(funcid)
        else:
            super().unbind(seq)

    def hide(self, index, chars, *args):
        self.insert(index, chars, ("hidden_prompt",), *args)

    def insert_diff(self, old_text, new_text, pos=INSERT):
        diff_by_char = True

        def added(words):
            self.insert(INSERT, diff_words_join(words), "added")

        def deleted(words):
            self.insert(INSERT, diff_words_join(words), "deleted")

        def diff_words(text):
            if diff_by_char:
                return [c for c in text]
            else:
                return text.split()

        def diff_words_join(diffwords):
            if diff_by_char:
                return "".join(diffwords)
            else:
                return " ".join(diffwords) + " "

        old_pos = self.search(old_text, 1.0, exact=True)
        if old_pos:
            pos = old_pos


        self.mark_set(INSERT, pos)
        self.delete(pos, f"{pos}+{len(old_text)}c")

        old_words = diff_words(old_text)
        new_words = diff_words(new_text)
        matcher = difflib.SequenceMatcher(None, old_words, new_words, autojunk=False)

        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == "equal":
                self.insert(INSERT, diff_words_join(old_words[i1:i2]))
            elif op == "insert":
                added(new_words[j1:j2])
            elif op == "delete":
                deleted(old_words[i1:i2])
            elif op == "replace":
                deleted(old_words[i1:i2])
                added(new_words[j1:j2])

    def elide_other(self, elide, event):
        elide_by_color = False
        tags = self.tag_names(tk.CURRENT)

        if not ("added" in tags or "deleted" in tags):
            return
        if elide:
            tag = "deleted" if "added" in tags else "added"
            self.tag_config(tag, elide_by_color and {"foreground": "white"} or {"elide": True})
        else:
            config = added_colors if elide_by_color else {"elide": False}
            self.tag_config("added", **config)
            config = deleted_colors if elide_by_color else {"elide": False}
            self.tag_config("deleted", **config)

    def backspace(self, event=None):
        sheet = event and event.widget or self
        sheet.delete(INSERT + "-1c")
        return "break"
