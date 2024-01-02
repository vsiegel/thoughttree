#!/usr/bin/env python3
import sys
import tkinter as tk
from datetime import datetime
from textwrap import dedent
from tkinter import BOTH, END, HORIZONTAL, INSERT, LEFT, SUNKEN, TOP, VERTICAL, W, X, SEL_FIRST, \
    SEL_LAST, BOTTOM, RAISED, GROOVE, NONE, DISABLED
from tkinter import simpledialog
from tkinter.messagebox import showinfo

from configargparse import Namespace
import Colors
from Console import Console
from FinishReasonIcon import FinishReasonIcon
from FoldablePane import FoldablePane
from ForkableSheet import ForkableSheet
from History import History
from InsertionIcon import InsertionIcon
from Keys import Keys
from SheetTree import SheetTree
from InitialSheetHelp import InitialSheetHelp
from Improvement import Improvement
from TextIOTee import TextIOTee
from Title import Title
from HidableFrame import HidableFrame
from Model import Model
from AlternativeLabel import AlternativeSheet
from StatusBar import StatusBar
from Sheet import Sheet, OUTPUT
from MainMenu import MainMenu
from Tree import Tree
from Ui import Ui
from WaitCursor import WaitCursor
from finish_reasons import finish_reasons
from sheet_help_texts import sheet_help
from tools import log_motion_on_ctrl_alt, screenshot_after_input

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
    ROOT_GEOMETRY = "1300x750"
    icon = None
    multi_completions = 5

    interactive_model_name = 'gpt-4'
    # interactive_model_name = 'gpt-3.5-turbo'
    generation_model_name = 'gpt-3.5-turbo'


    def __init__(self, argv=None):
        Ui.__init__(self, title="Thoughttree", name="tt", icon_path=WINDOW_ICON, closeable=False)
        self.show_hidden_prompts = None
        self.current_sheet: ForkableSheet|None = None
        self.status_hider = None
        self.status = None
        self.console = None
        self.tree = None
        self.detail: Sheet = None
        self.system: Sheet|None = None
        self.sheet_tree = None
        self.model = None
        self.console_pane = None
        self.tree_pane = None
        self.detail_pane = None
        self.system_pane = None

        # def on_configure(event):
        #     print(f"Event: {event}: {event.widget} {event.x},{event.y} {event.width}x{event.height}")
        # self.bind_all('<Configure>', on_configure)

        if argv and "-geometry" in argv:
            geometry = argv[argv.index("-geometry") + 1]
            if geometry.startswith('+'):
                geometry = Thoughttree.ROOT_GEOMETRY + geometry
            print(f"{geometry=}")
        else:
            geometry = Thoughttree.ROOT_GEOMETRY
        self.root.geometry(geometry)
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
        self.status.note = f"OpenAI: {n} models found."

        if conf.debug:
            def log_heights(e):
                w: tk.Widget = e.widget
                print(f"{e.height=} {w.winfo_height()=} {w.winfo_reqheight()=} {w.cget('height')=} {e.widget}")
            log_motion_on_ctrl_alt(self, log_heights)
            # screenshot_after_input(self, "thoughttree")

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

        self.console_pane = FoldablePane(self, orient=VERTICAL, name="cp")
        self.tree_pane = FoldablePane(self.console_pane, orient=HORIZONTAL, name="tp", fold_size=500)
        self.detail_pane = FoldablePane(self.tree_pane, orient=HORIZONTAL, name="dp", fold_size=100)
        self.system_pane = FoldablePane(self.tree_pane, orient=VERTICAL, name="sp")
        self.console_pane.pack(side=TOP, fill=BOTH, expand=True)

        # if self.main_window:
        #     self.console = Console(self.console_pane)
        self.console = Console(self.console_pane)
        self.tree = Tree(self.detail_pane, self)
        self.detail = Sheet(self.detail_pane, width=25, wrap=NONE, state=DISABLED, takefocus=False)
        self.system = Sheet(self.system_pane, height=3, highlightthickness=2, highlightcolor=Colors.highlight)
        self.sheet_tree = SheetTree(self.system_pane)

        self.current_sheet: ForkableSheet = self.sheet_tree.forkable_sheet

        self.console_pane.add(self.tree_pane)
        self.console_pane.addFoldable(self.console)
        self.tree_pane.addFoldable(self.detail_pane)
        self.tree_pane.add(self.system_pane)
        self.detail_pane.add(self.tree, stretch="never")
        self.detail_pane.addFoldable(self.detail, stretch="always")
        self.system_pane.addFoldable(self.system)
        self.system_pane.add(self.sheet_tree)

        bound_pane = self.detail_pane
        def on_first_configure(ev=None):
            bound_pane.unbind("<Configure>")
            self.system_pane.fold(set_folded=False)
            self.console_pane.fold(set_folded=True)
            self.tree_pane.fold(set_folded=False)
            self.detail_pane.fold(set_folded=False)
            self.toTop()
        bound_pane.bind("<Configure>", on_first_configure)

        if type(sys.stdout) is not TextIOTee:
            sys.stdout = TextIOTee(sys.stdout, self.console.out)
        if type(sys.stderr) is not TextIOTee:
            sys.stderr = TextIOTee(sys.stderr, self.console.err)

        self.menu.create_menu()

        self.sheet_tree.focus_set()

        InitialSheetHelp(self.system, *sheet_help("System prompt - [?]"))
        InitialSheetHelp(self.sheet_tree.forkable_sheet, *sheet_help("User prompt - Chat - [?]"))
        InitialSheetHelp(self.detail, *sheet_help("Details - [?]"))

    def configure_ui_options(self):
        size = 12
        self.option_add('*Dialog*Font', ("sans-serif", size))
        self.option_add('*Menu*Font', ("Arial", size))
        self.option_add('*Font', ("Arial", size))
        if not conf.blinking_caret:
            self.option_add('*Text*insertOffTime', '0')

    def is_initially_modified(self):
        return self.sheet_tree.forkable_sheet.initially_modified or self.system.initially_modified

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
            text = sheet.get(1.0, 'end-1c')
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


    def chat(self, n=1, prefix="", postfix="", inline=False, insert=False, replace=False, location=False, hidden_command=None):
        inline = inline or insert or replace
        self.model.is_canceled = False

        sheet = self.it

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
                self.set_up_insert_completion(sheet)
            elif location:
                self.set_up_location_reference(sheet)
            elif replace:
                self.set_up_replace_completion(sheet)

            history = self.history_from_system_and_chat(additional_message=hidden_command)
            if self.log_messages_to_console:
                history.log()
            self.delete_hidden_prompt(sheet)
            self.model.counter.go()

            reason, message, answer = self.completions(sheet, history, n)
            self.model.counter.summarize("Completion cost:", self.console.tagged_out("cost"))

            self.finish_completion(sheet, reason, message, postfix, inline)
            self.post_completion_tasks(start_time)
        return "break"

    def ask(self, event=None):
        question_box = Sheet(relief=SUNKEN, borderwidth=3, background="lightgray", width=10)

        self.it.window_create(INSERT, window=question_box, stretch=1) #todo implement incomplete feature


    def comment(self, event=None):
        comment_prompt = dedent(
            f"""
            Propose a small change that makes the text better. Solve just one individual issue. A minimal change.
            Specify it as a replacement, as

            Old: "..."
            New: "..."
            [followed by a newline]

            Make a replacement of minimal length, not of whole sentences. It is used as a text replacement, on character level.
            Do not repeat previous results if they are present in the input.
            """)
        sheet = self.it
        self.set_up_location_reference(sheet)
        self.system.hide(END, comment_prompt)

        history = self.history_from_system_and_chat()
        self.delete_hidden_prompt(sheet)
        if self.log_messages_to_console:
            history.log()
        reason, message, answer = self.completions(sheet, history)
        self.tree.add_improvement(Improvement(answer))



    def improve(self, event=None):
        self.system.hide(END, dedent(
            f"""
            Make the proposed change at the position of the location marker "{conf.location_marker}".
            Do not refer to the location marker in the output.
            Ignore the location marker for all other purposes.
            For example, for a marker X and input "foo baXr baz", the word at the location X is "bar" (not "baXr").
            Never literally mention the marker, it is automatically hidden from the user.
            Do not use "{conf.location_marker}" in output.
            
            Propose a small change here that improves the text. Solve just one individual issue. A minimal change.
            Specify it as a replacement, as
            
            Title: "..."
            Old: "..."
            New: "..."
            
            Make a replacement of minimal length, not of whole sentences. It is used as a text replacement, on character level.
            Do not repeat previous results if they are present in the input.
            Always (!) Finish the output with 2 newlines.
            """))
            # If the location marker is after previous changes based on this prompt, assume the whole text as possible places to change.
            # Propose the best change that is anywhere in the text, but not already listed. Never repeat an earlier result.

        sheet = self.it
        history = self.history_from_system_and_chat()
        self.delete_hidden_prompt(sheet)

        if self.log_messages_to_console:
            history.log()

        with WaitCursor(sheet):
            with InsertionIcon(sheet, OUTPUT):
                reason, message, answer = self.model.complete(history)

        self.tree.add_improvement(Improvement(answer))


    def rewrite(self, event=None):
        self.system.hide(END, dedent(
            f"""
            Rewrite the input text to be better, but make only small local changes.
            """))

        sheet = self.it
        history = self.history_from_system_and_chat()
        self.delete_hidden_prompt(sheet)
        if self.log_messages_to_console:
            history.log()
        reason, message, answer = self.completions(sheet, history)

        self.tree.add_improvement(Improvement(history[-1], answer))

    def set_up_location_reference(self, sheet, specific=""):
        location_reference_prompt = dedent(
            f"""
            When the prompt refers to a location or marker in the text, it is the position of "{conf.location_marker}".
            References to a location could be "here", "there", "this", "that" etc.
            Do not refer to that character in the output.
            Ignore the character for all other purposes.
            For example, for a marker X and input "foo baXr baz", the word "here" is "bar" (not "baXr").
            Never literally mention the marker, it is automatically hidden from the user.
            Do not use "{conf.location_marker}" in output, if not strictly needed.
            {specific}
            """)
        self.system.hide(END, location_reference_prompt)
        sheet.hide(INSERT, conf.location_marker)


    def set_up_insert_completion(self, sheet, specific=""):
        insertion_prompt = dedent(
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
        self.system.hide(END, insertion_prompt)
        sheet.hide(INSERT, conf.location_marker)


    def set_up_replace_completion(self, sheet):
        replacement_prompt = dedent(
            f"""
            Do an replacement completion: The output will replace the users text selection, which is 
            the part of text between the two "{conf.location_marker}". 
            Complete assuming the insertion cursor for the text is at the first marker "{conf.location_marker}".
            Produce text that will replace the text between the start marker and the end marker.
            The text after the end marker will still be there after the completion.
            Do not use the markers in the completion. The markers will be removed from the text after completion.
            The part before start marker and after the end marker is already present for the user,
            only produce text that should be in between.
            Do not overlap output and following text.
            The markers themselves will be removed.
            For example, if inside of "fooBARbaz" the text to be replaced is "BAR", the output sould not be "foobarbaz", but just "bar".
            Take care to add the right amount of spaces after the start marker and before the end marker.
            """)
        self.system.hide(END, replacement_prompt)
        sheet.hide(SEL_FIRST, conf.location_marker)
        sheet.hide(SEL_LAST,  conf.location_marker)

    def delete_hidden_prompt(self, sheet):
        sheet.delete_tagged('hidden_prompt')
        self.system.delete_tagged('hidden_prompt')

    @property
    def it(self) -> Sheet:
        focussed = self.focus_get()
        # if focussed == self.system:
        #     self.system.tk_focusNext().focus()
        #     focussed = self.focus_get()
        #     print(f'(switched focus away from system)')

        if isinstance(focussed, Sheet):
            self.current_sheet = focussed

        return self.current_sheet


    def scroll(self, sheet, to=OUTPUT):
        if self.scroll_output:
            sheet.see(to)
        sheet.update()


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


    def completions(self, sheet, history, n=1):
        reason, message, answer = 'unknown', '', ''

        def write_sheet(text, written_sheet: Sheet):
            if self.is_root_destroyed:
                return
            written_sheet.insert(OUTPUT, text, ("assistant", "model-" + self.model.name))
            self.scroll(sheet)

        if n > 1:
            alternatives_frame = tk.Frame(sheet, borderwidth=4, relief=GROOVE)
            sheet.insert(OUTPUT, "\n")
            sheet.window_create(OUTPUT, window=alternatives_frame)
            sheet.insert(OUTPUT, "\n")
            sheet.see(OUTPUT)
            for i in range(n):
                if self.model.is_canceled:
                    reason = "canceled"
                    break
                alternative_frame = tk.Frame(alternatives_frame, borderwidth=4, relief=GROOVE)
                alternative_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
                title = tk.Label(alternative_frame, text=f"Alternatives ({i+1}/{n})", foreground="gray")
                title.pack(side=tk.TOP, anchor=tk.W)
                # sheet.see(OUTPUT)
                alternatives_sheet = AlternativeSheet(alternative_frame) #, width=3)
                reason, message, answer = self.model.complete(history, lambda text: write_sheet(text, alternatives_sheet))
        else:
            with InsertionIcon(sheet, OUTPUT):
                reason, message, answer = self.model.complete(history, lambda text: write_sheet(text, sheet))

        if self.log_messages_to_console:
            print(f'Answer:\n"{answer}"')

        return reason, message, answer


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

        if conf.update_title_after_completion and not self.model.is_canceled:
            self.update_window_title()


    def history_from_system_and_chat(self, additional_message=None, additional_system=None, max_messages=0, max_size=None) :
        system = self.system.get(1.0, 'end-1c')
        history = History(system)

        history = self.it.history_from_path(history)

        history.system(additional_system)
        history.user(additional_message)
        history.limit(messages=max_messages)
        return history

    def toggle_show_hidden_prompts(self, event=None):
        hidden = bool(int(self.system.tag_cget('hidden_prompt', 'elide')))
        for sheet in [self.system, self.it]:
            sheet.tag_config("hidden_prompt", elide=not hidden)

    def insert_system_prompt(self, event=None):
        file = self.tree.focussed_file()
        self.system.insert_file(INSERT, file)

    def replace_system_prompt(self, event=None):
        self.system.delete(1.0, END)
        self.insert_system_prompt()

    def insert_user_prompt(self):
        file = self.tree.focussed_file()
        self.current_sheet.insert_file(INSERT, file)

    def replace_user_prompt(self):
        self.current_sheet.delete(1.0, END)
        self.insert_user_prompt()

    def use_default(self):
        print(f"{self.current_sheet.get(1.0, 'end-1c')=}")
        if not self.current_sheet.get(1.0, "end-1c"):
            self.insert_user_prompt()
            self.it.focus_set()

if __name__ == "__main__":
    Thoughttree(sys.argv)

