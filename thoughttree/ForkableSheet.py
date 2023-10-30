import sys
import tkinter as tk
from tkinter import X, BOTH, Y, INSERT, END, CURRENT, SEL

from ForkFrame import ForkFrame
from Notebook import Notebook
from Sheet import Sheet
from Title import new_child_title, new_sibling_title, Title


class ForkableSheet(Sheet):
    def __init__(self, parent_frame, parent_sheet=None, parent_notebook=None, parent_sheet_tree=None, name="fs", *args, **kw):
        self.fork_frame = ForkFrame(parent_frame)
        self.fork_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.fork_frame.forkable_sheet = self
        Sheet.__init__(self,  self.fork_frame, name=name, height=1, width=250, scrollbar=False, background="white", *args, **kw)
        self.pack(side=tk.TOP, fill=BOTH, expand=True)
        self.frame.pack_propagate(False)
        self.fork_frame.pack_propagate(False)
        # self.pack_propagate(False)

        self.parent_sheet = parent_sheet
        self.parent_notebook = parent_notebook
        self.parent_sheet_tree = parent_sheet_tree
        if self.parent_sheet_tree:
            self.parent_sheet_tree.bind("<Configure>", self.parent_sheet_tree.configure_scrollregion, add=True)
        self.child_notebook = None

        self.previous_sheet_height = None #todo
        self.unbind("<BackSpace>")
        self.bind_class("Text", "<BackSpace>", self.close_empty_tab_or_backspace)
        self.bind('<<Modified>>', self.grow_to_displaylines, add=True)
        # def on_key(e):
        #     print(f"on_key: {self.bbox(INSERT)=}")
        # self.bind("<KeyRelease>", on_key, add=True)

    def grow_to_displaylines(self, event: tk.Event):
        if self.edit_modified():
            sheet:ForkableSheet = event.widget
            # sheet:ForkableSheet = self
            print(f"grow_to_displaylines:" + str(sheet))
            sheet.count("1.0", "end", "update")
            ypixels = sheet.count("1.0", "end lineend", 'ypixels')[0]
            print(f"ypixels: {ypixels}")
            # sheet.frame.configure(height=ypixels)
            height = ypixels
            if sheet.child_notebook:
                notebook_height = sheet.child_notebook.winfo_height()
                print(f"height: {sheet.child_notebook.winfo_height()=}")
                print(f"height: {sheet.child_notebook.winfo_reqheight()=}")
                height += notebook_height
            width = sheet.master.winfo_width()
            print(f"WxH: {width}x{height}")
            sheet.frame.configure(height=ypixels)
            self.fork_frame.configure(width=width, height=height)
            sheet.event_generate("<Configure>", x=0, y=0, width=width, height=height)
            sheet.edit_modified(False)

    def generate_title(self, event=None):
        def get():
            return self.parent_notebook.tab(CURRENT, option="text")
        def set(title):
            self.parent_notebook.tab(CURRENT, text=title)
        self.generate(get, set)


    def generate(self, get, set):
        progress_title = get().split(" ")[0] + " ..."
        print(f"{progress_title=}")

        def write_title(delta):
            # if self.is_root_destroyed or self.model.is_canceled:
            #     return
            current_title = get()
            if current_title == progress_title:
                current_title = progress_title.split(" ")[0] + " "
            set(current_title + delta)
            self.update()

        set(progress_title)
        self.update()

        history = self.history_from_system_and_chat(Title.PROMPT, max_messages=5,
                                                    max_size=1000)  # todo limit, do not use system for title

        self.generation_model.counter.go()
        self.generation_model.complete(history, write_title, max_tokens=30, temperature=0.3)
        self.generation_model.counter.summarize("Title cost:")

    def create_child_notebook(self): # make sure we have a notebook
        if not self.child_notebook:
            self.child_notebook = Notebook(self.fork_frame, self, self.parent_notebook)
            self.child_notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            self.pack_configure(expand=False)
            first_child = new_child_title(self.parent_notebook)
            # self.child_notebook.bind("<<NotebookTabChanged>>", self.grow_to_displaylines)
            return self.child_notebook.add_sheet(first_child, parent_sheet=self)

    def fork(self, index=INSERT):
        index = self.index(index)
        self.initially_modified = True

        leading_text = bool(self.get("1.0", index).strip())


        def move_trailing_text(from_sheet, to_sheet, starting):
            trailing_text = from_sheet.get(starting, END).rstrip()
            to_sheet.insert("1.0", trailing_text)
            from_sheet.delete(starting, END)


        if not self.child_notebook:
            if leading_text:
                sheet = self.create_child_notebook()
                move_trailing_text(self, sheet, index)
                notebook = self.child_notebook
            else:
                if self.parent_notebook:
                    notebook = self.parent_notebook
                else:
                    sheet = self.create_child_notebook()
                    move_trailing_text(self, sheet, index)
                    notebook = self.child_notebook
        else:
            notebook = self.child_notebook

        sibling = new_sibling_title(notebook)
        if notebook == self.parent_notebook:
            parent = self.parent_sheet
        else:
            parent = self
        notebook.add_sheet(sibling, parent)
        return "break"


    def selected_sheet(self):
        if not self.child_notebook:
            return None
        return self.child_notebook.selected_sheet()


    def child_sheets(self)->['ForkableSheet']:
        if not self.child_notebook:
            return []
        return self.child_notebook.child_sheets()

    def winfo_reqheight(self):
        reqheight = self.count("1.0", "end lineend", 'ypixels')[0]

        if self.child_notebook:
            reqheight += self.child_notebook.winfo_reqheight()
        return reqheight


    def history_from_path(self, history=None) :
        if self.parent_sheet:
            history = self.parent_sheet.history_from_path(history)
        else:
            history = history or []

        return history + self.as_history()


    def as_history(self):
        print(f"as_history: {self.winfo_name()=}")

        history = []
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


    def close_tab(self):

        notebook: Notebook = self.parent_notebook
        if notebook and notebook.tabs():
            print(f"{self.focus_get()    =}")
            selected = notebook.index(CURRENT)
            # sheet = selected_sheet(notebook)
            sheet = notebook.selected_sheet()
            notebook.forget(selected)

            if notebook.tabs():
                notebook.select(max(selected - 1, 0))
                print(f"{sheet           =}")
                notebook.selected_sheet().focus_set()
                print(f"{self.focus_get()=}")
                sheet.insert(END, "c")
            else:
                tab_text = sheet.get('1.0', END)
                self.parent_sheet.insert(END, tab_text)
                self.parent_sheet.mark_set(INSERT, "end-1 char")
                self.parent_sheet.focus_set()
                self.parent_notebook.pack_forget()
                self.parent_notebook = None
                self.pack_configure(expand=True)
            return "break"


    def close_empty_tab_or_backspace(self, event=None):
        sheet = event and event.widget or self
        if sheet.index(INSERT) == "1.0" and not sheet.tag_ranges(SEL):
            notebook: Notebook = sheet.parent_notebook
            if notebook:
                string_in_tab = sheet.get('1.0', END).strip()
                if not string_in_tab:
                    sheet.close_tab()
        else:
            sheet.delete(INSERT + "-1c")
        return "break"
