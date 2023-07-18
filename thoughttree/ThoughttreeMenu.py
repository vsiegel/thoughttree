import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import font as tkfont, NONE, WORD, SEL, END, INSERT

from Files import Files
from Menu import Menu
from ModelsMenu import ModelsMenu
from Text import Text
from menu_help import menu_help


class ThoughttreeMenu(Menu):
    def __init__(self, thoughttree, new_window_callback):
        super().__init__(thoughttree, menu_help=menu_help, tearoff=False)
        self.new_window_callback = new_window_callback
        self.ui = thoughttree

        self.fixed_model_menu_items = -1
        self.models_menu = None
        self.create_menu()


    @property
    def it(self) -> Text:
        return self.ui.focus_get()



    def create_menu(self):

        def save(save_dialog, status_bar_label):
            file_name = save_dialog(self.it)
            if not file_name:
                return
            base_name = file_name.split("/")[-1]
            self.ui.status_bar.note = status_bar_label + base_name
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

        def new_main_tab(event=None) :
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
            txt = self.it
            txt.event_generate("<<Clear>>")
            txt.event_generate("<<Paste>>")
            txt.see(INSERT)

        def select_all(event=None):
            txt = self.it
            if type(txt) == Text:
                txt.tag_add(SEL, "1.0", END)
                txt.mark_set(INSERT, "1.0")
                txt.see(INSERT)

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
            txt = self.it
            if delta == 0:
                name, size = Text.FONT
            else:
                name, size = txt.cget("font").split()
            txt.config(font=(name, int(size) + delta))

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

        def item(label, keystroke=None, command=None, bind_key=True, context_menu=None, variable=None, add=False):
            if not label in menu_help:
                print("Help text missing for menu item \"" + label + "\"")
            menu.item(label, keystroke, command, bind_key, context_menu, variable, add)

        def toggle_scroll_output(event=None):
            self.ui.scroll_output = not self.ui.scroll_output
            if self.ui.scroll_output:
                self.it.see(END)

        def toggle_ring_bell(event=None):
            self.ui.notify_end = not self.ui.notify_end

        def toggle_font_mono(event=None):
            font = tkfont.Font(font=self.it.cget("font"))
            size = font.cget("size")
            if font.measure('I') != font.measure('M'):
                family = Text.FONT_NAME_MONOSPACE
            else:
                family = Text.FONT_NAME_PROPORTIONAL
            self.it.configure(font=(family, size))
            return "break"

        def close_text_tab(event=None):
            it = self.it
            if type(it) == Text:
                it.close_text_tab()

        def search_google(event=None):
            selected_range = self.it.tag_ranges(SEL)
            if selected_range:
                selected_text = self.it.get(*selected_range)[:2000]
                if selected_text:
                    webbrowser.open_new_tab("https://www.google.com/search?q=" + selected_text)

        ui = self.ui

        menu = Menu(self, "File")
        item("New Window", "<Control-n>", new_window)
        item("New Main Tab", "<Control-t>", lambda e: self.it.fork("1.0"))
        # item("Save Chat", "<Control-s>", Files.save_chat)
        item("Save Chat", "<Control-s>", save_chat)
        item("Save Message", "<Control-Shift-S>", save_section)
        item("Save Selection", "<Alt-S>", save_selection)
        item("Save Code Block", "<Control-Alt-s>", save_code_block)
        item("Run Code Block", "", None)
        menu.add_separator()
        item("Close Tab", "<Control-w>", close_text_tab, add=False)
        item("Close Empty Tab", "<BackSpace>", lambda e: self.it.close_empty_tab_or_backspace(), add=False)
        item("Quit", "<Control-q>", ui.close)

        menu = Menu(self, "Edit")
        edit_menu = menu
        item("Cut", "<Control-x>", cut_text)
        item("Copy", "<Control-c>", copy_text)
        item("Paste", "<Control-v>", paste_text)
        item("Delete", "<Delete>", lambda e: self.it.delete())
        menu.add_separator()
        item("Undo", "<Control-z>", edit_undo)
        item("Redo", "<Control-Shift-Z>", edit_redo)
        item("Select All", "<Control-a>", select_all)
        menu.add_separator()
        item("Search with Google", "<Control-g>", search_google)
        item("Insert Current Time", "<Control-Shift-I>", insert_current_time)
        item("Include Date in System Prompt", None, None)
        item("Copy Title", None, None)

        menu = Menu(self, "View")
        item("Show System Prompt", "<Alt-Shift-S>", ui.system_pane.fold)
        item("Show Tree", "<Alt-Shift-T>", ui.tree_pane.fold)
        item("Show Console", "<Alt-Shift-C>", ui.console_pane.fold)
        item("Count Tokens", "<Control-Alt-m>", ui.count_text_tokens)
        item("Update Window Title", "<Control-u>", ui.update_window_title)
        item("Increase Font Size", "<Control-plus>", lambda e: font_size(1))
        item("Decrease Font Size", "<Control-minus>", lambda e: font_size(-1))
        item("Reset Font Size", "<Control-period>", lambda e: font_size(0))
        item("Toggle Monospace", "<Control-Shift-O>", toggle_font_mono)
        # menu.add_checkbutton(label="Show Cursor line", variable=ui.show_cursor)
        menu.add_separator()
        item("Toggle Scrolling Output", "<Control-o>", toggle_scroll_output)
        item("Ring Bell When Finished", "<Control-Alt-o>", toggle_ring_bell)
        item("Toggle Wrap Lines", "<Control-l>", lambda e: self.it.configure(wrap=(NONE if self.it.cget("wrap") != NONE else WORD)))
        item("Generate Titles", "", None)
        item("Calculate Cost", "", None)

        menu = Menu(self, "Navigate")
        item("Next Similar Line", "<Control-j>", lambda e: self.it.jump_to_similar_line(direction=1))
        item("Previous Similar Line", "<Control-Shift-J>", lambda e: self.it.jump_to_similar_line(direction=-1))
        item("Next Message", "", None)
        item("Previous Message", "", None)

        menu = Menu(self, "Chat")
        item("Next Paragraph", "<Control-Return>", lambda e: ui.complete(1, "\n\n", "\n\n"))
        item("Next Line", "<Shift-Return>", lambda e: ui.complete(1, "\n", "\n"))
        item("Continue Directly", "<Control-space>", lambda e: ui.complete())
        item("Fork Conversation", "<Alt-Return>", lambda e: self.it.fork())
        item("Complete in Branch", "<Control-Shift-Return>", lambda e: branch())
        item("Complete Alternatives", "<Alt-Shift-Return>", lambda e: ui.complete(-1, "\n"))
        menu.add_separator()
        item("Complete 2 Times", "<Control-Key-2>", lambda e: ui.complete(2))
        item("Complete 3 Times", "<Control-Key-3>", lambda e: ui.complete(3))
        item("Complete 5 Times", "<Control-Key-5>", lambda e: ui.complete(5))
        item("Complete Multiple...", "<Control-Shift-M>", lambda e: ui.complete(0))
        item("Complete Multiple Again", "<Control-m>", lambda e: ui.complete(-1))
        menu.add_separator()
        # item("Mark assistant message", "<Control-Alt-a>", mark_assistant_message)
        item("Cancel", "<Escape>", ui.cancelModels)

        menu = Menu(self, "Query")
        item("Max Tokens...", "<Control-Shift-L>", ui.configure_max_tokens)
        item("Temperature...", "<Control-Shift-T>", ui.configure_temperature)
        item("Increase Temperature", "<Alt-plus>", None)
        item("Decrease Temperature", "<Alt-minus>", None)
        item("Temperature 0.0", "<Control-Key-0>", None)
        menu.add_separator()
        item("API Key...", "", None)

        self.models_menu = ModelsMenu(self, ui, "Models")

        menu = Menu(self, "Help")
        item("Test", "<Control-Alt-Shift-T>", menu_test)
        item("Debug Info", "<Control-i>", debug_info)
        item("About", None, None)

        ui.bind("<Control-Button-4>", lambda event: font_size(1))
        ui.bind("<Control-Button-5>", lambda event: font_size(-1))

        ui.bind_class("Text", "<Button-3>", lambda event: show_context_menu(event, edit_menu))
