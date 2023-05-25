#!/usr/bin/env python
import os
import tkinter as tk
from argparse import Namespace
from tkinter import ttk
from tkinter import font as tkfont
from tkinter.messagebox import showinfo
from tkinter.scrolledtext import ScrolledText

from ChatFileManager import ChatFileManager
from ToolTip import ToolTip
from GPT import GPT
from StatusBar import StatusBar
from Menu import Menu

CHATGPT_ICON = "chatgpt-icon.png"

DEFAULT_SYSTEM_PROMPT_FILE = "thoughttree-system.txt"
system_prompt = """Allways be terse.
Never apologize.
Use markdown to make it more readable.
"""
# open(DEFAULT_SYSTEM_PROMPT_FILE, 'r').read()

conf = Namespace()
conf.show_finish_reason = True
conf.ring_bell_after_completion = False
conf.scroll_during_completion = True

#NODE_OPEN = '\u25B6'
#NODE_CLOSED = '\u25BC'
NODE_OPEN = '*'
NODE_CLOSED = '|'


class Thoughttree:
    MIN_WIDTH = 250
    MIN_HEIGHT = 100
    CHAT_WIDTH = 400
    ROOT_GEOMETRY = "1000x600"
    TEXT_FONT = ("monospace", 10)

    def __init__(self, root, argv=None):
        self.root = root
        self.gpt = GPT()
        self.is_root_destroyed = False
        self.root.protocol("WM_DELETE_WINDOW", self.on_root_close)
        self.set_icon()
        self.create_ui()

    def set_icon(self):
        def get_icon_file_name(icon_file_name):
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), icon_file_name)

        try:
            abs_name = str(get_icon_file_name(CHATGPT_ICON))
            self.root.iconphoto(False, tk.PhotoImage(file=abs_name)) # Note: has no effect when running in PyCharm IDE
        except Exception as e:
            print("Error loading icon:", e)

    def set_model(self, model_name):
        self.gpt.set_model(model_name)
        self.status_bar.set_right_text(model_name)

    def on_root_close(self):
        self.is_root_destroyed = True
        self.root.destroy()

    def create_ui(self):
        self.root.title("Thoughttree")

        self.root.geometry(Thoughttree.ROOT_GEOMETRY)
        self.root.minsize(Thoughttree.MIN_WIDTH, Thoughttree.MIN_HEIGHT)

        self.root.option_add('*Text*insertWidth', '3')
        self.root.option_add('*Dialog*Font', ("sans-serif", 10))
        self.root.option_add('*Menu*Font', ("Arial", 10))
        self.root.option_add('*Font', ("Arial", 10))
        # self.root.option_add('*Text*Border', '6')
        # self.root.option_add('*Text*Background', 'red')
        # self.root.option_add('*Label*Background', 'red')
        # self.root.option_add('*Label*background', 'red')

        font_height = tkfont.Font(font=Thoughttree.TEXT_FONT).metrics("linespace")
        style = ttk.Style(self.root)

        style.configure("Treeview", rowheight=2 * font_height + 0)
        # style.configure("Treeview", font=Thoughttree.TEXT_FONT)
        style.configure("Treeview.Cell", anchor=tk.NW)
        style.configure("Treeview.Cell", padding=(1, 1))

        self.status_bar = StatusBar(self.root, right_text=self.gpt.model,
            main_text=f"Max tokens: {self.gpt.max_tokens} T: {self.gpt.temperature}")

        SASHWIDTH = 8
        self.hPane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=SASHWIDTH)
        self.hPane.pack(fill=tk.BOTH, expand=True)
        self.vPane = tk.PanedWindow(self.hPane, orient=tk.VERTICAL, sashwidth=SASHWIDTH)

        tree = ttk.Treeview(self.hPane, columns=("C1"), show="tree")
        self.tree = tree
        tree.column("#0", width=160, minwidth=60, anchor=tk.W, stretch=tk.NO)
        tree.column("#1", width=30, minwidth=60, anchor=tk.W, stretch=tk.NO)
        tree.heading("C1", text="")

        self.current_cell_editor = None

        def on_treeview_click(event):
            item = tree.identify('item', event.x, event.y)
            print(item)
            if item:
                if 'closed' in tree.item(item, 'tags'):
                    replaced = tree.item(item, 'text').replace(NODE_CLOSED, NODE_OPEN, 1)
                    print(replaced)
                    tree.item(item, text=replaced)
                    tree.item(item, tags='opened')
                elif 'opened' in tree.item(item, 'tags'):
                    tree.item(item, text=tree.item(item, 'text').replace(NODE_OPEN, NODE_CLOSED, 1))
                    tree.item(item, tags='closed')

        #tree.bind('<Double-Button-1>', on_treeview_click)

        self.create_dummy_data(tree)
        tree.bind_class("Treeview", "<KeyPress-Return>", lambda _: None)
        tree.bind_class("Treeview", "<KeyRelease-Return>", lambda _: None)

        self.hPane.add(tree)
        self.hPane.add(self.vPane)
        self.hPane.sash_place(0, 0, 0)

        tree.focus(tree.get_children()[0])
        tree.bind("<Double-Button-1>", self.edit_tree_entry)
        tree.bind("<Return>", self.edit_tree_entry)

        self.system_txt = self.create_textbox(self.vPane, system_prompt)
        self.system_txt.config(pady=5)

        self.chat = self.create_textbox(self.vPane, "")

        self.vPane.add(self.system_txt)
        self.vPane.add(self.chat)
        self.chat.focus_set()

        self.create_menu()

    def create_menu(self):

        def focus():
            return self.root.focus_get()

        def save_chat(e=None):
            file_name = ChatFileManager.save_chat_dialog(self.chat)
            if not file_name:
                return
            base_name = file_name.split("/")[-1]
            self.root.title(base_name)

        def save_section(e=None):
            file_name = ChatFileManager.save_section_dialog(self.chat)
            if not file_name:
                return
            # base_name = file_name.split("/")[-1]
            self.status_bar.set_main_text("Code section saved to " + file_name)

        def save_code_section(e=None):
            file_name = ChatFileManager.save_code_section_dialog(self.chat)
            if not file_name:
                return
            # base_name = file_name.split("/")[-1]
            self.status_bar.set_main_text("Code section saved to " + file_name)

        def new_window(event=None) :
            Thoughttree(tk.Tk())

        def show_context_menu(event) :
            widget = self.root.winfo_containing(event.x_root, event.y_root)
            if widget :
                widget.focus_set()
            self.context_menu.tk_popup(event.x_root, event.y_root)

        def cut_text(event=None) :
            focus().event_generate("<<Cut>>")

        def copy_text(event=None) :
            focus().event_generate("<<Copy>>")

        def paste_text(event=None) :
            text = focus()
            text.event_generate("<<Paste>>")
            print(event)
            text.see(tk.INSERT)

        def select_all(event=None):
            txt = focus()
            if type(txt) == tk.scrolledtext.ScrolledText:
                txt.tag_add(tk.SEL, "1.0", tk.END)
                txt.mark_set(tk.INSERT, "1.0")
                txt.see(tk.INSERT)

        def update_window_title(event=None):
            progress_title = "[Generating...]"

            def output_response_delta_to_title(content):
                if self.is_root_destroyed:
                    return
                current_title = self.root.title()
                if current_title == progress_title:
                    current_title = ""
                self.root.title(current_title + content)
                self.chat.update()

            self.root.title(progress_title)
            self.chat.update()
            history = self.chat_history_from_textboxes(GPT.TITLE_GENERATION_PROMPT)
            self.gpt.chat_complete(history, output_response_delta_to_title, 30, 1)


        def edit_undo():
            try:
                focus().edit_undo()
            except tk.TclError:
                pass # nothing to undo

        def edit_redo():
            try:
                focus().edit_redo()
            except tk.TclError:
                pass # nothing to redo

        def change_text_size(delta):
            text = focus()
            if delta == 0:
                name, size = Thoughttree.TEXT_FONT
            else:
                name, size = text.cget("font").split()
            text.config(font=(name, int(size) + delta))

        def menu_test(event=None):
            pass

        def item(label, keystroke, command, bind_key=True, context_menu=None):
            menu.item(label, keystroke, command, bind_key, context_menu)

        bar = Menu(self.root)

        menu = Menu(bar, "File")
        item("New Window", "<Control-n>", new_window)
        item("Load Chat", None, lambda: ChatFileManager.load_chat_dialog(self.chat))
        item("Save Chat", "<Control-s>", save_chat)
        item("Save Section", "<Control-Shift-S>", save_section)
        item("Save Code Section", "<Control-Shift-C>", save_code_section)
        item("Quit", "<Control-q>", self.close)

        menu = Menu(bar, "Edit")
        item("Undo", "<Control-z>", edit_undo, False)
        item("Redo", "<Control-Shift-Z>", edit_redo, False)
        item("Select All", "<Control-a>", command=select_all)

        menu = Menu(bar, "View")
        item("Show System Prompt", "", None)
        item("Show Tree", "", None)
        item("Count Tokens", "<Control-t>", self.count_tokens)
        item("Run Code Block", "", None)
        item("Update Window Title", "<Control-u>", update_window_title)
        item("Increase Font Size", "<Control-plus>", lambda e: change_text_size(1))
        item("Decrease Font Size", "<Control-minus>", lambda e: change_text_size(-1))
        item("Reset Font Size", "<Control-period>", lambda e: change_text_size(0))
        # txt.bind("<Control-Button-4>", lambda event: change_text_size(event, txt, 1))
        # txt.bind("<Control-Button-5>", lambda event: change_text_size(event, txt, -1))

        menu = Menu(bar, "Navigate")
        item("Jump to Similar Line", "<Control-j>", self.jump_to_similar_line)

        menu = Menu(bar, "Model")
        item("Continue Chat", "<Control-Return>", lambda e: self.chatWithGpt("\n\n"))
        item("Complete Directly", "<Shift-Return>", lambda e: self.chatWithGpt(""))
        menu.add_separator()
        for model_name in self.gpt.get_available_models() :
            menu.item(f"{model_name}", None, lambda m=model_name : self.set_model(m))

        menu = Menu(bar, "Output")
        item("Cancel", "<Escape>", self.gpt.cancel)

        menu = Menu(bar, "Help")
        item("Test", "<Control-Shift-T>", menu_test)
        item("About", None, None)

        menu = Menu(self.chat)
        self.context_menu = menu
        item("Cut", "<Control-x>", cut_text, False)
        item("Copy", "<Control-c>", copy_text, False)
        item("Paste", "<Control-v>", paste_text, False)
        menu.add_separator()
        item("Undo", "<Control-z>", edit_undo, False)
        item("Redo", "<Control-Shift-Z>", edit_redo, False)
        item("Select All", "<Control-a>", command=select_all)
        self.root.bind_class("Text", "<Button-3>", show_context_menu)


    def jump_to_similar_line(self, event=None) :

        def find_matching_line(target_line, line_nr_1, lines):
            line_nr_0 = line_nr_1 - 1
            num_lines = len(lines)
            if num_lines == 0:
                return 0
            stripped_target_line = target_line.strip()
            start = (line_nr_0 + 1) % num_lines
            numbered_lines = list(enumerate(lines[start :] + lines[:start]))
            for i, line in numbered_lines :
                if line.strip() == stripped_target_line:
                    return ((i + start) % num_lines) + 1
            return 0

        txt = self.root.focus_get()
        line_nr = int(txt.index('insert + 1 chars').split('.')[0])
        current_line = txt.get(f"{line_nr}.0", f"{line_nr}.end")
        if not current_line.strip():
            return
        lines = txt.get(1.0, tk.END).splitlines()
        jump_line = find_matching_line(current_line, line_nr, lines)
        if jump_line :
            jump_index = f"{jump_line}.{0}"
            txt.mark_set(tk.INSERT, jump_index)
            txt.see(jump_index)

    def create_textbox(self, parent, text) :

        lines = len(text.splitlines())
        txt = ScrolledText(parent, undo=True,
            wrap=tk.WORD, height=lines, padx=1, pady=1,
            font=self.TEXT_FONT, bd=0,
            highlightbackground='black', highlightcolor='green',
            selectbackground="#66a2d4", selectforeground="white")
        txt.vbar.config(width=16, takefocus=False)
        txt.pack(pady=0, fill=tk.X, expand=True)
        # txt.tag_configure("user", background="white", selectbackground="#5692c4", selectforeground="white")
        txt.tag_configure("assistant", background="#F0F0F0", selectbackground="#4682b4", selectforeground="white")
        txt.insert(tk.END, text, "user")
        return txt

    def chatWithGpt(self, prefix="", postfix="\n", number_of_completions=1) :

        def insert_label(text, label_text, tool_tip_text=""):
            label = tk.Label(text, text=label_text, padx=8, bg="#F0F0F0", fg="grey")
            if tool_tip_text:
                ToolTip(label, tool_tip_text)
            # label.pack(expand=True, fill="both")
            text.window_create(tk.END, window=label)

        def output_response_delta_to_chat(content) :
            if self.is_root_destroyed :
                return
            self.chat.insert(tk.END, content, "assistant")
            if conf.scroll_during_completion:
                self.chat.see(tk.END)
            self.chat.update()

        if prefix :
            self.chat.insert(tk.END, prefix)
            self.chat.update()
        history = self.chat_history_from_textboxes()
        finish_reason, message = self.gpt.chat_complete(history, output_response_delta_to_chat)
        if self.is_root_destroyed:
            return
        if conf.show_finish_reason:
            symbol = GPT.finish_reasons[finish_reason]["symbol"]
            tool_tip = GPT.finish_reasons[finish_reason]["tool_tip"]
            if message:
                tool_tip += "\n" + message
            if finish_reason not in ["stop", "length", "canceled", "error"] :
                print(f"{finish_reason=}")
            if symbol :
                insert_label(self.chat, symbol, tool_tip)

        self.chat.insert(tk.END, postfix, "assistant")
        self.chat.mark_set(tk.INSERT, tk.END)
        self.chat.see(tk.END)
        if conf.ring_bell_after_completion:
            self.root.bell()

    def chat_history_from_textboxes(self, additional_message=None) :
        system = self.system_txt.get(1.0, 'end - 1c').strip()
        history = [{'role': 'system', 'content': system}]
        content = self.chat.dump(1.0, tk.END, text=True, tag=True, window=True)
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
            elif item[0] == "text" :
                section += item[1]
            elif item[0] == "window":
                pass
            else:
                print(f"Ignored text widget item: {item}")
        if section!= "" :
            section = section.strip()
            if history[-1]['role'] == "user" :
                history += [{'role' : 'assistant', 'content' : section}]
            elif history[-1]['role'] in ["assistant", "system"] :
                history += [{'role' : 'user', 'content' : section}]
        if additional_message:
            history += [{'role': 'user', 'content': additional_message}]
        return history

    def count_tokens(self, event=None) :
        try :
            text = self.chat.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError :
            text = self.chat.get(1.0, tk.END)
        self.status_bar.set_main_text("Counting tokens (loading model)")
        num_tokens = self.gpt.count_tokens(text)
        num_lines = text.count("\n")
        num_words = len(text.split())
        num_chars = len(text)
        self.status_bar.set_main_text("")
        showinfo("Count Tokens",
                 f"The length of the text is:\n"
                 f"{num_tokens} tokens\n"
                 f"{num_lines} lines\n"
                 f"{num_words} words\n"
                 f"{num_chars} characters")
        return "break"

    def create_dummy_data(self, tree):
        for r in range(10):
            key = f"R{r}"
            parent_id = tree.insert("", "end", key, text=key, values=(r,))
            tree.item(key, tags='closed')
            if r % 2 == 0:
                for c in range(2):
                    child_key = f"R{r}_C{c}"
                    tree.insert(parent_id, "end", child_key, text=child_key, values=(c,))
                    tree.item(child_key, open=True, tags='opened')
                    for g in range(2):
                        grandchild_key = f"{child_key}_G{g}"
                        tree.insert(child_key, "end", grandchild_key, text=grandchild_key, values=(g,))
                        tree.item(grandchild_key, tags='closed')

    def close(self, event=None):
        self.is_root_destroyed = True
        self.root.destroy()

    def edit_tree_entry(self, event):
        row_id = self.tree.focus()
        if not row_id:
            return
        column = self.tree.identify_column(event.x)
        if column != "#1":  # Only allow editing the "Messages" column
            return
        x, y, width, height = self.tree.bbox(row_id, column)
        char_width = tkfont.Font(font=self.TEXT_FONT).measure('0')
        line_height = tkfont.Font(font=self.TEXT_FONT).metrics("linespace")
        width = max(self.tree.column(column)["width"], width)
        height = max(line_height, height)

        cur_text = self.tree.item(row_id, "values")[0]
        w = width // char_width
        h = height // line_height
        txt = tk.Text(self.tree, wrap=tk.WORD, width=w, height=h, font=self.TEXT_FONT,
                      highlightthickness=0, highlightbackground="black", padx=4, pady=0)
        txt.insert(tk.END, cur_text)
        txt.place(x=x, y=y)
        txt.focus_set()

        def save_text(event):
            print(event.type)
            if event.type == tk.EventType.FocusOut or int(event.state) & 0x4 == 0 :  # Check if Control key is not pressed
                text = txt.get(1.0, tk.END).strip()
                self.tree.set(row_id, column, text)
                txt.destroy()

        # txt.bind("<FocusOut>", save_text)
        txt.bind("<Return>", lambda e: e.state & 0x4 == 0 and save_text(e) or self.tree.focus_set())
        txt.bind("<Control-Return>", lambda e: txt.insert(tk.INSERT, "\n") or "break")
        # txt.bind("<Control-Key>", lambda e : "break")
        # txt.bind("<Control_L>", lambda e : "break")

    @classmethod
    def main(argv=None) :
        root = tk.Tk()
        Thoughttree(root, argv)
        root.mainloop()

if __name__ == "__main__":
    Thoughttree.main()
