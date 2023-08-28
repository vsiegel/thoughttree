#!/usr/bin/env python
import sys
import tkinter as tk
from tkinter import BOTH, END, HORIZONTAL, INSERT, LEFT, SUNKEN, TOP, VERTICAL, W, X, SEL_FIRST, \
    SEL_LAST, BOTTOM
from tkinter import simpledialog
from tkinter.messagebox import showinfo

from configargparse import Namespace

from Console import Console
from FinishReasonIcon import FinishReasonIcon
from FoldablePane import FoldablePane
from GeneratedTitle import GeneratedTitle
from HidableFrame import HidableFrame
from Model import Model
from MultiTextboxLabel import MultiTextboxLabel
from PrimaryUi import PrimaryUi
from StatusBar import StatusBar
from Sheet import Sheet
from MainMenu import MainMenu
from Tree import Tree
from WaitCursor import WaitCursor
from finish_reasons import finish_reasons

WINDOW_ICON = "chatgpt-icon.png"

conf = Namespace()
conf.show_finish_reason = True
conf.update_title_after_completion = True
conf.scroll_output = True
conf.ring_bell_after_completion = False
conf.blinking_caret = True


class Thoughttree(PrimaryUi):
    MIN_SIZE = (600, 300)
    ROOT_GEOMETRY = "1000x600"
    icon = None
    multi_completions = 5

    interactive_model_name = 'gpt-4'
    # interactive_model_name = 'gpt-3.5-turbo'
    generation_model_name = 'gpt-3.5-turbo'


    def __init__(self):
        PrimaryUi.__init__(self, "Thoughttree", WINDOW_ICON)
        self.previous_current_sheet = None
        self.status_hider = None
        self.status = None
        self.console = None
        self.tree = None
        self.system = None
        self.chat = None
        self.model = None
        self.console_pane = None
        self.tree_pane = None
        self.system_pane = None

        self.root.geometry(Thoughttree.ROOT_GEOMETRY)
        self.root.minsize(*Thoughttree.MIN_SIZE)
        try:
            self.set_icon(self.WINDOW_ICON)
        except:
            print("Error loading icon.")

        self.scroll_output = conf.scroll_output
        self.ring_bell_after_completion = conf.ring_bell_after_completion
        self.create_ui()

        def new_window_callback():
            Thoughttree()
        self.models = {}
        self.generation_model = Model(self.generation_model_name)
        self.set_model(self.interactive_model_name)
        menu = MainMenu(self, new_window_callback)

        self.pack(fill=BOTH, expand=True)
        self.status.note = "Loading available models..."
        self.update_idletasks()
        menu.models_menu.load_available_models()
        self.status.note = ""

        if self.first_window:
            self.root.mainloop()


    def set_model(self, model_name):
        if not model_name in self.models:
            self.models[model_name] = Model(model_name)
        self.model = self.models[model_name]

        self.status.model = model_name
        self.status.set_max_token_var(self.model.max_tokens)
        self.status.set_temperature_var(self.model.temperature)

    def cancel_models(self, event=None):
        for model in self.models.values():
            model.cancel()

    def create_ui(self):
        self.configure_ui_options()

        self.status_hider = HidableFrame(self)
        self.status_hider.pack(side=BOTTOM, fill=X, expand=False)
        self.status = StatusBar(self.status_hider)
        self.status.pack(side=BOTTOM, fill=X, expand=True)

        self.console_pane = FoldablePane(self, orient=VERTICAL)
        self.tree_pane = FoldablePane(self.console_pane, orient=HORIZONTAL)
        self.system_pane = FoldablePane(self.tree_pane, orient=VERTICAL)
        self.console_pane.pack(side=TOP, fill=BOTH, expand=True)

        self.console = Console(self.console_pane)
        self.tree = Tree(self.tree_pane)
        self.system = Sheet(self.system_pane, height=3)
        self.chat = Sheet(self.system_pane)

        self.console_pane.add(self.tree_pane, stretch="always")
        self.console_pane.addFoldable(self.console, stretch="never")
        self.tree_pane.addFoldable(self.tree, stretch="never")
        self.tree_pane.add(self.system_pane, stretch="always")
        self.system_pane.addFoldable(self.system, stretch="never")
        self.system_pane.add(self.chat, stretch="always")

        def on_first_configure(ev=None):
            self.system_pane.fold(set_folded=True)
            self.console_pane.fold(set_folded=True)
            self.tree_pane.fold(set_folded=True)
            self.console_pane.unbind("<Configure>")
        self.console_pane.bind("<Configure>", on_first_configure)

        sys.stdout = self.console
        sys.stderr = self.console.err

        self.chat.focus_set()


    def configure_ui_options(self):
        self.option_add('*Dialog*Font', ("sans-serif", 10))
        self.option_add('*Menu*Font', ("Arial", 10))
        self.option_add('*Font', ("Arial", 10))
        if not conf.blinking_caret:
            self.option_add('*Text*insertOffTime', '0')


    def update_window_title(self, event=None):
        progress_title = self.root.title() + "..."

        def write_title(content):
            if self.is_root_destroyed or self.model.is_canceled:
                return
            current_title = self.root.title()
            if current_title == progress_title:
                current_title = ""
            self.root.title(current_title + content)
            self.update()

        self.root.title(progress_title)
        self.update()
        history = self.history_from_system_and_chat(GeneratedTitle.PROMPT, max_messages=5, max_size=1000) # todo limit, do not use system for title

        self.generation_model.counter.go()
        self.generation_model.chat_complete(history, write_title, max_tokens=30, temperature=0.3)
        self.generation_model.counter.summarize("Title cost:")


    def configure_parameter(self, title, message, variable, minvalue, maxvalue):
        askfunction = simpledialog.askinteger if isinstance(variable, tk.IntVar) else simpledialog.askfloat
        value = askfunction(
            title,
            message,
            initialvalue=variable.get(),
            minvalue=minvalue,
            maxvalue=maxvalue)
        if value is not None:
            variable.set(value)


    def configure_max_tokens(self, event=None):
        self.configure_parameter(
            "Max Tokens",
            "What should be the model's maximum number of tokens to generate?\n"
            "(Query parameter 'max_tokens')\n",
            self.model.max_tokens,
            1,
            100000)


    def configure_temperature(self, event=None):
        self.configure_parameter(
            "Query Temperature",
            "What should be the level of creativity of the model?\n"
            "0.0 for deterministic, typically 0.5 or 0.7, maximal 2.0?\n"
            "(Query parameter 'temperature')\n",
            self.model.temperature,
            0,
            2.0)


    def count_text_tokens(self, event=None) :
        sheet = self.current_sheet()
        try :
            text = sheet.get(SEL_FIRST, SEL_LAST)
        except tk.TclError :
            text = sheet.get(1.0, END)
        old_status = self.status.message
        self.status.message = "Counting tokens (loading model)"
        self.status.update()
        num_tokens = self.model.counter.count_tokens(text)
        self.status.message = old_status
        num_lines = text.count("\n")
        num_words = len(text.split())
        num_chars = len(text)
        # todo: align numbers, using TextDialog or so
        showinfo("Count Tokens",
                 f"The length of the text is:\n"
                 f"{num_tokens:,} tokens\n"
                 f"{num_lines:,} lines\n"
                 f"{num_words:,} words\n"
                 f"{num_chars:,} characters",
                 master=sheet)
        return "break"


    def complete(self, n=1, prefix="", postfix=""):
        self.model.is_canceled = False
        sheet = self.current_sheet()
        sheet.tag_remove('cursorline', 1.0, "end")

        n = self.find_number_of_completions(n)
        if n is None:
            return

        with WaitCursor(sheet):
            sheet.undo_separator()
            self._insert_prefix_and_scroll(sheet, prefix)

            history = self.history_from_system_and_chat()
            self.model.counter.go()

            finish_reason, message = self._process_completions(sheet, n, history)

            self._handle_completion_finish(sheet, finish_reason, message, postfix)
            self._post_completion_tasks()
        return "break"


    def current_sheet(self) -> Sheet:
        focussed_widget = self.focus_get()
        if isinstance(focussed_widget, Sheet):
            self.previous_current_sheet = focussed_widget
            return focussed_widget
        else:
            return self.previous_current_sheet


    def scroll(self, sheet):
        if self.scroll_output:
            sheet.see(END)
        sheet.update()


    def find_number_of_completions(self, n):
        if not n:
            n = simpledialog.askinteger(
                "Alternative completions",
                "How many alternative results do you want?",
                initialvalue=Thoughttree.multi_completions,
                minvalue=2, maxvalue=1000, parent=self)
            if not n:
                return
        elif n == -1:  # repeat
            n = Thoughttree.multi_completions
        Thoughttree.multi_completions = n
        return n


    def _insert_prefix_and_scroll(self, sheet, prefix):
        if prefix:
            sheet.insert(END, prefix)
            self.scroll(sheet)


    def _process_completions(self, sheet, n, history):
        finish_reason, message = 'unknown', ''
        label_frame = None
        if n == 1:
            if self.model.is_canceled:
                finish_reason = "canceled"
            else:
                def write_chat(text):
                    if self.is_root_destroyed:
                        return
                    sheet.insert(END, text, "assistant")
                    self.scroll(sheet)

                finish_reason, message = self.model.chat_complete(history, write_chat)
        else:
            label_frame = tk.Frame(sheet, borderwidth=4)
            sheet.window_create(END, window=label_frame)
            sheet.insert(END, "\n")
            sheet.see(END)
            finish_reason, message = 'unknown', ''

            for i in range(n):
                if self.model.is_canceled:
                    finish_reason = "canceled"
                    break
                label = MultiTextboxLabel(label_frame, sheet)

                def write_label(text):
                    if self.is_root_destroyed:
                        return
                    label.config(text=label.cget("text") + text)
                    self.scroll(sheet)

                finish_reason, message = self.model.chat_complete(history, write_label)
        return finish_reason, message


    def _handle_completion_finish(self, sheet, finish_reason, message, postfix):
        if self.is_root_destroyed:
            return
        if conf.show_finish_reason:
            self.show_finish_reason_icon(sheet, finish_reason, message)
        if not self.model.is_canceled and not finish_reason == "length":
            sheet.insert(END, postfix)
        if self.scroll_output:
            sheet.mark_set(INSERT, END)
            sheet.see(END)
        sheet.undo_separator()


    def show_finish_reason_icon(self, sheet, finish_reason, message):
        symbol = finish_reasons[finish_reason]["symbol"]
        if finish_reason not in ["stop", "length", "canceled", "error"]:
            print(f"{finish_reason=}")
        if symbol:
            tooltip = finish_reasons[finish_reason]["tooltip"]
            if message:
                tooltip += "\n" + message

            sheet.window_create(END, window=FinishReasonIcon(sheet, symbol, tooltip=tooltip))


    def _post_completion_tasks(self):
        if conf.ring_bell_after_completion:
            self.bell()

        self.model.counter.summarize("Completion cost:")

        if conf.update_title_after_completion and not self.model.is_canceled:
            if self.model.counter.tokens_since_go() > GeneratedTitle.GEN_THRESHOLD:
                self.update_window_title()


    def history_from_system_and_chat(self, additional_message=None, max_messages=None, max_size=None) :
        system = self.system.get(1.0, 'end - 1c').strip()
        history = [{'role': 'system', 'content': system}]

        history = self.current_sheet().history_from_path(history)

        if additional_message:
            history += [{'role': 'user', 'content': additional_message}]

        if max_messages:
            history = history[-max_messages:]
        return history


if __name__ == "__main__":
    Thoughttree()
