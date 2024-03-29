#!/usr/bin/env python3
import random
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
from EventPlayer import EventPlayer
from EventRecorder import EventRecorder
from OutlineExploration import OutlineExploration
from FinishReasonIcon import FinishReasonIcon
from FoldablePane import FoldablePane
from History import History
from InsertionIcon import InsertionIcon
from Log import Log
from Sheets import Sheets
from InitialSheetHelp import InitialSheetHelp
from Improvement import Improvement
from TextIOTee import TextIOTee
from ExceptionBlockedIO import ExceptionBlockedIO
from Title import Title
from HidableFrame import HidableFrame
from Model import Model
from AlternativeSheet import AlternativeSheet
from StatusBar import StatusBar
from Sheet import Sheet, OUTPUT
from MainMenu import MainMenu
from Tree import Tree
from TreeSheet import TreeSheet
from Ui import Ui
from WaitCursor import WaitCursor
from finish_reasons import finish_reasons
from sheet_help_texts import sheet_help
from tools import log_motion_on_ctrl_alt, fail

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
    MIN_SIZE = (600, 150)
    ROOT_GEOMETRY = "1300x750"
    icon = None
    multi_completions = 5

    interactive_model_name = 'gpt-4'
    # interactive_model_name = 'gpt-3.5-turbo'
    generation_model_name = 'gpt-3.5-turbo'


    def __init__(self, argv=None):
        Ui.__init__(self, title="Thoughttree", name="tt", icon_path=WINDOW_ICON, closeable=False)

        # class TkExceptionHandler:
        #     def __init__(self, func=None, subst=None, widget=None):
        #         self.func = func
        #         self.subst = subst
        #         self.widget = widget
        #
        #
        #     def __call__(self, *args):
        #         print(f"TkExceptionHandler: {args=}")
        #         if self.subst:
        #             args = self.subst(*args)
        #         return self.func(*args)
        # tk.CallWrapper = TkExceptionHandler()

        self.show_internal_prompts = None
        self.status_hider = None
        self.status = None
        self.console = None
        Ui.log = None
        self.tree = None
        self.detail: Sheet|None = None
        self.system: Sheet|None = None
        self.sheets: Sheets | None = None
        self.model = None
        self.console_pane = None
        self.tree_pane = None
        self.detail_pane = None
        self.system_pane = None

        geometry = Thoughttree.ROOT_GEOMETRY
        if conf.debug:
            geometry += "+700+100"
        self.configure_geometry(argv, geometry, Thoughttree.MIN_SIZE)

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

        self.update()
        InitialSheetHelp(self.system, *sheet_help("System prompt - [?]"))
        InitialSheetHelp(self.sheets.sheet, *sheet_help("User prompt - Chat - [?]"))
        InitialSheetHelp(self.detail, *sheet_help("Details - [?]"))


        if self.main_window:
            # EventRecorder(self)
            # events = (["a", "b", "c", "\n", "a", "<b>", "c", "\n", "foo", "bar", 500, "a", "bbbb", ])
            # events = None # (["a", "a", "a", "b", "c", "d", "e", "a", "a", "a",])
            # events = None # (["a", "a", "a", "b", "c", "d", "e", "a", "a", "a",])
            # EventPlayer(self, events)
            # EventRecorder(self)
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

        self.console_pane = FoldablePane(self, orient=VERTICAL, name="cp", panel="Console", key="<Control-Alt-C>")
        self.tree_pane = FoldablePane(self.console_pane, orient=HORIZONTAL, name="tp", fold_size=500, panel="Tree", key="<Control-Alt-T>")
        self.detail_pane = FoldablePane(self.tree_pane, orient=HORIZONTAL, name="dp", fold_size=100, panel="Details", key="<Control-Alt-D>")
        self.system_pane = FoldablePane(self.tree_pane, orient=VERTICAL, name="sp", panel="System", key="<Control-Alt-S>")
        self.console_pane.pack(side=TOP, fill=BOTH, expand=True)

        self.console = Console(self.console_pane, highlightthickness=2, highlightcolor=Colors.highlight)
        if not Ui.log:
            Ui.log = Log(self.console)
        tree_highlight_frame = tk.Frame(self.detail_pane, highlightthickness=2)
        self.tree = Tree(tree_highlight_frame, self)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        self.detail = Sheet(self.detail_pane, width=25, wrap=NONE, state=DISABLED, takefocus=False)
        self.system = Sheet(self.system_pane, height=3, highlightthickness=2, highlightcolor=Colors.highlight)
        self.sheets = Sheets(self.system_pane)
        self.console_pane.add(self.tree_pane)
        self.console_pane.addFoldable(self.console)
        self.tree_pane.addFoldable(self.detail_pane)
        self.tree_pane.add(self.system_pane)
        self.detail_pane.add(tree_highlight_frame, stretch="never")
        self.detail_pane.addFoldable(self.detail, stretch="always")
        self.system_pane.addFoldable(self.system)
        self.system_pane.add(self.sheets)

        bound_pane = self.detail_pane
        def on_first_configure(ev=None):
            bound_pane.unbind("<Configure>")
            self.system_pane.fold(set_folded=False)
            self.console_pane.fold(set_folded=True)
            self.tree_pane.fold(set_folded=False)
            self.detail_pane.fold(set_folded=False)
        bound_pane.bind("<Configure>", on_first_configure)
        self.toTop()

        if not isinstance(sys.stdout, TextIOTee):
            sys.stdout = TextIOTee(ExceptionBlockedIO(sys.stdout), self.console.out)
        if not isinstance(sys.stderr, TextIOTee):
            sys.stderr = TextIOTee(ExceptionBlockedIO(sys.stderr), self.console.err)

        self.menu.create_menu()

        self.sheets.focus_set()


    def configure_ui_options(self):
        size = 12
        self.option_add('*Dialog*Font', ("sans-serif", size))
        self.option_add('*Menu*Font', ("Arial", size))
        self.option_add('*Font', ("Arial", size))
        if not conf.blinking_caret:
            self.option_add('*Text*insertOffTime', '0')

    def significantly_changed(self):
        if self.sheets.sheet.initially_modified or self.system.initially_modified: # todo recurse sheets
            size = self.history_from_system_and_chat().size()
            return size >= Ui.SIGNIFICANT_CHANGE_LIMIT
        else:
            return False

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
        self.generation_model.complete(history, write_title, max_tokens=30, temperature=0.5)
        Ui.log.cost("Title cost:\n" + self.generation_model.counter.summary())


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

        if self.focus_get() == self.system:
            self.sheets.focus_set()

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
                Ui.log.format(history)
            self.delete_internal_prompt(sheet)
            self.model.counter.go()

            reason, message, answer = self.completions(sheet, history, n)

            Ui.log.cost("Completion cost:\n" + self.model.counter.summary())

            self.finish_completion(sheet, reason, message, postfix, inline, start_time)

        self.sheets.update_tab_title()
        return "break"

    def ask(self, event=None):
        question_box = Sheet(relief=SUNKEN, borderwidth=3, background="lightgray", width=10)

        self.it.window_create(INSERT, window=question_box, stretch=1) #todo implement incomplete feature


    def comment(self, event=None):
        sheet = self.it
        self.set_up_location_reference(sheet)
        self.system.hide(END, dedent(
            f"""
            Propose a small change that makes the text better. Solve just one individual issue. A minimal change.
            Specify it as a replacement, as

            Old: "..."
            New: "..."
            [followed by a newline]

            Make a replacement of minimal length, not of whole sentences. It is used as a text replacement, on character level.
            Do not repeat previous results if they are present in the input.
            """))

        history = self.history_from_system_and_chat()
        self.delete_internal_prompt(sheet)
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
        self.delete_internal_prompt(sheet)

        if self.log_messages_to_console:
            history.log()

        with WaitCursor(sheet):
            with InsertionIcon(sheet, OUTPUT):
                reason, message, answer = self.model.complete(history)

        self.tree.add_improvement(Improvement(answer))


    def explore_outline(self, event=None, prompt_arg=None, outline_id=None, parent_id=None):
        outline_id = outline_id or random.randint(1000000, 9999999)
        parent_id = parent_id or outline_id
        self.system.hide(END, dedent(
            f"""
Lines starting with "#" are comments or disabled parts of the prompt and should be ignored.
# Prompt "explore_outline"

Explore an outline drilling down in the information by incrementally extending an outline locally, directed by the user input that specifies what the user is interested in.  Analyse the text and express the relevant data incrementally in an outline structure that is most suitable for this specific text.
Use a decimal outline (1.1.1...)
The structure of the outline should not be based on the document structure. 
The outline structure can be of any usual or unusual kind, abstract or concrete or both - the important point is that it is custom build for the document at hand, it does not need to fit any other purpose. 
The purpose of the outline is not to describe the content of the document, it should provide information about the document.
For example high level descriptions, conclusions that can be drawn, political or other implications, criticism...

Except if a subitem is specified, produce the first level of the structure, each item as detailed as appropriate - the token budget to used is high.

If a subitem is given, and the higher levels are already generated, generate a level from there.

So for the first prompt that contains only the input text,  generate only one outline level of items .
1. ...
2. ...
...

In a second run, generate the sub items for one of the existing items. For example, if the new prompt specifies "2.":
2.1. ...
2.2. ...
...

Each item consists of a one line title.
Section names need to match exactly when used in multiple places. 

For example, for this outline level as first output:
1. Foo
2. Bar
3. Baz

and a next prompt:

2.

the answer needs to start exactly with:

Id: ...
Title: Bar
2.1. ...

If an item is not directly based on the document, but on background knowledge, set it in "()", like so:
1.1 (Foo) 
Use as many items as make sense from the content. More detailed output is preferred.
There is no requirement for symmetry or balance, always focus on the sub-item the user is interested in.
Start the output with a newline.

The output for a prompt contains only one level. The user then can select items according to his interest, to generate further details.
Prepend the output with the following fields:

Id: ...
Title: ...

Start the output with two newlines. Add two newlines after the output.
If the prompt is a section id, continue with that section.
If it is "Text: [id]", output the text of the section as Text: [id] "..."
If it is "Ref: [id]", output a substring of the text this item is referring to as Ref: [id] "..."
The Id of this outline is: {outline_id} (equal for all levels of this outline.)
"""))
        # For each item, add a reference and a section text, like this:
        # 2.3. Foo ...
        #    "relevant substring"
        #    "Text of Foo section"

        # Prepend the outline with the following fields:
        #
        # Input_Title: ...
        # Input_Summary: ...
        # Outline_Title: ...
        # Outline_Abstract: ...
        # Disabled propmpt part:
        # Start the output with a description of the reasoning that lead to choosing #the speciffic outline.
        # Use the format:
        # Description: ...

        sheet = self.it
        history = self.history_from_system_and_chat(additional_message=prompt_arg)
        # self.delete_internal_prompt(sheet)

        if self.log_messages_to_console:
            Ui.log.assistant(history)

        with WaitCursor(sheet):
            with InsertionIcon(sheet, OUTPUT):
                reason, message, answer = self.model.complete(history, lambda text: self.write_sheet(text, sheet))

        # sheet.insert(END, "\n\n")
        # answer += "\n\n"
        self.write_sheet("\n\n", sheet)
        if self.log_messages_to_console:
            Ui.log.assistant(f'"{answer}"\n')

        outline_exploration = OutlineExploration(answer, outline_id=outline_id, parent_id=parent_id)
        # self.tree.add_outline_exploration(outline_exploration)
        outline_exploration and outline_exploration.add_to_tree(self.tree)


    def rewrite(self, event=None):
        self.system.hide(END, dedent(
            f"""
            Rewrite the input text to be better, but make only small local changes.
            """))

        sheet = self.it
        history = self.history_from_system_and_chat()
        self.delete_internal_prompt(sheet)
        if self.log_messages_to_console:
            history.log()
        reason, message, answer = self.completions(sheet, history)

        self.tree.add_improvement(Improvement(history[-1], answer))

    def set_up_location_reference(self, sheet, specific=""):
        self.system.hide(END, dedent(
            f"""
            When the prompt refers to a location or marker in the text, it is the position of "{conf.location_marker}".
            References to a location could be "here", "there", "this", "that" etc.
            Do not refer to that character in the output.
            Ignore the character for all other purposes.
            For example, for a marker X and input "foo baXr baz", the word "here" is "bar" (not "baXr").
            Never literally mention the marker, it is automatically hidden from the user.
            Do not use "{conf.location_marker}" in output, if not strictly needed.
            {specific}
            """))
        sheet.hide(INSERT, conf.location_marker)


    def set_up_insert_completion(self, sheet, specific=""):
        self.system.hide(END, dedent(
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
            """))
        sheet.hide(INSERT, conf.location_marker)


    def set_up_replace_completion(self, sheet):
        self.system.hide(END, dedent(
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
            """))
        sheet.hide(SEL_FIRST, conf.location_marker)
        sheet.hide(SEL_LAST,  conf.location_marker)

    def delete_internal_prompt(self, sheet):
        sheet.delete_tagged('internal_prompt')
        self.system.delete_tagged('internal_prompt')

    @property
    def it(self) -> Sheet:
        focussed = self.focus_get()
        # if isinstance(focussed, TreeSheet):
        #     sheet = focussed
        if isinstance(focussed, Sheet):
            sheet = focussed
        else:
            sheet = self.sheets.current
        return sheet


    def scroll(self, sheet, to=OUTPUT):
        if self.scroll_output and isinstance(sheet, TreeSheet):
            sheet.see_in_tree(to=to)
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

    def write_sheet(self, text, written_sheet: Sheet):
        if self.is_root_destroyed:
            return
        written_sheet.insert(OUTPUT, text, ("assistant", "model-" + self.model.name))
        self.scroll(written_sheet)


    def completions(self, sheet, history, n=1):
        reason, message, answer = 'unknown', '', ''

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
                reason, message, answer = self.model.complete(history, lambda text: self.write_sheet(text, alternatives_sheet))
        else:
            with InsertionIcon(sheet, OUTPUT):
                reason, message, answer = self.model.complete(history, lambda text: self.write_sheet(text, sheet))

        if self.log_messages_to_console:
            Ui.log.assistant(f'"{answer}"\n')

        return reason, message, answer


    def finish_completion(self, sheet, finish_reason, message, postfix, inline, start_time):
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

        if self.ring_bell_after_completion:
            if datetime.now().timestamp() - start_time.timestamp() > conf.ring_bell_only_after:
                self.bell()

        if conf.update_title_after_completion and not self.model.is_canceled:
            self.update_window_title()


    def show_finish_reason_icon(self, sheet, finish_reason, message):
        symbol = finish_reasons[finish_reason]["symbol"]
        if finish_reason not in ["stop", "length", "canceled", "error"]:
            print(f"{finish_reason=}")
        if symbol:
            tooltip = finish_reasons[finish_reason]["tooltip"]
            if message:
                tooltip += "\n" + message

            sheet.window_create(OUTPUT, window=FinishReasonIcon(sheet, symbol, tooltip=tooltip))



    def history_from_system_and_chat(self, additional_message=None, additional_system=None, max_messages=0, max_size=None) :
        system = self.system.get(1.0, 'end-1c')
        history = History(system)

        # history = self.it.history_from_path(history)
        history = self.sheets.current.history_from_path(history)

        history.system(additional_system)
        history.user(additional_message)
        history.limit(messages=max_messages)
        return history

    def toggle_show_internal_prompts(self, event=None):
        hidden = bool(int(self.system.tag_cget('internal_prompt', 'elide')))
        for sheet in [self.system, self.it]:
            sheet.tag_config("internal_prompt", elide=not hidden)


if __name__ == "__main__":
    Thoughttree(sys.argv)

