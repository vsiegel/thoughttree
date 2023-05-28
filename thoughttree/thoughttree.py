#!/usr/bin/env python
import os
import tkinter as tk
from argparse import Namespace
from datetime import datetime
from tkinter import ttk, simpledialog
from tkinter import font as tkfont
from tkinter.messagebox import showinfo

import prompts
from ChatFileManager import ChatFileManager
from ToolTip import ToolTip
from GPT import GPT
from StatusBar import StatusBar
from Menu import Menu
from Text import Text
from prompts import system_prompt

CHATGPT_ICON = "chatgpt-icon.png"

conf = Namespace()
conf.show_finish_reason = True
conf.ring_bell_after_completion = False
conf.update_title_after_completion = True
conf.scroll_during_completion = True

#NODE_OPEN = '\u25B6'
#NODE_CLOSED = '\u25BC'
NODE_OPEN = '*'
NODE_CLOSED = '|'

class ThoughttreeMenu(Menu):
    def __init__(self, thoughttree):
        super().__init__(thoughttree.root, tearoff=0)

        self.tt = thoughttree
        self.root = thoughttree.root
        self.create_menu()

    def create_menu(self):

        def focus() -> Text:
            return self.root.focus_get()

        def save(save_dialog, status_bar_label):
            file_name = save_dialog(self.tt.chat)
            if not file_name:
                return
            base_name = file_name.split("/")[-1]
            self.tt.status_bar.main_text(status_bar_label + base_name)
            return base_name

        def save_chat(e=None):
            name = save(ChatFileManager.save_chat_dialog, "Chat saved to ")
            self.root.title(name)

        def save_section(e=None):
            save(ChatFileManager.save_section_dialog, "Section saved to ")

        def save_code_block(e=None):
            save(ChatFileManager.save_code_block_dialog, "Code block saved to ")

        def new_window(event=None) :
            Thoughttree()

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
            if type(txt) == Text:
                txt.tag_add(tk.SEL, "1.0", tk.END)
                txt.mark_set(tk.INSERT, "1.0")
                txt.see(tk.INSERT)

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
            txt = focus()
            if delta == 0:
                name, size = Text.FONT
            else:
                name, size = txt.cget("font").split()
            txt.config(font=(name, int(size) + delta))

        def insert_current_time(event=None):
            focus().insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        def menu_test(event=None):
            pass

        def item(label, keystroke, command, bind_key=True, context_menu=None):
            menu.item(label, keystroke, command, bind_key, context_menu)

        bar = Menu(self.tt.root)

        menu = Menu(bar, "File")
        item("New Window", "<Control-n>", new_window)
        item("Load Chat", None, lambda: ChatFileManager.load_chat_dialog(self.tt.chat))
        item("Save Chat", "<Control-s>", save_chat)
        item("Save Section", "<Control-Shift-S>", save_section)
        item("Save Code Block", "<Control-Shift-B>", save_code_block)
        item("Quit", "<Control-q>", self.tt.close)

        menu = Menu(bar, "Edit")
        item("Undo", "<Control-z>", edit_undo, False)
        item("Redo", "<Control-Shift-Z>", edit_redo, False)
        item("Select All", "<Control-a>", select_all)
        menu.add_separator()
        item("Insert Current Time", "", insert_current_time, False)

        menu = Menu(bar, "View")
        item("Show System Prompt", "", None)
        item("Show Tree", "", None)
        item("Count Tokens", "<Control-t>", self.tt.count_tokens)
        item("Run Code Block", "", None)
        item("Update Window Title", "<Control-u>", self.tt.update_window_title)
        item("Increase Font Size", "<Control-plus>", lambda e: change_text_size(1))
        item("Decrease Font Size", "<Control-minus>", lambda e: change_text_size(-1))
        item("Reset Font Size", "<Control-period>", lambda e: change_text_size(0))
        self.root.bind("<Control-Button-4>", lambda event: change_text_size(1))
        self.root.bind("<Control-Button-5>", lambda event: change_text_size(-1))

        menu = Menu(bar, "Navigate")
        item("Jump to Similar Line", "<Control-j>", self.tt.jump_to_similar_line)

        menu = Menu(bar, "Model")
        item("Cancel", "<Escape>", self.tt.gpt.cancel)
        item("Send Chat Message", "<Control-Return>", lambda e: self.tt.chat_continue("\n"))
        item("Complete Directly", "<Shift-Return>", lambda e: self.tt.chat_continue(""))
        item("Complete Multiple...", "<Control-m>", lambda e: self.tt.chat_continue("", "", 0))
        item("Complete Multiple Again", "<Alt-Return>", lambda e: self.tt.chat_continue("", "", -1))
        menu.add_separator()
        item("Complete 2 Times", "<Control-Key-2>", lambda e: self.tt.chat_continue("", "", 2))
        item("Complete 3 Times", "<Control-Key-3>", lambda e: self.tt.chat_continue("", "", 3))
        item("Complete 5 Times", "<Control-Key-5>", lambda e: self.tt.chat_continue("", "", 5))
        item("Complete 10 Times", "<Control-Key-0>", lambda e: self.tt.chat_continue("", "", 10))
        menu.add_separator()
        for model_name in self.tt.gpt.get_available_models() :
            if model_name == "gpt-4":
                key = "<Control-Alt-Key-4>"
            elif model_name == "gpt-3.5-turbo":
                key = "<Control-Alt-Key-3>"
            else:
                key = None
            item(f"{model_name}", key, lambda e, m=model_name: self.tt.set_model(m))

        menu = Menu(bar, "Help")
        item("Test", "<Control-Shift-T>", menu_test)
        item("About", None, None)

        menu = Menu(self.tt.chat)
        self.context_menu = menu
        item("Cut", "<Control-x>", cut_text, False)
        item("Copy", "<Control-c>", copy_text, False)
        item("Paste", "<Control-v>", paste_text, False)
        menu.add_separator()
        item("Undo", "<Control-z>", edit_undo, False)
        item("Redo", "<Control-Shift-Z>", edit_redo, False)
        item("Select All", "<Control-a>", command=select_all)
        self.root.bind_class("Text", "<Button-3>", show_context_menu)


