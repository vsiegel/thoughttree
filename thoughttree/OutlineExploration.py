import difflib
import random
import re
import tkinter as tk
from textwrap import dedent
from tkinter import INSERT, END

from InsertionIcon import InsertionIcon
from Sheet import Sheet, OUTPUT
from StructuredInteraction import StructuredInteraction
from WaitCursor import WaitCursor
from tools import fail


class OutlineExploration(StructuredInteraction):
    def __init__(self, outline_level_spec, title=None, outline_id=None, parent_id=None):
        super().__init__()
        self.outline_id = outline_id or random.randint(1000000, 9999999)
        self.parent_id = parent_id or outline_id

        self.title = title or self.outline_id
        self.valid = True
        self.outline_level_items = []
        self.parse(outline_level_spec)

    def __str__(self):
        return "oa" + self.outline_id


    def explore_outline(self, event=None, hidden_command=None, outline_id=None, parent_id=None):
        outline_id = outline_id or random.randint(1000000, 9999999)
        parent_id = parent_id or outline_id
        keep_hidden_command = True
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
        history = self.history_from_system_and_chat(additional_message=hidden_command)
        if not keep_hidden_command:
            self.delete_hidden_prompt(sheet)

        if self.log_messages_to_console:
            history.log()

        with WaitCursor(sheet):
            with InsertionIcon(sheet, OUTPUT):
                reason, message, answer = self.model.complete(history, lambda text: self.write_sheet(text, sheet))

        answer += "\n\n"
        if self.log_messages_to_console:
            self.log.print(f'Answer:\n"{answer}"')

        outline_exploration = OutlineExploration(answer, outline_id=outline_id, parent_id=parent_id)
        sheet.outline_exploration = outline_exploration
        self.tree.add_outline_exploration(outline_exploration)


    def parse(self, outline_level_spec):
        LABELED_LINE_PATTERN = "(?m)^([A-Z]\w+): (.*)$"
        OUTLINE_ITEM_PATTERN = "(?m)^ *([0-9]+\.[0-9.]*)\s+(.*)$"
        try:
            match = re.match(LABELED_LINE_PATTERN, outline_level_spec)
            if match:
                self.title = match.group(2)

            matches = re.findall(OUTLINE_ITEM_PATTERN, outline_level_spec)
            matches or fail(f'No match for "{OUTLINE_ITEM_PATTERN}"')

            for groups in matches:
                outline_id = groups[0]
                outline_title = groups[1]
                self.outline_level_items.append((outline_id, outline_title))
        except Exception as ex:
            self.valid = False
            print(f'{ex=}')
            print(f'{outline_level_spec}')
