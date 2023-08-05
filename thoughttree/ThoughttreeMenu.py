import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import font as tkfont, NONE, WORD, SEL, END, INSERT

from AboutDialog import AboutDialog
from Files import Files
from Menu import Menu
from ModelsMenu import ModelsMenu
from WindowsMenu import WindowsMenu
from Sheet import Sheet
from Console import Console
from menu_help import menu_help
from functools import partial

class ThoughttreeMenu(Menu):
    def __init__(self, thoughttree, new_window_callback):
        super().__init__(thoughttree, menu_help=menu_help)
        self.new_window_callback = new_window_callback
        self.ui = thoughttree

        self.fixed_model_menu_items = -1
        self.models_menu = None
        self.create_menu()


    @property
    def it(self) -> Sheet:
        widget = self.ui.focus_get()
        if isinstance(widget, Sheet) or isinstance(widget, Console):
            return widget


    def create_menu(self):

        def save(save_dialog, status_bar_label):
            file_name = save_dialog(self.it)
            if not file_name:
                return
            base_name = file_name.split("/")[-1]
            self.ui.status.note = status_bar_label + base_name
            return base_name

        def save_chat(e=None):
            name = save(Files.save_chat_dialog, "Chat saved to ")
            self.ui.title(name)

        def save_section(e=None):
            save(Files.save_section_dialog, "Section saved to ")

        def save_selection(e=None):
            save(Files.save_selection_dialog, "Selection saved to ")

        def save_code_block(e=None):
            save(Files.save_code_block_dialog, "Code block saved to ")

        def new_window(event=None) :
            self.new_window_callback()

        def show_context_menu(event, context_menu) :
            widget = self.ui.winfo_containing(event.x_root, event.y_root)
            if widget :
                widget.focus_set()
            context_menu.tk_popup(event.x_root, event.y_root)

        def cut_text(event=None) :
            self.it.event_generate("<<Cut>>")

        def copy_text(event=None) :
            self.it.event_generate("<<Copy>>")

        def paste_text(event=None) :
            sheet = self.it
            sheet.event_generate("<<Clear>>")
            sheet.event_generate("<<Paste>>")
            sheet.see(INSERT)

        def select_all(event=None):
            sheet = self.it
            if type(sheet) == Sheet:
                sheet.tag_add(SEL, "1.0", END)
                sheet.mark_set(INSERT, "1.0")
                sheet.see(INSERT)

        def edit_undo(event=None):
            try:
                self.it.edit_undo()
            except tk.TclError:
                pass # nothing to undo

        def edit_redo(event=None):
            try:
                self.it.edit_redo()
            except tk.TclError:
                pass # nothing to redo

        def font_size(delta):
            sheet = self.it
            if not sheet:
                return
            if delta == 0:
                name, size = Sheet.FONT
            else:
                name, size = sheet.cget("font").split()
            sheet.config(font=(name, int(size) + delta))

        def insert_current_time(event=None):
            self.it.insert(INSERT, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ")

        def debug_info(event=None):
            print(f"{self.focus_get()=}")
            return

            dumped = self.it.dump("insert - 1 char", window=True)
            # print(f'{ dumped=}')
            if dumped and dumped[0][1].endswith("label"):
                dumped_win = dumped[0][1]
                dumped_win_pos = dumped[0][2]
                print(f'{dumped_win=}')
                print(f'{dumped_win_pos=}')
                print(f'{type(self.it.window_configure(dumped_win_pos))=}')
                # print(f'{self.focus.window_configure(dumped_win_pos)=}')
                print(f"{type(self.it.window_cget(dumped_win_pos, 'window'))=}")
            print()
            dumped = self.it.dump("1.0", INSERT, all=True)
            for part in dumped:
                print(f'{part=}')


        def menu_test(event=None):
            pass


        def branch():
            self.it.fork()
            self.ui.update()
            self.ui.complete()

        def toggle_scroll_output(event=None):
            if self.ui.scroll_output:
                self.it.see(END)
            self.ui.scroll_output = not self.ui.scroll_output

        def toggle_ring_bell(event=None):
            self.ui.ring_bell_after_completion = not self.ui.ring_bell_after_completion

        def toggle_font_mono(event=None):
            font = tkfont.Font(font=self.it.cget("font"))
            size = font.cget("size")
            if font.measure('I') != font.measure('M'):
                family = Sheet.FONT_NAME_MONOSPACE
            else:
                family = Sheet.FONT_NAME_PROPORTIONAL
            self.it.configure(font=(family, size))
            return "break"

        def close_tab(event=None):
            it = self.it
            if type(it) == Sheet:
                it.close_tab()

        def search_google(event=None):
            selected_range = self.it.tag_ranges(SEL)
            if selected_range:
                selected_text = self.it.get(*selected_range)[:2000]
                if selected_text:
                    webbrowser.open_new_tab("https://www.google.com/search?q=" + selected_text)


        item = self.sub_item
        ui = self.ui

        self.menu = Menu(self, "File")
        item("New Window", "<Control-n>", new_window)
        item("New Main Tab", "<Control-t>", lambda e=None: self.it.fork("1.0"))
        item("Open File", "<Control-o>", save_chat)
        # item("Save Chat", "<Control-s>", Files.save_chat)
        item("Save Chat", "<Control-s>", save_chat)
        item("Save Message", "<Control-Shift-S>", save_section)
        item("Save Selection", "<Alt-S>", save_selection)
        item("Save Code Block", "<Control-Alt-s>", save_code_block)
        item("Run Code Block", "", None)
        self.menu.add_separator()
        item("Close Tab", "<Control-w>", close_tab, add=False)
        item("Close Empty Tab", "<BackSpace>", lambda e=None: self.it.close_empty_tab_or_backspace(), add=False)
        item("Quit", "<Control-q>", ui.close)

        self.menu = Menu(self, "Edit")
        edit_menu = self.menu
        item("Cut", "<Control-x>", cut_text)
        item("Copy", "<Control-c>", copy_text)
        item("Paste", "<Control-v>", paste_text)
        item("Delete", "<Delete>", lambda e=None: self.it.delete())
        self.menu.add_separator()
        item("Undo", "<Control-z>", edit_undo)
        item("Redo", "<Control-Shift-Z>", edit_redo)
        item("Select All", "<Control-a>", select_all)
        self.menu.add_separator()
        item("Search with Google", "<Control-g>", search_google)
        item("Insert Current Time", "<Control-Shift-I>", insert_current_time)
        item("Include Date in System Prompt", None, None)
        item("Copy Title", None, None)

        self.menu = Menu(self, "View")
        item("Show Main Menu", "<Alt-Shift-M>", None)
        item("Show System Prompt", "<Alt-Shift-S>", ui.system_pane.fold)
        item("Show Tree", "<Alt-Shift-T>", ui.tree_pane.fold)
        item("Show Console", "<Alt-Shift-C>", ui.console_pane.fold)
        item("Show Status Bar", "<Alt-Shift-I>", ui.status_hider.hide)
        self.menu.add_separator()
        item("Count Tokens", "<Control-Alt-m>", ui.count_text_tokens)
        item("Update Window Title", "<Control-u>", ui.update_window_title)
        self.menu.add_separator()
        item("Increase Font Size", "<Control-plus>", lambda e=None: font_size(1))
        item("Decrease Font Size", "<Control-minus>", lambda e=None: font_size(-1))
        item("Reset Font Size", "<Control-period>", lambda e=None: font_size(0))
        item("Toggle Monospace", "<Control-Shift-O>", toggle_font_mono)
        # self.menu.add_checkbutton(label="Show Cursor line", variable=ui.show_cursor)
        self.menu.add_separator()
        item("Toggle Scrolling Output", "<Control-e>", toggle_scroll_output)
        item("Ring Bell When Finished", "<Control-Alt-o>", toggle_ring_bell)
        item("Toggle Wrap Lines", "<Control-l>", lambda e=None: self.it.configure(wrap=(NONE if self.it.cget("wrap") != NONE else WORD)))
        item("Generate Titles", "", None)
        item("Calculate Cost", "", None)

        self.menu = Menu(self, "Navigate")
        item("Next Similar Line", "<Control-j>", lambda e=None: self.it.jump_to_similar_line(direction=1))
        item("Previous Similar Line", "<Control-Shift-J>", lambda e=None: self.it.jump_to_similar_line(direction=-1))
        item("Next Message", "", None)
        item("Previous Message", "", None)

        self.menu = Menu(self, "Chat")
        item("Next Paragraph", "<Control-Return>", lambda e=None: ui.complete(1, "\n\n", "\n\n"))
        item("Next Line", "<Shift-Return>", lambda e=None: ui.complete(1, "\n", "\n"))
        item("Continue Directly", "<Control-space>", lambda e=None: ui.complete())
        item("Fork Conversation", "<Alt-Return>", lambda e=None: self.it.fork())
        item("Complete in Branch", "<Control-Shift-Return>", lambda e=None: branch())
        item("Complete Alternatives", "<Alt-Shift-Return>", lambda e=None: ui.complete(-1, "\n"))
        self.menu.add_separator()
        item("Complete 3 Times", "<Control-Key-3>", lambda e=None: ui.complete(3), add=False)
        [self.bind_class("Text", f"<Control-Key-{i}>", lambda e=None, i=i: ui.complete(i)) for i in [2,4,5,6,7,8,9]]

        item("Complete Multiple...", "<Control-Shift-M>", lambda e=None: ui.complete(0))
        item("Complete Multiple Again", "<Control-m>", lambda e=None: ui.complete(-1))
        self.menu.add_separator()
        # item("Mark assistant message", "<Control-Alt-a>", mark_assistant_message)
        item("Cancel", "<Escape>", ui.cancel_models)

        self.menu = Menu(self, "Query")
        item("Max Tokens...", "<Control-Shift-L>", ui.configure_max_tokens)
        item("Temperature...", "<Control-Shift-T>", ui.configure_temperature)
        item("Increase Temperature", "<Alt-plus>", None)
        item("Decrease Temperature", "<Alt-minus>", None)
        item("Temperature 0.0", "<Control-Key-0>", None)

        self.models_menu = ModelsMenu(self, ui, "Models")

        self.windows_menu = WindowsMenu(self, "Windows")

        self.menu = Menu(self, "Help")
        item("Test", "<Control-Alt-Shift-T>", menu_test)
        item("Debug Info", "<Control-i>", debug_info)
        item("About", "<Shift-Alt-F1>", lambda e=None: AboutDialog(self.ui))

        ui.bind("<Control-Button-4>", lambda e=None: font_size(1))
        ui.bind("<Control-Button-5>", lambda e=None: font_size(-1))

        ui.bind_class("Text", "<Button-3>", lambda e=None: show_context_menu(e, edit_menu))


    def sub_item(self, label, keystroke=None, command=None, variable=None, add=False):
        if not label in menu_help:
            print("Help text missing for menu item \"" + label + "\"")
        self.menu.item(label, keystroke, command, variable, add)



'''
"New Window", 4,
"New Main Tab", 4,
"Save Chat", 5,
"Save Message", 5,
"Save Selection", 5,
"Save Code Block", 5,
"Run Code Block", 4,
"Close Tab", 6,
"Close Empty Tab", 6,
"Quit", 0,

"Cut", 1,
"Copy", 1,
"Paste", 0,
"Delete", 0,
"Undo", 1,
"Redo", 0,
"Select All", 7,
"Search with Google", 7,
"Insert Current Time", 7,
"Include Date in System Prompt", 8,
"Copy Title", 5,

"Show Main Menu", 5,
"Show System Prompt", 5,
"Show Tree", 5,
"Show Console", 5,
"Show Status Bar", 5,
"Count Tokens", 6,
"Update Window Title", 7,
"Increase Font Size", 9,
"Decrease Font Size", 9,
"Reset Font Size", 6,
"Toggle Monospace", 7,
"Toggle Scrolling Output", 7,
"Ring Bell When Finished", 10,
"Toggle Wrap Lines", 7,
"Generate Titles", 9,
"Calculate Cost", 9,

"Next Similar Line", 5,
"Previous Similar Line", 9,
"Next Message", 5,
"Previous Message", 9,

"Next Paragraph", 5,
"Next Line", 5,
"Continue Directly", 9,
"Fork Conversation", 5,
"Complete in Branch", 9,
"Complete Alternatives", 9,
"Complete 3 Times", 9,
"Complete Multiple...", 9,
"Complete Multiple Again", 9,
"Cancel", 0,

"Max Tokens...", 4,
"Temperature...", 0,
"Increase Temperature", 9,
"Decrease Temperature", 9,
"Temperature 0.0", 11,

"Test", 0,
"Debug Info", 6,
"About", 0.

'''
