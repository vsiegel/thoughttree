import difflib
import re
import tkinter as tk
from os.path import exists
from tkinter import END, INSERT, SEL, WORD, SEL_FIRST, SEL_LAST, RAISED, SOLID, BOTH, LEFT, TOP
from tkinter.scrolledtext import ScrolledText
from tkinter.simpledialog import askstring

from Cursorline import Cursorline
from FinishReasonIcon import FinishReasonIcon
from Fonts import Fonts
from Keys import Keys
from LineHandling import LineHandling
from tools import fail

OUTPUT = "output"



class Sheet(ScrolledText, LineHandling):

    instances = []
    common_font_size = Fonts.FONT[1]

    def __init__(self, master=None, scrollbar=True, name="s", wrap=WORD, width=40, borderwidth=0,
                 highlightthickness=1, highlightcolor="lightgray",  insertbackground="#000",
                 insertwidth=3, insertunfocussed="none", #"none", "solid","hollow",
                 padx=0, pady=0, height=0, background='white', text="", font=None, **kw):
        font = font or Fonts.FONT
        ScrolledText.__init__(
            self, master, undo=True, wrap=wrap, padx=padx, pady=pady, background=background,
            width=width, height=height, insertwidth=insertwidth, insertunfocussed=insertunfocussed,
            insertbackground=insertbackground, font=font, insertborderwidth=1,
            border=0, borderwidth=borderwidth, highlightthickness=highlightthickness, highlightcolor=highlightcolor,
            highlightbackground="white", selectbackground="#66a2d4", selectforeground="white", name=name, **kw)
        self.frame.widgetName = "stf"
        self.register_instance()

        if scrollbar:
            self.vbar.config(width=18, takefocus=False, borderwidth=2)
        else:
            self.vbar.pack_forget()

        self.file = None
        self.pattern = None
        self.found = None
        self.initially_modified = False

        self.configure_sheet_keys_once()

        self.bind('<Prior>', self.jump_to_limit)
        self.bind('<Next>', self.jump_to_limit)
        # self.pack(padx=0, pady=0, fill=X, expand=True)


        name, size = self.cget("font").rsplit(None, 1) # fixme value
        self.tag_config("assistant", background="#e8e8e8", selectbackground="#4682b4", selectforeground="white")
        self.cursorline = Cursorline(self)
        self.tag_config('bold', font=(name, int(size), "bold"))
        self.tag_config('strikethrough', overstrike=True)
        self.tag_config('found_one', background="#f3eb24", borderwidth=1, relief=RAISED)
        self.tag_config('found_all', background="#d9d55d")
        self.tag_config('highlight', background="#6cd8ff")
        self.tag_config('semi_highlight', background="#c8e7ff")
        self.tag_config('hidden_markup', elide=False, foreground="#E0E0E0")
        self.tag_config('hidden_prompt', elide=False, foreground="#d0d0d0")
        self.tag_config("mask", borderwidth=2, relief=SOLID, foreground="#D0D0D0", selectforeground="#5cacee")

        # self.tag_bind("added", "<Enter>", on_event)
        self.tag_config("added", background="#9af1a9")
        self.tag_config("deleted", background="#f1a8ae")
        for tag in ["added", "deleted"]:
            self.tag_bind(tag, "<Button-1>", lambda event: self.elide_other(True, event))
            self.tag_bind(tag, "<ButtonRelease-1>", lambda event: self.elide_other(False, event))


        self.mark_set(OUTPUT, "1.0")
        self.mark_gravity(OUTPUT, tk.RIGHT)

        self.old_num_display_lines = 0
        if text:
            self.insert(END, text)


    configure_sheet_keys_done = False

    def configure_sheet_keys_once(self):
        if not Sheet.configure_sheet_keys_done:
            Keys.configure_sheet_keys(self)
            Sheet.configure_sheet_keys_done = True


    def split_sheet(self, to_sheet,  starting):
        trailing_text = self.get(starting, END)
        if self.get(starting) == "\n":
            trailing_text = trailing_text[1:]
        print(repr(self.get(starting)))
        to_sheet.insert("1.0", trailing_text)
        self.delete(starting, END)


    def insert_file(self, index, file):
        if file and exists(file):
            with open(file, mode="r", encoding="utf-8") as f:
                previous_index = self.index(index)
                self.insert(index, f.read())
                self.mark_set(INSERT, previous_index)


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
        if pattern:
            pass
        elif self.tag_ranges(SEL):
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

        def first(i1, i2):
            return self.compare(i1, '<=', i2) and i1 or i2

        def last(i1, i2):
            return self.compare(i1, '>=', i2) and i1 or i2

        def intersection(ranges, range):
            intersections = []
            for r in ranges:
                if  self.compare(last(r[0], range[0]), "<", first(r[1], range[1])):
                    intersections.append((last(r[0], range[0]), first(r[1], range[1])))
            return intersections


        if not self.tag_ranges(SEL):
            return
        tag_ranges = self.tag_ranges(tag)
        iters = [iter(tag_ranges)] * 2
        ranges = list(zip(*iters))
        sel = (self.index(SEL_FIRST), self.index(SEL_LAST))
        tag_in_selection = intersection(ranges, sel)

        if tag_in_selection:
            self.tag_remove(tag, *sel)
        else:
            self.tag_add(tag, *sel)

    def invert_tag(self, tag):
        print(f"{self.tag_ranges('mask')=}")


    def unbind(self, seq: str, funcid: str=None):
        if funcid:
            self.bind(seq, re.sub(
                r'^if {"\[' + funcid + '.*$', '', self.bind(seq), flags=re.M
            ))
            self.deletecommand(funcid)
        else:
            super().unbind(seq)

    def hide(self, index, chars, *args):
        if not self.search(chars, "1.0"):
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

        pos = self.search(old_text, 1.0, exact=True)
        pos or fail(f"Old text not found: {old_text}")

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

    # def hide(self, elide, event):
    def elide_other(self, elide, event):
        tags = self.tag_names(tk.CURRENT)

        ("added" in tags or "deleted" in tags) or fail(f"Cannot elide other tags: {tags}")

        tag = "deleted" if "added" in tags else "added"
        if elide:
            self.tag_config(tag, {"elide": True})
        else:
            self.tag_config(tag, {"elide": False})

    def backspace(self, event=None):
        sheet = event and event.widget or self
        sheet.delete(INSERT + "-1c")
        return "break"


    def register_instance(self):
        Sheet.instances.append(self)

    @staticmethod
    def font_size_all(delta=0):
        if not delta:
            size = Fonts.FONT[1]
        else:
            size = Sheet.common_font_size
        size = int(size)
        sign = int(size/abs(size))
        size = abs(size)
        new_size = size + delta


        for sheet in Sheet.instances:
            try:
                if sheet.winfo_exists():
                    sheet.font_size(delta)
            except Exception as ex:
                print(f"{ex=}")

    def font_size(self, delta=0):
        name, size = self.cget("font").rsplit(None, 1)
        if not delta:
            size = Fonts.FONT[1]
        size = int(size)
        sign = int(size/abs(size))
        size = abs(size)
        new_size = size + delta
        if new_size:
            self.config(font=(name, sign * new_size))

    def focusNextSheet(self):
        self.tk_focusNext().focus_set()

    def focusPrevSheet(self):
        # print(f"{self.tk_focusPrev()=}")
        self.tk_focusPrev().focus_set()
