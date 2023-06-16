#!/usr/bin/env python
import os
import tkinter as tk
from tkinter import ttk, simpledialog
from tkinter import font as tkfont
from tkinter.messagebox import showinfo

from configargparse import ArgumentParser, Namespace

import prompts
from Model import Model
from ThoughttreeMenu import ThoughttreeMenu
from ToolTip import ToolTip
from StatusBar import StatusBar
from Menu import Menu
from Text import Text
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
    CHAT_WIDTH = 400
    ROOT_GEOMETRY = "1000x600"
    GEN_TITLE_THRESHOLD = 20
    icon = None
    multi_completions = 5

    # self.model_name = 'gpt-4'
    model_name = 'gpt-3.5-turbo'
    generation_model_name = 'gpt-3.5-turbo'


    def __init__(self):
        UI.__init__(self, "Thoughttree", WINDOW_ICON)
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
        self.config(menu=ThoughttreeMenu(self, new_window_callback))



    def set_model(self, model_name):
        if not model_name in self.models:
            self.models[model_name] = Model(model_name)
        self.model = self.models[model_name]
        self.status_bar.model = model_name
        self.status_bar.message = f"Max tokens: {self.model.max_tokens} T: {self.model.temperature}"

    def cancelModels(self, event=None):
        for model in self.models.values():
            model.cancel()

    def create_ui(self):

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

        self.option_add('*Dialog*Font', ("sans-serif", 10))
        self.option_add('*Menu*Font', ("Arial", 10))
        self.option_add('*Font', ("Arial", 10))
        if not conf.blinking_caret:
            self.option_add('*Text*insertOffTime', '0')

        font_height = tkfont.Font(font=Text.FONT).metrics("linespace")
        style = ttk.Style(self)

        style.configure("Treeview", rowheight=2 * font_height + 0)
        # style.configure("Treeview", font=Text.TEXT_FONT)
        style.configure("Treeview.Cell", anchor=tk.NW)
        style.configure("Treeview.Cell", padding=(1, 1))

        self.status_bar = StatusBar(self)

        SASHWIDTH = 8
        tree_and_main_pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=SASHWIDTH, sashrelief=tk.RIDGE)
        tree_and_main_pane.pack(fill=tk.BOTH, expand=True)
        system_and_chat_pane = tk.PanedWindow(tree_and_main_pane, orient=tk.VERTICAL, sashwidth=SASHWIDTH, sashrelief=tk.RIDGE)

        tree = ttk.Treeview(tree_and_main_pane, columns=("C1"), show="tree")
        self.tree = tree
        tree.column("#0", width=160, minwidth=60, anchor=tk.W, stretch=tk.NO)
        tree.column("#1", width=30, minwidth=60, anchor=tk.W, stretch=tk.NO)
        tree.heading("C1", text="")

        tree.bind('<Double-Button-1>', on_treeview_click)
        tree.bind_class("Treeview", "<KeyPress-Return>", lambda _: None)
        tree.bind_class("Treeview", "<KeyRelease-Return>", lambda _: None)
        from tools import create_dummy_data
        create_dummy_data(tree)

        tree_and_main_pane.add(tree)
        tree_and_main_pane.add(system_and_chat_pane)
        tree_and_main_pane.sash_place(0, 0, 0)

        self.tree_and_main_pane_old_sash = (160, 160)
        self.system_and_chat_pane_old_sash = (20, 20)

        self.tree_and_main_pane = tree_and_main_pane
        self.system_and_chat_pane = system_and_chat_pane

        children = tree.get_children()
        if children:
            tree.focus(children[0])
        tree.bind("<Double-Button-1>", self.edit_tree_entry)
        tree.bind("<Return>", self.edit_tree_entry)

        self.system = Text(system_and_chat_pane, system_prompt)
        self.chat = Text(system_and_chat_pane)
        self.system.config(pady=5)

        system_and_chat_pane.add(self.system)
        system_and_chat_pane.add(self.chat)

        self.chat.focus_set()

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
        history = self.history_from_system_and_chat(prompts.TITLE_GENERATION_PROMPT, maxMessages=5)

        self.generation_model.counter.go()
        self.generation_model.chat_complete(history, write_title, max_tokens=30, temperature=0.3)
        print("Title cost:")
        self.generation_model.counter.summarize()



    def configure_temperature(self):
        temperature = simpledialog.askfloat(
            "Query Temperature",
            "What should be the level of creativity of the model?\n"
            "0.0 for deterministic, typically 0.5 or 0.7, maximal 2.0?\n"
            "(Query parameter 'temperature')\n",
            initialvalue=self.model.temperature,
            minvalue=0, maxvalue=2.0)
        if temperature == None:
            return
        self.model.temperature = temperature

    def configure_max_tokens(self):
        max_tokens = simpledialog.askinteger(
            "Max Tokens",
            "What should be the model's maximum number of tokens to generate?\n"
            "(Query parameter 'max_tokens')\n",
            initialvalue=self.model.max_tokens,
            minvalue=1, maxvalue=100000)
        if not max_tokens:
            return
        self.model.max_tokens = max_tokens

    def count_text_tokens(self, event=None) :
        txt: Text = self.focus_get()
        try :
            text = txt.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError :
            text = txt.get(1.0, tk.END)
        old_status = self.status_bar.message
        self.status_bar.message = "Counting tokens (loading model)"
        num_tokens = self.model.counter.count_tokens(text)
        num_lines = text.count("\n")
        num_words = len(text.split())
        num_chars = len(text)
        self.status_bar.message = old_status
        showinfo("Count Tokens",
                 f"The length of the text is:\n"
                 f"{num_tokens} tokens\n"
                 f"{num_lines} lines\n"
                 f"{num_words} words\n"
                 f"{num_chars} characters",
                 master=txt)
        return "break"


    def complete(self, n=1, prefix="", postfix=""):
        self.model.is_canceled = False
        txt: Text = self.focus_get()
        txt.tag_remove('cursorline', 1.0, "end")
        if self.scroll_output:
            txt.see(tk.END)
        with WaitCursor(txt):

            def insert_label(txt, text, tool_tip=""):
                label = tk.Label(txt, text=text, padx=7, pady=0, bg="#F0F0F0", fg="grey", borderwidth=0)
                if tool_tip:
                    ToolTip(label, tool_tip)
                txt.window_create(tk.END, window=label)

            def write_chat(text) :
                if self.is_root_destroyed :
                    return
                txt.insert(tk.END, text, "assistant")
                if self.scroll_output:
                    txt.see(tk.END)
                txt.update()

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
                txt.insert(tk.END, prefix)
                txt.update()
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
                txt.window_create(tk.END, window=frame)
                txt.insert(tk.END, "\n")
                txt.see(tk.END)
                finish_reason, message = 'unknown', ''
                for i in range(n):
                    if self.model.is_canceled:
                        finish_reason = "canceled"
                        break
                    label = tk.Label(frame, borderwidth=4, anchor=tk.W, wraplength=txt.winfo_width(),
                                     justify=tk.LEFT, font=Text.FONT, relief=tk.SUNKEN)

                    label.pack(side=tk.TOP, fill=tk.X, expand=True)

                    def write_label(text):
                        if self.is_root_destroyed :
                            return
                        label.config(text=label.cget("text") + text)
                        if self.scroll_output:
                            txt.see(tk.END)
                        txt.update()

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

            if not self.model.is_canceled:
                txt.insert(tk.END, postfix)
            if self.scroll_output:
                txt.mark_set(tk.INSERT, tk.END)
                txt.see(tk.END)
            txt.edit_separator()

            if conf.ring_bell_after_completion:
                self.bell()

            print("Completion cost:")
            self.model.counter.summarize()

            if conf.update_title_after_completion:
                if self.model.counter.tokens_since_go() > Thoughttree.GEN_TITLE_THRESHOLD:
                    self.update_window_title()


    def history_from_system_and_chat(self, additional_message=None, maxMessages=0) :
        txt: Text = self.focus_get()
        system = self.system.get(1.0, 'end - 1c').strip()
        history = [{'role': 'system', 'content': system}]

        history = txt.history_from_path(history)

        if additional_message:
            history += [{'role': 'user', 'content': additional_message}]

        if maxMessages:
            history = history[-maxMessages:]
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
        Thoughttree().mainloop()


if __name__ == "__main__":
    Thoughttree.main()