class Thoughttree:
    MIN_WIDTH = 250
    MIN_HEIGHT = 100
    CHAT_WIDTH = 400
    ROOT_GEOMETRY = "1000x600"

    icon = None
    multi_completions = 3

    def __init__(self, root=None):
        self.root = root or tk.Tk()
        self.gpt = GPT()
        self.is_root_destroyed = False
        self.root.protocol("WM_DELETE_WINDOW", self.on_root_close)
        self.set_icon()
        self.create_ui()
        self.menu = ThoughttreeMenu(self)


    def set_icon(self):
        def get_icon_file_name(icon_base_name):
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), icon_base_name)

        if Thoughttree.icon:
            return
        try:
            abs_name = str(get_icon_file_name(CHATGPT_ICON))
            photo_image = tk.PhotoImage(file=abs_name)
            Thoughttree.icon = photo_image
            self.root.iconphoto(True, photo_image) # Note: has no effect when running in PyCharm IDE
        except Exception as e:
            print("Error loading icon:", e)

    def set_model(self, model_name):
        self.gpt.set_model(model_name)
        self.status_bar.right_text = model_name

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

        font_height = tkfont.Font(font=Text.FONT).metrics("linespace")
        style = ttk.Style(self.root)

        style.configure("Treeview", rowheight=2 * font_height + 0)
        # style.configure("Treeview", font=Text.TEXT_FONT)
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

        tree.bind('<Double-Button-1>', on_treeview_click)
        tree.bind_class("Treeview", "<KeyPress-Return>", lambda _: None)
        tree.bind_class("Treeview", "<KeyRelease-Return>", lambda _: None)
        # self.create_dummy_data(tree)

        self.hPane.add(tree)
        self.hPane.add(self.vPane)
        self.hPane.sash_place(0, 0, 0)

        children = tree.get_children()
        if children:
            tree.focus(children[0])
        tree.bind("<Double-Button-1>", self.edit_tree_entry)
        tree.bind("<Return>", self.edit_tree_entry)

        self.system = Text(self.vPane, system_prompt)
        self.chat = Text(self.vPane)
        self.system.config(pady=5)

        self.vPane.add(self.system)
        self.vPane.add(self.chat)
        self.chat.focus_set()

        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=None)

        self.root.config(menu=menubar)
        # self.root.config(menu=ThoughttreeMenu(self))
        # self.create_menu()

    def update_window_title(self, event=None):
        progress_title = self.root.title() + "..."

        def output_response_delta_to_title_callback(content):
            if self.is_root_destroyed:
                return
            current_title = self.root.title()
            if current_title == progress_title:
                current_title = ""
            self.root.title(current_title + content)
            self.root.update()

        self.root.title(progress_title)
        self.root.update()
        history = self.chat_history_from_textboxes(prompts.TITLE_GENERATION_PROMPT)
        model = GPT.internal_generation_model or GPT.model
        self.gpt.chat_complete(history, output_response_delta_to_title_callback,
            30, 1, model)


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

        txt: Text = self.root.focus_get()
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

    def chat_continue(self, prefix="", postfix="\n", number_of_completions=1) :
        txt: Text = self.root.focus_get()

        def insert_label(txt, label_text, tool_tip_text=""):
            label = tk.Label(txt, text=label_text, padx=8, bg="#F0F0F0", fg="grey")
            if tool_tip_text:
                ToolTip(label, tool_tip_text)
            txt.window_create(tk.END, window=label)

        def output_response_delta_to_chat_callback(text) :
            if self.is_root_destroyed :
                return
            txt.insert(tk.END, text, "assistant")
            if conf.scroll_during_completion:
                txt.see(tk.END)
            txt.update()

        if not number_of_completions:
            number_of_completions = simpledialog.askinteger(
                "Alternative completions",
                "How many alternative results do you want?",
                initialvalue=Thoughttree.multi_completions,
                minvalue=2, maxvalue=1000)
            if not number_of_completions:
                return
            Thoughttree.multi_completions = number_of_completions
        elif number_of_completions == -1:
            number_of_completions = Thoughttree.multi_completions

        if prefix :
            txt.insert(tk.END, prefix)
            txt.update()
        history = self.chat_history_from_textboxes()
        if number_of_completions == 1:
            finish_reason, message = self.gpt.chat_complete(history, output_response_delta_to_chat_callback)
        else:
            frame = tk.Frame(txt)
            for i in range(number_of_completions):
                label = tk.Label(frame, borderwidth=4, anchor=tk.E, wraplength=txt.winfo_width(),
                                 justify=tk.LEFT, font=Text.FONT, relief="ridge")
                txt.window_create(tk.END, window=frame)
                txt.insert(tk.END, "\n")

                def output_response_delta_to_label_callback(text):
                    if self.is_root_destroyed :
                        return
                    label.config(text=label.cget("text") + text)
                    # txt.insert(tk.END, text, "assistant")
                    if conf.scroll_during_completion:
                        txt.see(tk.END)
                    txt.update()

                finish_reason, message = self.gpt.chat_complete(history, output_response_delta_to_label_callback)

        if self.is_root_destroyed:
            return
        if conf.show_finish_reason:
            symbol = GPT.finish_reasons[finish_reason]["symbol"]
            if finish_reason not in ["stop", "length", "canceled", "error"] :
                print(f"{finish_reason=}")
            if symbol :
                tool_tip = GPT.finish_reasons[finish_reason]["tool_tip"]
                if message:
                    tool_tip += "\n" + message
                insert_label(txt, symbol, tool_tip)

        txt.insert(tk.END, postfix, "assistant")
        txt.mark_set(tk.INSERT, tk.END)
        txt.see(tk.END)

        if conf.ring_bell_after_completion:
            self.root.bell()
        if conf.update_title_after_completion:
            self.update_window_title()

    def chat_history_from_textboxes(self, additional_message=None) :
        system = self.system.get(1.0, 'end - 1c').strip()
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
        txt: Text = self.root.focus_get()
        try :
            text = txt.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError :
            text = txt.get(1.0, tk.END)
        old_status = self.status_bar.main_text
        self.status_bar.main_text = "Counting tokens (loading model)"
        num_tokens = self.gpt.count_tokens(text)
        num_lines = text.count("\n")
        num_words = len(text.split())
        num_chars = len(text)
        self.status_bar.main_text = old_status
        showinfo("Count Tokens",
                 f"The length of the text is:\n"
                 f"{num_tokens} tokens\n"
                 f"{num_lines} lines\n"
                 f"{num_words} words\n"
                 f"{num_chars} characters",
                 master=txt)
        return "break"

    @staticmethod
    def create_dummy_data(tree):
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
        char_width = tkfont.Font(font=Text.FONT).measure('0')
        line_height = tkfont.Font(font=Text.FONT).metrics("linespace")
        width = max(self.tree.column(column)["width"], width)
        height = max(line_height, height)

        cur_text = self.tree.item(row_id, "values")[0]
        w = width // char_width
        h = height // line_height
        txt = tk.Text(self.tree, wrap=tk.WORD, width=w, height=h, font=Text.FONT,
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
    def main(cls) :
        root = tk.Tk()
        Thoughttree(root)
        root.mainloop()

if __name__ == "__main__":
    Thoughttree.main()
