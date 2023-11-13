#!/usr/bin/env python3
import sys
import tkinter as tk
from datetime import datetime
from textwrap import dedent
from tkinter import BOTH, END, HORIZONTAL, INSERT, LEFT, SUNKEN, TOP, VERTICAL, W, X, SEL_FIRST, \
    SEL_LAST, BOTTOM, RAISED, GROOVE
from tkinter import simpledialog
from tkinter.messagebox import showinfo

from configargparse import Namespace

from Console import Console
from FinishReasonIcon import FinishReasonIcon
from FoldablePane import FoldablePane
from ForkableSheet import ForkableSheet
from History import History
from InsertionIcon import InsertionIcon
from Keys import Keys
from SheetTree import SheetTree
from InitialSheetHelp import InitialSheetHelp
from TextIOTee import TextIOTee
from Title import Title
from HidableFrame import HidableFrame
from Model import Model
from AlternativeLabel import AlternativeLabel
from StatusBar import StatusBar
from Sheet import Sheet, OUTPUT
from MainMenu import MainMenu
from Tree import Tree
from Ui import Ui
from WaitCursor import WaitCursor
from finish_reasons import finish_reasons
from tools import log_motion_on_ctrl_alt

WINDOW_ICON = "chatgpt-icon.png"

conf = Namespace()
conf.show_finish_reason = True
conf.update_title_after_completion = True
conf.scroll_output = True
conf.ring_bell_after_completion = True
conf.log_messages_to_console = True
conf.ring_bell_only_after = 15
conf.blinking_caret = True
# conf.chat_completion_request_timeout = 5
conf.location_marker = "@"
conf.debug = True

