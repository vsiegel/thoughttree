import tkinter as tk
from tkinter import X, BOTH, Y, INSERT, END, CURRENT, SEL, LEFT, TOP, RIGHT, VERTICAL, NW

import Colors
import tools
from History import History
from Notebook import Notebook
from ResizingSheet import ResizingSheet
from Sheet import Sheet
from Title import new_child_title, new_sibling_title, Title

class TreeSheet(tk.Frame):
    def __init__(self, *args, **kw):
        tk.Frame.__init__(self, background="#daa6ea", *args, **kw)

        self.sheet = ResizingSheet(self, background="#a5d6ea")
        self.sheet.sheet.insert("1.0", "A\n\nZ")

        # self.sheet.pack_propagate(False)
        # self.pack_propagate(False)

        self.notebook = Notebook(self, background="#eed6ea")
        self.sheet.pack(side=tk.TOP, fill=X, expand=False, anchor=tk.N)
        self.notebook.pack(side=tk.TOP, fill=BOTH, expand=True)

        # self.sheet2 = ResizingSheet(self.notebook, background="#dee5d7")
        # self.notebook.add(self.sheet2)
        # self.notebook.add(ResizingSheet(self.notebook, background="#dee5d7"))


        # self.bind("<FocusIn>", lambda event: self.sheet.focus_set(), add=True)


        # self.fork_frame.pack_propagate(False)
        # self.pack(side=tk.TOP, fill=BOTH, expand=True)
        #
        # self.parent_sheet = parent_sheet
        # self.parent_notebook = parent_notebook
        # self.parent_sheet_tree = parent_sheet_tree
        # self.child_notebook = None
        #
        # self.previous_sheet_height = None #todo
        # self.unbind("<BackSpace>")
        # self.bind_class("Text", "<BackSpace>", self.backspace)

    def branch(self):
        # frame = tk.Frame(self.notebook, background="#a5d6ba", borderwidth=3)
        sheet = TreeSheet(self.notebook)
        # sheet.pack(side=tk.TOP, fill=BOTH, expand=True)
        # sheet.pack(fill=BOTH, expand=True)
        self.notebook.add(sheet)

    def sheet_configure(self, event):
        print(f"sheet_configure: {event=} on {event.widget=} rh: {event.widget.winfo_reqheight()}")

    def notebook_configure(self, event):
        print(f"notebook_configure: {event=} on {event.widget=} rh: {event.widget.winfo_reqheight()}")

    def update_tab_title(self, event=None):
        def get():
            return self.parent_notebook.tab(CURRENT, option="text")
        def set(title):
            self.parent_notebook.tab(CURRENT, text=title)
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

        # history = self.history_from_system_and_chat(Title.PROMPT, max_messages=5, max_size=1000)
        prompt_history = [{'role' : "system", 'content' : Title.PROMPT}]
        history = self.history_from_path(prompt_history)

        Title.model.complete(history, write_title, max_tokens=30, temperature=0.3)
        Title.model.counter.summarize("Title cost:")

    def create_child_notebook(self): # make sure we have a notebook
        if not self.notebook:
            self.notebook = Notebook(self.frame, self, self.parent_notebook)
            self.notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            self.pack_configure(expand=False)
            first_child = new_child_title(self.parent_notebook)
            # self.child_notebook.bind("<<NotebookTabChanged>>", self.grow_to_displaylines)
            return self.notebook.add_sheet(first_child, parent_sheet=self)

    def fork(self, index=INSERT, duplicate=False):
        index = self.index(index)
        self.initially_modified = True

        leading_text = bool(self.get("1.0", index).strip())


        def copy_trailing_text(from_sheet, to_sheet, starting):
            trailing_text = from_sheet.get(starting, END).rstrip()
            to_sheet.insert("1.0", trailing_text)


        if self.notebook:
            notebook = self.notebook
        elif not leading_text and self.parent_notebook:
            notebook = self.parent_notebook
        else:
            sheet = self.create_child_notebook()
            copy_trailing_text(self, sheet, index)
            notebook = self.notebook

        sibling = new_sibling_title(notebook)
        if notebook == self.parent_notebook:
            parent = self.parent_sheet
        else:
            parent = self
        sheet = notebook.add_sheet(sibling, parent)
        # copy_trailing_text(self, sheet, index)
        self.delete(index, END)
        return "break"


    def selected_sheet(self):
        if not self.notebook:
            return None
        return self.notebook.selected_sheet()


    def child_sheets(self)->['ForkableSheet']:
        if not self.notebook:
            return []
        return self.notebook.child_sheets()


    def history_from_path(self, history=None) :
        if self.parent_sheet:
            history = self.parent_sheet.history_from_path(history)
        else:
            history = history or History()

        return history + History(self)


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
                tab_text = sheet.get('1.0', 'end-1c')
                self.parent_sheet.insert(END, tab_text)
                self.parent_sheet.mark_set(INSERT, 'end-1c')
                self.parent_sheet.focus_set()
                self.parent_notebook.pack_forget()
                self.parent_notebook = None
                self.pack_configure(expand=True)
            return "break"


    def backspace(self, event=None): # close_empty_tab_or_backspace
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



class TreeSheetTree(tk.Frame):
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, name="st", highlightthickness=3, highlightcolor=Colors.highlight, background="#d5d6aa", *args, **kw)

        self.canvas = tk.Canvas(self, name="c", background="lightcyan")
        self.scrollbar = tk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview, width=18, takefocus=False, borderwidth=2)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.frame = tk.Frame(self.canvas, bd=0, background="#eeeeff", name="cf")

        self.frame_id = self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        # self.height_spacer = tk.Frame(self.frame, width=0, height=0)
        # self.height_spacer.pack(side=RIGHT, fill=Y)

        self.sheet = TreeSheet(self.frame)
        self.sheet.branch()
        self.sheet.branch()
        self.sheet.pack(side=TOP, expand=True, fill=BOTH)
        # self.add_scrolling()

        self.canvas.bind("<Configure>", self.configure_frame, add=True)
        self.frame.bind("<Configure>", self.configure_scrollregion, add=True)

        # self.winfo_toplevel().bind("<Control-Alt-Shift-S>", self.debug)

    def configure_frame(self, event):
        self.canvas.itemconfigure(self.frame_id, width=event.width)
        # self.height_spacer.configure(height=event.height)

    def configure_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))



if __name__ == "__main__":
    root = tk.Tk()
    tools.escapable(root)
    # widget = TreeSheet(root)
    widget = TreeSheetTree(root)
    widget.pack(side=LEFT, fill=BOTH, expand=True)
    # widget.branch()
    # widget.notebook.add(TreeSheet(widget.notebook))
    # widget.pack_propagate(False)
    widget.focus_set()
    root.mainloop()
