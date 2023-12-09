import tkinter as tk
from tkinter import ttk, SEL

from ListDialog import ListDialog
from tools import on_event

class Keys:
    text_keys = {
    '<<NextLine>>': ('<Down>', 'Next Line', 'Down'),
    '<<PrevLine>>': ('<Up>', 'Previous Line', 'Up'),
    '<<NextChar>>': ('<Right>', 'Next Character', 'Right'),
    '<<PrevChar>>': ('<Left>', 'Previous Character', 'Left'),
    '<<NextWord>>': ('<Control-Right>', 'Next Word', 'Control + Right'),
    '<<PrevWord>>': ('<Control-Left>', 'Previous Word', 'Control + Left'),
    '<<NextPara>>': ('<Control-Down>', 'Next Paragraph', 'Control + Down'),
    '<<PrevPara>>': ('<Control-Up>', 'Previous Paragraph', 'Control + Up'),
    '<<NextWindow>>': ('<Tab>', 'Next Window', 'Tab'),
    '<<LineStart>>': ('<Home>', 'Line Start', 'Home'),
    '<<LineEnd>>': ('<End>', 'Line End', 'End'),
    '<<SelectNextLine>>': ('<Shift-Down>', 'Select Next Line', 'Shift + Down'),
    '<<SelectPrevLine>>': ('<Shift-Up>', 'Select Previous Line', 'Shift + Up'),
    '<<SelectNextChar>>': ('<Shift-Right>', 'Select Next Character', 'Shift + Right'),
    '<<SelectPrevChar>>': ('<Shift-Left>', 'Select Previous Character', 'Shift + Left'),
    '<<SelectNextWord>>': ('<Control-Shift-Right>', 'Select Next Word', 'Control + Shift + Right'),
    '<<SelectPrevWord>>': ('<Control-Shift-Left>', 'Select Previous Word', 'Control + Shift + Left'),
    '<<SelectNextPara>>': ('<Control-Shift-Down>', 'Select Next Paragraph', 'Control + Shift + Down'),
    '<<SelectPrevPara>>': ('<Control-Shift-Up>', 'Select Previous Paragraph', 'Control + Shift + Up'),
    '<<SelectLineStart>>': ('<Shift-Home>', 'Select Line Start', 'Shift + Home'),
    '<<SelectLineEnd>>': ('<Shift-End>', 'Select Line End', 'Shift + End'),
    '<<SelectAll>>': ('<Control-a>', 'Select All', 'Control + /'),
    '<<SelectNone>>': ('<Control-backslash>', 'Select None', 'Control + \\'),
    # '<<Copy>>': ('<Control-c>', 'Copy', 'Control + C'),
    # '<<Cut>>': ('<Control-x>', 'Cut', 'Control + X'),
    # '<<Paste>>': ('<Control-v>', 'Paste', 'Control + V'),
    '<<PasteSelection>>': ('<ButtonRelease-2>', 'Paste Selection', 'ButtonRelease-2'),
    '<<Undo>>': ('<Control-z>', 'Undo', 'Control + Z'),
    '<<Redo>>': ('<Control-Z>', 'Redo', 'Control + Shift + Z'),
    '<<ToggleSelection>>': ('<Control-Button-1>', 'Toggle Selection', 'Control + Button 1'),
    '<<ContextMenu>>': ('<Button-3>', 'Context Menu', 'Button 3')
    }

    superfluous_tcl_tk_text_keys = [
        '<Control-t>',
        '<Control-d>',
        '<Control-e>',
        '<Control-h>',
        '<Control-k>',
        '<Control-i>',
        '<Control-o>',
    ]

    @staticmethod
    def configure_text_keys(text: tk.Text):
        for virtual, (key, explanation, key_name) in list(Keys.text_keys.items()):
            text.event_delete(virtual)
            text.event_add(virtual, key)
        for key in Keys.superfluous_tcl_tk_text_keys:
            text.unbind_class("Text", key)
        Keys.fix_paste(text)


    @staticmethod
    def fix_paste(text):
        def replacing_paste(event):
            w = event.widget
            if w.tag_ranges(SEL):
                w.delete("sel.first", "sel.last")
            w.insert("insert", w.clipboard_get())
            return "break"
        text.winfo_toplevel().bind_class("Text", "<<Paste>>", replacing_paste)


    @staticmethod
    def show_text_keys_help(text):
        desc_and_keystroke = {k: (v[1], v[2]) for k, v in Keys.text_keys.items()}
        ListDialog(desc_and_keystroke, "Text Keymap Help", text)