class Thoughttree(Ui):
    MIN_SIZE = (600, 300)
    ROOT_GEOMETRY = "1000x500"
    icon = None
    multi_completions = 5

    interactive_model_name = 'gpt-4'
    # interactive_model_name = 'gpt-3.5-turbo'
    generation_model_name = 'gpt-3.5-turbo'


    def __init__(self):
        Ui.__init__(self, title="Thoughttree", name="tt", icon_path=WINDOW_ICON, closeable=False)
        self.show_hidden_prompts = None
        self.current_sheet: ForkableSheet|None = None
        self.status_hider = None
        self.status = None
        self.console = None
        self.tree = None
        self.system: Sheet|None = None
        self.chat_sheet = None
        self.model = None
        self.console_pane = None
        self.tree_pane = None
        self.system_pane = None

        # def on_configure(event):
        #     print(f"Event: {event}: {event.widget} {event.x},{event.y} {event.width}x{event.height}")
        # self.bind_all('<Configure>', on_configure)

        self.root.geometry(Thoughttree.ROOT_GEOMETRY)
        self.root.minsize(*Thoughttree.MIN_SIZE)
        try:
            self.set_icon(self.WINDOW_ICON)
        except:
            print("Error loading icon.")

        self.scroll_output = conf.scroll_output
        self.ring_bell_after_completion = conf.ring_bell_after_completion
        self.log_messages_to_console = conf.log_messages_to_console
        self.create_ui()

        self.models = {}
        self.generation_model = Model(self.generation_model_name)
        self.set_model(self.interactive_model_name)
        Title.initialize()

        self.pack(fill=BOTH, expand=True)
        self.status.note = "Loading available models..."
        self.update_idletasks()
        n = self.menu.models_menu.load_available_models()
        self.status.note = f"{n} models found."

        if conf.debug:
            log_motion_on_ctrl_alt(self)

        if self.main_window:
            self.root.mainloop()


    def set_model(self, model_name):
        model_name = model_name.rsplit()[-1]
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

        self.menu = MainMenu(self)
        self.menu.pack(side=TOP, fill=X, expand=False)

        self.status_hider = HidableFrame(self)
        self.status_hider.pack(side=BOTTOM, fill=X, expand=False)
        self.status = StatusBar(self.status_hider)
        self.status.pack(side=BOTTOM, fill=X, expand=True)

        self.console_pane = FoldablePane(self, orient=VERTICAL)
        self.tree_pane = FoldablePane(self.console_pane, orient=HORIZONTAL)
        self.system_pane = FoldablePane(self.tree_pane, orient=VERTICAL)
        self.console_pane.pack(side=TOP, fill=BOTH, expand=True)

        if self.main_window:
            self.console = Console(self.console_pane)
        self.tree = Tree(self.tree_pane)
        self.system = Sheet(self.system_pane, height=3)
        # self.chat_sheet = Sheet(self.system_pane)
        self.chat_sheet = SheetTree(self.system_pane)
        self.current_sheet: ForkableSheet = self.chat_sheet.forkable_sheet

        self.console_pane.add(self.tree_pane, stretch="always")
        if self.main_window:
            self.console_pane.addFoldable(self.console, stretch="never")
        self.tree_pane.addFoldable(self.tree, stretch="never")
        self.tree_pane.add(self.system_pane, stretch="always")
        self.system_pane.addFoldable(self.system, stretch="never")
        self.system_pane.add(self.chat_sheet, stretch="always")

        if self.main_window:
            if type(sys.stdout) is not TextIOTee:
                sys.stdout = TextIOTee(sys.stdout, self.console.out)
            if type(sys.stderr) is not TextIOTee:
                sys.stderr = TextIOTee(sys.stderr, self.console.err)

        self.menu.create_menu()


        def on_first_configure(ev=None):
            self.system_pane.fold(set_folded=False)
            self.console_pane.fold(set_folded=True)
            self.tree_pane.fold(set_folded=True)
            self.console_pane.unbind("<Configure>")
        self.console_pane.bind("<Configure>", on_first_configure)

        self.chat_sheet.focus_set()

        InitialSheetHelp(self.system, "System prompt - [?]",
                  "Enter a system prompt for ChatGPT in this text box. This prompt will guide the model's responses."
                  " For instance, if you want the model to speak like Shakespeare, you could use a prompt like"
                  " 'You are an AI trained in the style of Shakespeare.' Be as specific as possible to get the best results.")
        InitialSheetHelp(self.chat_sheet.forkable_sheet, "User prompt - Chat - [?]",
                  "In this text box, you need to input your general prompt for ChatGPT. This is essentially your conversation"
                  " starter or question, which will guide the AI model's responses. For example, if you want to write a story,"
                  " your prompt could be 'Once upon a time in a kingdom far away...'. If you're looking for answers to a specific"
                  " question, simply type your question here, such as 'What is the process of photosynthesis?'. Remember, the more"
                  " specific and detailed your prompt, the more accurate and helpful the model's response will be. This can include"
                  " setting a context, defining a role, or asking a question. Don't hesitate to experiment with different types"
                  " of prompts to see the various responses!")


    def configure_ui_options(self):
        self.option_add('*Dialog*Font', ("sans-serif", 10))
        self.option_add('*Menu*Font', ("Arial", 10))
        self.option_add('*Font', ("Arial", 10))
        if not conf.blinking_caret:
            self.option_add('*Text*insertOffTime', '0')

    def is_initially_modified(self):
        return self.chat_sheet.forkable_sheet.initially_modified or self.system.initially_modified

    def update_window_title(self, event=None):
        progress_title = self.root.title().rstrip('.') + "..."

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
        history = self.history_from_system_and_chat(Title.PROMPT, max_messages=5, max_size=1000) # todo limit, do not use system for title

        self.generation_model.counter.go()
        self.generation_model.complete(history, write_title, max_tokens=30, temperature=0.3)
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
        sheet = self.it
        try :
            text = sheet.get(SEL_FIRST, SEL_LAST)
        except tk.TclError :
            text = sheet.get(1.0, END)
        old_status = self.status.message
        self.status.message = "Counting tokens (loading model)..."
        self.status.update()
        num_tokens = self.model.counter.count_tokens(text)
        self.status.message = old_status
        num_lines = text.count("\n")
        num_words = len(text.split())
        num_chars = len(text)
        # todo: align numbers, using TextDialog or so
        showinfo("Count Tokens",
                 f"The length of this section is:\n"
                 f"{num_tokens:,} tokens\n"
                 f"{num_lines:,} lines\n"
                 f"{num_words:,} words\n"
                 f"{num_chars:,} characters",
                 master=sheet)
        return "break"


    def chat(self, n=1, prefix="", postfix="", inline=False, insert=False, replace=False, location=False, hidden_prompt=None):
        inline = inline or insert or replace
        self.model.is_canceled = False
        sheet = self.it
        sheet.tag_remove('cursorline', 1.0, "end")

        n = self.find_number_of_completions(n)
        if n is None:
            return

        with WaitCursor(sheet):
            sheet.undo_separator()
            start_time = datetime.now()
            sheet.mark_set(OUTPUT, inline and INSERT or "end-1c") # todo
            if not inline:
                self.set_up(sheet, prefix)
            if insert:
                self.set_up_inline_completion(sheet)
            elif location:
                self.set_up_location_reference(sheet)
            elif replace:
                self.set_up_replace_completion(sheet)

            history = self.history_from_system_and_chat(additional_message=hidden_prompt)
            self.remove_hidden_prompt(sheet)
            self.model.counter.go()

            reason, message = self.completions(sheet, n, history)

            self.finish_completion(sheet, reason, message, postfix, inline)
            self.post_completion_tasks(start_time)
        return "break"

    def ask(self, event=None):
        question_box = Sheet(relief=SUNKEN, borderwidth=3, background="lightgray", width=10)

        self.it.window_create(INSERT, window=question_box, stretch=1)

    def set_up_inline_completion(self, sheet, specific=""):
        inline_completion_marker = dedent(
            f"""
            Do an insertion completion:
            Complete assuming the insertion cursor for the text is at the character "{conf.location_marker}".
            Assume that the trailing text will be there after the completion.
            Do not use the mark character in the completion.
            The part before and after the mark is already present for the user,
            only produce text that should be in between.
            Do not overlap output and following text, the end of the output should not be the same as the start of the trailing existing text.
            The marker itself will be removed.
            Take care to add the right amount of spaces before and after the marker.
            For example, add a trailing space if the insertion is a word, and the next char after the mark is a space.
            The completion needs to make sense before the following text, so it can not be the same normally.
            Make sure there is no repetition.The inserted text should not be the same as the text after the insertion.
            {specific}
            """)
        self.system.hide(END, inline_completion_marker)
        sheet.hide(INSERT, conf.location_marker)

    def set_up_location_reference(self, sheet, specific=""):
        inline_completion_marker = dedent(
            f"""
            When the prompt refers to a location or marker in the text, it is the position of "{conf.location_marker}".
            Do not refer to that character in the output.
            Ignore the character for all other purposes.
            For example, for a marker X and input "foo baXr baz", the word "here" is "bar" (not "baXr").
            Never literally mention the marker, it is automatically hidden from the user.
            {specific}
            """)
        self.system.hide(END, inline_completion_marker)
        sheet.hide(INSERT, conf.location_marker)


    def set_up_replace_completion(self, sheet):
        replace_completion_marker = dedent(
            f"""
            Do an replacement completion:The output will replace the users text selection, which is 
            the part of text between the two "{conf.location_marker}". 
            Complete assuming the insertion cursor for the text is at the first marker "{conf.location_marker}".
            Produce text that will replace the text between the start marker and the end marker.
            The text after the end marker will still be there after the completion.
            Do not use the markers in the completion. The markers will be removed from the text after completion.
            The part before start marker and after the end marker is already present for the user,
            only produce text that should be in between.
            Do not overlap output and following text.
            The markers themselves will be removed.
            Take care to add the right amount of spaces after the start marker and before the end marker.
            """)
        self.system.hide(END, replace_completion_marker)
        sheet.hide(SEL_FIRST, conf.location_marker)
        sheet.hide(SEL_LAST,  conf.location_marker)

    def remove_hidden_prompt(self, sheet):
        sheet.remove_tag('hidden_prompt')
        self.system.remove_tag('hidden_prompt')

    @property
    def it(self) -> Sheet:
        focussed = self.focus_get()
        print()
        if isinstance(focussed, Sheet):
            self.current_sheet = focussed
        return self.current_sheet


    def scroll(self, sheet, to=OUTPUT):
        if self.scroll_output:
            sheet.see(to)
        sheet.update() # todo: Needed?


    def find_number_of_completions(self, n):
        if not n:
            n = simpledialog.askinteger(
                "Alternative completions",
                "How many alternative results do you want?",
                initialvalue=Thoughttree.multi_completions,
                minvalue=2, maxvalue=1000, parent=self)
            if not n:
                return None
            Thoughttree.multi_completions = n
        elif n == -1:  # repeat
            n = Thoughttree.multi_completions
        return n


    def set_up(self, sheet, prefix):
        if prefix:
            sheet.insert(OUTPUT, prefix)
            self.scroll(sheet)


    def completions(self, sheet, n, history):
        reason, message = 'unknown', ''

        # sheet.mark_set(OUTPUT, inline and INSERT or "end-2c")
        sheet.mark_set("completion_start", OUTPUT)

        alternatives_frame = None

        def write_stdout(text, *args):
            if self.is_root_destroyed:
                return
            print(text)
            self.scroll(sheet)

        def write_sheet(text, written_sheet: Sheet):
            if self.is_root_destroyed:
                return
            written_sheet.insert(OUTPUT, text, ("assistant", "model-" + self.model.name))
            self.scroll(sheet)

        def write_label(text, label=None):
            if self.is_root_destroyed:
                return
            label.config(text=label.cget("text") + text)
            self.scroll(sheet)


        for i in range(n):
            if self.model.is_canceled:
                reason = "canceled"
                break
            if n > 1 and i == 0:
                alternatives_frame = tk.Frame(sheet, borderwidth=4, relief=GROOVE)
                title = tk.Label(alternatives_frame, text=f"Alternatives ({n})")
                title.pack(side=tk.TOP, anchor=tk.W)
                sheet.insert(OUTPUT, "\n")
                sheet.window_create(OUTPUT, window=alternatives_frame)
                sheet.see(OUTPUT)

            if alternatives_frame:
                label = AlternativeLabel(alternatives_frame, sheet)
                reason, message = self.model.complete(history, lambda text: write_label(text, label))
            else:
                with InsertionIcon(sheet, OUTPUT):
                    reason, message = self.model.complete(history, lambda text: write_sheet(text, sheet))

        sheet.mark_set("completion_end", OUTPUT)
        return reason, message



    def finish_completion(self, sheet, finish_reason, message, postfix, inline):
        if self.is_root_destroyed:
            return
        if conf.show_finish_reason:
            self.show_finish_reason_icon(sheet, finish_reason, message)
        if not self.model.is_canceled and not finish_reason == "length":
            sheet.insert(OUTPUT, postfix)
        if self.scroll_output:
            if not inline:
                sheet.mark_set(OUTPUT, END)
            sheet.see(OUTPUT)
        sheet.undo_separator()


    def show_finish_reason_icon(self, sheet, finish_reason, message):
        symbol = finish_reasons[finish_reason]["symbol"]
        if finish_reason not in ["stop", "length", "canceled", "error"]:
            print(f"{finish_reason=}")
        if symbol:
            tooltip = finish_reasons[finish_reason]["tooltip"]
            if message:
                tooltip += "\n" + message

            sheet.window_create(OUTPUT, window=FinishReasonIcon(sheet, symbol, tooltip=tooltip))


    def post_completion_tasks(self, start_time):
        if self.ring_bell_after_completion:
            if datetime.now().timestamp() - start_time.timestamp() > conf.ring_bell_only_after:
                self.bell()

        self.model.counter.summarize("Completion cost:")

        if conf.update_title_after_completion and not self.model.is_canceled:
            self.update_window_title()


    def history_from_system_and_chat(self, additional_message=None, additional_system=None, max_messages=0, max_size=None) :
        system = self.system.get(1.0, 'end - 1c').strip()
        history = History(system)

        if self.it == self.system:
            print(f"{self.it=}")
            self.system.tk_focusNext().focus()
            print(f"{self.it=}")
        history = self.it.history_from_path(history)

        history.system(additional_system)
        history.user(additional_message)
        history.limit(messages=max_messages)
        return history

    def toggle_show_hidden_prompts(self, event=None):
        hidden = bool(int(self.system.tag_cget('hidden_prompt', 'elide')))
        for sheet in [self.system, self.it]:
            sheet.tag_config("hidden_prompt", elide=not hidden)

if __name__ == "__main__":
    Thoughttree()

