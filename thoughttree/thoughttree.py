#!/usr/bin/env python
import tkinter as tk
from tkinter import BOTH, DISABLED, END, HORIZONTAL, INSERT, LEFT, NO, SUNKEN, TOP, VERTICAL, W, WORD, X, SEL_FIRST, \
    SEL_LAST
from tkinter import font as tkfont
from tkinter import ttk, simpledialog
from tkinter.messagebox import showinfo

from configargparse import Namespace

import prompts
from FinishReasonIcon import FinishReasonIcon
from FoldablePane import FoldablePane
from Model import Model
from StatusBar import StatusBar
from Text import Text
from ThoughttreeMenu import ThoughttreeMenu
from UI import UI
from WaitCursor import WaitCursor
from prompts import system_prompt

WINDOW_ICON = "chatgpt-icon.png"

conf = Namespace()
conf.show_finish_reason = True
conf.update_title_after_completion = True
conf.scroll_output = True
conf.ring_bell_after_completion = False
conf.blinking_caret = True

#NODE_OPEN = '\u25B6'
#NODE_CLOSED = '\u25BC'
NODE_OPEN = '*'
NODE_CLOSED = '|'


class Thoughttree(UI):
    MIN_WIDTH = 600
    MIN_HEIGHT = 300
    ROOT_GEOMETRY = "1000x600"
    GEN_TITLE_THRESHOLD = 20
    icon = None
    multi_completions = 5

    # self.model_name = 'gpt-4'
    model_name = 'gpt-3.5-turbo'
    generation_model_name = 'gpt-3.5-turbo'


    def __init__(self):
        UI.__init__(self, "Thoughttree", WINDOW_ICON)
        self.console = None
        self.tree = None
        self.system = None
        self.chat = None
        self.status_bar = None
        self.model = None
        self.console_pane = None
        self.tree_pane = None
        self.system_pane = None

        self.max_tokens = None
        self.temperature = None

        self.geometry(Thoughttree.ROOT_GEOMETRY)
        self.minsize(Thoughttree.MIN_WIDTH, Thoughttree.MIN_HEIGHT)
        self.protocol("WM_DELETE_WINDOW", self.close)
        try:
            self.set_icon(self.WINDOW_ICON)
        except:
            print("Error loading icon.")

        self.scroll_output = conf.scroll_output
        self.ring_bell_after_completion = conf.ring_bell_after_completion
        self.is_root_destroyed = False
        self.is_title_immutable = False
        self.create_ui()

        def new_window_callback():
            Thoughttree()
        self.models = {}
        self.generation_model = Model(self.generation_model_name)
        self.set_model(self.model_name)
        menu = ThoughttreeMenu(self, new_window_callback)

        self.status_bar.note = "Loading available models..."
        menu.create_available_models_menu_items()
        self.status_bar.note = ""


    def set_model(self, model_name):
        if not model_name in self.models:
            self.models[model_name] = Model(model_name)
        self.model = self.models[model_name]
        self.status_bar.model = model_name
        self.status_bar.set_max_token_var(self.model.max_tokens)
        self.status_bar.set_temperature_var(self.model.temperature)

    def cancelModels(self, event=None):
        for model in self.models.values():
            model.cancel()

    def create_ui(self):

        self.configure_ui_options()

        self.status_bar = StatusBar(self)

        self.create_panes()

        self.tree = self.create_tree(self.tree_pane, self.system_pane)
        self.console = self.create_console(self.console_pane)
        self.system = Text(self.system_pane, system_prompt, pady=5)
        self.chat = Text(self.system_pane)

        self.console_pane.add(self.tree_pane)
        self.console_pane.addFoldable(self.console)
        self.tree_pane.addFoldable(self.tree)
        self.tree_pane.add(self.system_pane)
        self.system_pane.addFoldable(self.system)
        self.system_pane.add(self.chat)

        self.chat.focus_set()

    def configure_ui_options(self):
        self.option_add('*Dialog*Font', ("sans-serif", 10))
        self.option_add('*Menu*Font', ("Arial", 10))
        self.option_add('*Font', ("Arial", 10))
        if not conf.blinking_caret:
            self.option_add('*Text*insertOffTime', '0')

    def create_panes(self):
        self.console_pane = FoldablePane(self, folded=False, fold_size=200, orient=VERTICAL)
        self.tree_pane = FoldablePane(self.console_pane, folded=False, fold_size=500, orient=HORIZONTAL)
        self.system_pane = FoldablePane(self.tree_pane, folded=True, orient=VERTICAL)
        self.console_pane.pack(fill=BOTH, expand=True)

    def create_tree(self, tree_pane, system_pane):

        def on_treeview_click(event):
            item = tree.identify('item', event.x, event.y)
            if item:
                if 'closed' in tree.item(item, 'tags'):
                    replaced = tree.item(item, 'text').replace(NODE_CLOSED, NODE_OPEN, 1)
                    tree.item(item, text=replaced)
                    tree.item(item, tags='opened')
                elif 'opened' in tree.item(item, 'tags'):
                    tree.item(item, text=tree.item(item, 'text').replace(NODE_OPEN, NODE_CLOSED, 1))
                    tree.item(item, tags='closed')

        tree = ttk.Treeview(tree_pane, columns=("C1"), show="tree")
        self.tree = tree
        tree.column("#0", width=160, minwidth=60, anchor=W, stretch=NO)
        tree.column("#1", width=30, minwidth=60, anchor=W, stretch=NO)
        tree.heading("C1", text="")
        tree.bind('<Double-Button-1>', on_treeview_click)

        self.add_dummy_data_to_tree(tree)
        self.bind_tree_view_events(tree)
        return tree

    def create_console(self, console_pane):
        console = Text(console_pane, height=20)
        console.insert(END, "Console:\n")
        console.config(state=DISABLED, takefocus=False)
        return console

    def add_dummy_data_to_tree(self, tree):
        from tools import create_dummy_data
        create_dummy_data(tree)

    def bind_tree_view_events(self, tree):
        tree.bind("<Double-Button-1>", self.edit_tree_entry)
        tree.bind("<Return>", self.edit_tree_entry)

    def create_system_and_chat(self, system_pane):
        self.system = Text(system_pane, system_prompt, pady=5)
        self.chat = Text(system_pane)

    def update_window_title(self, event=None):
        progress_title = self.title() + "..."

        def write_title(content):
            if self.is_root_destroyed or self.model.is_canceled:
                return
            current_title = self.title()
            if current_title == progress_title:
                current_title = ""
            self.title(current_title + content)
            self.update()

        self.title(progress_title)
        self.update()
        history = self.history_from_system_and_chat(prompts.TITLE_GENERATION, max_messages=5, max_size=1000) # todo

        self.generation_model.counter.go()
        self.generation_model.chat_complete(history, write_title, max_tokens=30, temperature=0.3)
        print("Title cost:")
        self.generation_model.counter.summarize()

    def configure_max_tokens(self, event=None):
        max_tokens = simpledialog.askinteger(
            "Max Tokens",
            "What should be the model's maximum number of tokens to generate?\n"
            "(Query parameter 'max_tokens')\n",
            initialvalue=self.model.max_tokens.get(),
            minvalue=1, maxvalue=100000)
        if max_tokens:
            self.model.max_tokens.set(max_tokens)

    def configure_temperature(self, event=None):
        temperature = simpledialog.askfloat(
            "Query Temperature",
            "What should be the level of creativity of the model?\n"
            "0.0 for deterministic, typically 0.5 or 0.7, maximal 2.0?\n"
            "(Query parameter 'temperature')\n",
            initialvalue=self.model.temperature.get(),
            minvalue=0, maxvalue=2.0)
        if temperature is not None:
            self.model.temperature.set(temperature)


    def count_text_tokens(self, event=None) :
        txt: Text = self.focus_get()
        try :
            text = txt.get(SEL_FIRST, SEL_LAST)
        except tk.TclError :
            text = txt.get(1.0, END)
        old_status = self.status_bar.message
        self.status_bar.message = "Counting tokens (loading model)"
        self.status_bar.update()
        num_tokens = self.model.counter.count_tokens(text)
        self.status_bar.message = old_status
        num_lines = text.count("\n")
        num_words = len(text.split())
        num_chars = len(text)
        showinfo("Count Tokens",
                 f"The length of the text is:\n"
                 f"{num_tokens} tokens\n"
                 f"{num_lines} lines\n"
                 f"{num_words} words\n"
                 f"{num_chars} characters",
                 master=txt)
        return "break"


    def complete_old(self, n=1, prefix="", postfix=""):
        self.model.is_canceled = False
        txt: Text = self.focus_get()
        txt.tag_remove('cursorline', 1.0, "end")
        with WaitCursor(txt):

            def insert_label(text, symbol, tooltip=""):
                icon = FinishReasonIcon(text, symbol, tooltip=tooltip)
                text.window_create(END, window=icon)

            def scroll():
                if self.scroll_output:
                    txt.see(END)
                txt.update()

            def write_chat(text) :
                if self.is_root_destroyed :
                    return
                txt.insert(END, text, "assistant")
                scroll()


            if not n:
                n = simpledialog.askinteger(
                    "Alternative completions",
                    "How many alternative results do you want?",
                    initialvalue=Thoughttree.multi_completions,
                    minvalue=2, maxvalue=1000)
                if not n:
                    return
                Thoughttree.multi_completions = n
            elif n == -1: # repeat
                n = Thoughttree.multi_completions
            txt.edit_separator()
            if prefix :
                txt.insert(END, prefix)
                scroll()
            history = self.history_from_system_and_chat()

            self.model.counter.go()

            finish_reason, message = 'unknown', ''
            if n == 1:
                if self.model.is_canceled:
                    finish_reason = "canceled"
                else:
                    finish_reason, message = self.model.chat_complete(history, write_chat)
            else:
                frame = tk.Frame(txt)
                txt.window_create(END, window=frame)
                txt.insert(END, "\n")
                txt.see(END)
                finish_reason, message = 'unknown', ''
                for i in range(n):
                    if self.model.is_canceled:
                        finish_reason = "canceled"
                        break
                    label = tk.Label(frame, borderwidth=4, anchor=W, wraplength=txt.winfo_width(),
                                     justify=LEFT, font=Text.FONT, relief=SUNKEN)

                    label.pack(side=TOP, fill=X, expand=True)

                    def write_label(text):
                        if self.is_root_destroyed :
                            return
                        label.config(text=label.cget("text") + text)
                        scroll()

                    if self.model.is_canceled:
                        finish_reason = "canceled"
                        break
                    finish_reason, message = self.model.chat_complete(history, write_label)

            if self.is_root_destroyed:
                return
            if conf.show_finish_reason:
                symbol = Model.finish_reasons[finish_reason]["symbol"]
                if finish_reason not in ["stop", "length", "canceled", "error"] :
                    print(f"{finish_reason=}")
                if symbol :
                    tool_tip = Model.finish_reasons[finish_reason]["tool_tip"]
                    if message:
                        tool_tip += "\n" + message
                    insert_label(txt, symbol, tool_tip)

            if not self.model.is_canceled and not finish_reason == "length":
                txt.insert(END, postfix)
            if self.scroll_output:
                txt.mark_set(INSERT, END)
                txt.see(END)
            txt.edit_separator()

            if conf.ring_bell_after_completion:
                self.bell()

            print("Completion cost:")
            self.model.counter.summarize()

            if conf.update_title_after_completion and not self.model.is_canceled:
                if self.model.counter.tokens_since_go() > Thoughttree.GEN_TITLE_THRESHOLD:
                    self.update_window_title()


    def complete(self, n=1, prefix="", postfix=""):
        self.model.is_canceled = False
        txt: Text = self.focus_get()
        txt.tag_remove('cursorline', 1.0, "end")

        with WaitCursor(txt):
            def insert_label(text, symbol, tooltip=""):
                icon = FinishReasonIcon(text, symbol, tooltip=tooltip)
                text.window_create(END, window=icon)


            def scroll():
                if self.scroll_output:
                    txt.see(END)
                txt.update()


            def write_chat(text):
                if self.is_root_destroyed:
                    return
                txt.insert(END, text, "assistant")
                scroll()


            n = self._process_number_of_completions(n)
            if n is None:
                return

            txt.edit_separator()
            self._insert_prefix_and_scroll(txt, prefix)

            history = self.history_from_system_and_chat()
            self.model.counter.go()

            frame, finish_reason, message = self._process_completions(txt, n, history, write_chat)

            self._handle_completion_finish(txt, finish_reason, message, postfix)
            self._post_completion_tasks()

    def _scroll(self, txt):
        if self.scroll_output:
            txt.see(END)
        txt.update()

    def _process_number_of_completions(self, n):
        if not n:
            n = simpledialog.askinteger(
                "Alternative completions",
                "How many alternative results do you want?",
                initialvalue=Thoughttree.multi_completions,
                minvalue=2, maxvalue=1000)
            if not n:
                return
            Thoughttree.multi_completions = n
        elif n == -1:  # repeat
            n = Thoughttree.multi_completions
        return n


    def _insert_prefix_and_scroll(self, txt, prefix):
        if prefix:
            txt.insert(END, prefix)
            self._scroll(txt)


    def _process_completions(self, txt, n, history, write_chat):
        finish_reason, message = 'unknown', ''
        frame = None
        if n == 1:
            if self.model.is_canceled:
                finish_reason = "canceled"
            else:
                finish_reason, message = self.model.chat_complete(history, write_chat)
        else:
            frame = tk.Frame(txt)
            txt.window_create(END, window=frame)
            txt.insert(END, "\n")
            txt.see(END)
            finish_reason, message = 'unknown', ''
            for i in range(n):
                if self.model.is_canceled:
                    finish_reason = "canceled"
                    break
                label = self._create_label(frame, txt)
                finish_reason, message = self.model.chat_complete(history, self._create_write_label(label, txt))
        return frame, finish_reason, message


    def _create_label(self, frame, txt):
        label = tk.Label(frame, borderwidth=4, anchor=W, wraplength=txt.winfo_width(),
                         justify=LEFT, font=Text.FONT, relief=SUNKEN)
        label.pack(side=TOP, fill=X, expand=True)
        return label


    def _create_write_label(self, label, txt):
        def write_label(text):
            if self.is_root_destroyed:
                return
            label.config(text=label.cget("text") + text)
            self._scroll(txt)

        return write_label


    def _handle_completion_finish(self, txt, finish_reason, message, postfix):
        if self.is_root_destroyed:
            return
        if conf.show_finish_reason:
            self._show_finish_reason(txt, finish_reason, message)
        if not self.model.is_canceled and not finish_reason == "length":
            txt.insert(END, postfix)
        if self.scroll_output:
            txt.mark_set(INSERT, END)
            txt.see(END)
        txt.edit_separator()


    def _show_finish_reason(self, txt, finish_reason, message):
        symbol = Model.finish_reasons[finish_reason]["symbol"]
        if finish_reason not in ["stop", "length", "canceled", "error"]:
            print(f"{finish_reason=}")
        if symbol:
            tool_tip = Model.finish_reasons[finish_reason]["tool_tip"]
            if message:
                tool_tip += "\n" + message
            self._insert_label(txt, symbol, tool_tip)


    def _post_completion_tasks(self):
        if conf.ring_bell_after_completion:
            self.bell()

        print("Completion cost:")
        self.model.counter.summarize()

        if conf.update_title_after_completion and not self.model.is_canceled:
            if self.model.counter.tokens_since_go() > Thoughttree.GEN_TITLE_THRESHOLD:
                self.update_window_title()


    def history_from_system_and_chat(self, additional_message=None, max_messages=None, max_size=None) :
        system = self.system.get(1.0, 'end - 1c').strip()
        history = [{'role': 'system', 'content': system}]

        txt: Text = self.focus_get()
        history = txt.history_from_path(history)

        if additional_message:
            history += [{'role': 'user', 'content': additional_message}]

        if max_messages:
            history = history[-max_messages:]
        return history



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
        txt = tk.Text(self.tree, wrap=WORD, width=w, height=h, font=Text.FONT,
                      highlightthickness=0, highlightbackground="black", padx=4, pady=0)
        txt.insert(END, cur_text)
        txt.place(x=x, y=y)
        txt.focus_set()

        def save_text(event):
            print(event.type)
            if event.type == tk.EventType.FocusOut or int(event.state) & 0x4 == 0 :  # Check if Control key is not pressed
                text = txt.get(1.0, END).strip()
                self.tree.set(row_id, column, text)
                txt.destroy()

        # txt.bind("<FocusOut>", save_text)
        txt.bind("<Return>", lambda e: e.state & 0x4 == 0 and save_text(e) or self.tree.focus_set())
        txt.bind("<Control-Return>", lambda e: txt.insert(INSERT, "\n") or "break")
        # txt.bind("<Control-Key>", lambda e : "break")
        # txt.bind("<Control_L>", lambda e : "break")


    @classmethod
    def main(cls) :
        Thoughttree().mainloop()


if __name__ == "__main__":
    Thoughttree.main()
