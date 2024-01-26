import sys
import tkinter as tk
import webbrowser
from datetime import datetime
from os.path import exists
from tkinter import font as tkfont, NONE, WORD, SEL, END, INSERT, SEL_FIRST
from tkinter.messagebox import askokcancel

from AboutDialog import AboutDialog
from Files import Files
from Fonts import Fonts
from Log import Log
from ModelsMenu import ModelsMenu
from TreeSheet import TreeSheet
from WindowsMenu import WindowsMenu
from IterateRangeForm import IterateRangeForm
from Keys import Keys
from Sheet import Sheet
from TooltipableMenu import TooltipableMenu
from MenuBar import MenuBar
from tools import web


class MainMenu(MenuBar):
    def __init__(self, thoughttree, **kw):
        super().__init__(thoughttree)
        self.previous_current_sheet = None
        from thoughttree import Thoughttree
        self.ui: Thoughttree = thoughttree

        self.fixed_model_menu_items = -1
        self.models_menu = None
        # self.create_menu()


    @property
    def it(self) -> TreeSheet:
        return self.ui.it


    def create_menu(self):
        def insert_file(e=None): #todo
            file, text = Files.open_file("Insert File", "chat.txt")
            self.it.insert(INSERT, text)

        def open_file(e=None):
            if self.it.get("1.0", END).strip() != "":
                if not askokcancel("Replace", "Are you sure you want to replace the current text?"):
                    return
            old_file = self.it.file or "document.txt"
            opened = Files.open_file("Open File", old_file)
            if not opened:
                return
            file, text = opened
            self.it.delete("1.0", END)
            self.it.insert("1.0", text)
            self.it.file = file

        def save_file(e=None):
            if self.it.file:
                if exists(self.it.file):
                    if askokcancel("Overwrite", "Are you sure you want to overwrite the current file?"):
                        Files.save_file(self.it.file, self.it.get("1.0", END))

        def save(save_dialog, status_bar_label):
            file_name = save_dialog(self.it)
            if not file_name:
                return
            base_name = file_name.split("/")[-1]
            self.ui.status.note = status_bar_label + base_name
            return base_name

        def save_chat(e=None):
            name = save(Files.save_chat_dialog, "Chat saved to ")
            self.ui.root.title(name)

        def save_section(e=None):
            save(Files.save_section_dialog, "Section saved to ")

        def save_selection(e=None):
            save(Files.save_selection_dialog, "Selection saved to ")

        def save_code_block(e=None):
            save(Files.save_code_block_dialog, "Code block saved to ")

        def new_window(event=None):
            from thoughttree import Thoughttree
            Thoughttree()

        def cut_text(event=None) :
            self.it.event_generate("<<Cut>>")

        def copy_text(event=None) :
            self.it.event_generate("<<Copy>>")

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

        def insert_current_time(event=None):
            self.it.insert(INSERT, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ")

        # def inspect_application(event=None):
        #     from objbrowser import browse
        #     browse(self.ui)
        #
        def debug_info(event=None):
            print(f"{self.focus_get()}")
            return

            import pyautogui
            top = self.ui.winfo_toplevel()
            # top.update_idletasks()

            def screenshot():
                im = pyautogui.screenshot(
                    region=(top.winfo_rootx(), top.winfo_rooty(), top.winfo_width(), top.winfo_height()))
                im.save(datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + "-out.png")
            top.after_idle(screenshot)

            def print_height(w, name=None):
                name = name or w
                print()
                print(f"{name} h: {w.winfo_height()}/req: {w.winfo_reqheight()}")

            print("-------")

            # print_height(self.ui.chat_sheet, "chat_sheet")

            sheet: TreeSheet = self.ui.sheet_tree.sheet
            while sheet:
                print_height(sheet, "sheet: " + str(sheet))
                if sheet.child_notebook:
                    print_height(sheet.child_notebook, "child_notebook: " + str(sheet.child_notebook))
                    sheet = sheet.child_notebook.selected_sheet()
                else:
                    sheet = None

            return "break"


        def branch():
            self.it.fork()
            self.ui.update()
            self.ui.chat()

        def toggle_scroll_output(event=None):
            # if self.ui.scroll_output:
            #     self.it.see(END)
            self.it.see(END)
            self.ui.scroll_output = not self.ui.scroll_output

        def toggle_ring_bell(event=None):
            self.ui.ring_bell_after_completion = not self.ui.ring_bell_after_completion

        def toggle_log_messages_to_console(event=None):
            self.ui.log_messages_to_console = not self.ui.log_messages_to_console

        def toggle_font_mono(event=None):
            font = tkfont.Font(font=self.it.cget("font"))
            size = font.cget("size")
            if font.measure('I') != font.measure('M'):
                family = Fonts.FONT_NAME_MONOSPACE
            else:
                family = Fonts.FONT_NAME_PROPORTIONAL
            self.it.configure(font=(family, size))
            return "break"

        def close_tab(event=None):
            it = self.it
            if type(it) == Sheet:
                it.close_tab()

        def search_web(event=None):
            sheet = self.it
            sel_range = sheet.tag_ranges(SEL)
            if sel_range:
                selected_text = sheet.get(*sel_range)[:2000]
                if selected_text:
                    webbrowser.open_new_tab("https://www.google.com/search?q=" + selected_text)

        ui = self.ui #fixme can not use this with bind_class()

        context = TooltipableMenu(None, "(sheet context menu)")

        file = self.submenu("File")
        file.item("New Window", "<Control-n>", new_window, to="all")
        file.item("New Tab", "<Control-t>", lambda e=None: self.it.fork("1.0"))#, to=TreeSheet)
        file.item("Import Shared Chat", None, None) # , "<Control-....>", import_shared_chat
        file.item("Insert File", "<Control-Shift-e>", insert_file)
        file.item("Open File", "<Control-o>", open_file)
        file.item("Save File", "<Control-s>", save_file)
        file.item("Save Chat", "<Control-Shift-C>", save_chat)
        file.item("Save Message", "<Control-Shift-S>", save_section)
        file.item("Save Selection", "<Alt-S>", save_selection)
        file.item("Save Code Block", "<Control-Alt-s>", save_code_block, menu2=context)
        file.separator()
        file.item("Close Tab", "<Control-w>", close_tab, add=False, to=TreeSheet)
        file.item("Close Empty Tab", "<BackSpace>", lambda e=None: self.it.backspace(e), add=False)
        file.item("Close Window", "<Control-Q>", ui.close, to="all")
        file.item("Quit Thoughttree", "<Control-Shift-Q>", lambda e=None: ui.quit(label="Quit Thoughttree"), to="all")
        file.item("Quit Without Confirmation", "<Control-Alt-Shift-Q>", lambda e=None: sys.exit(0), to="all")


        edit = self.submenu("Edit")
        edit.item("Undo", "<Control-z>", edit_undo, menu2=context)
        edit.item("Redo", "<Control-Shift-Z>", edit_redo, menu2=context)
        edit.separator()
        edit.item("Cut", "<Control-x>", lambda e=None: self.it.event_generate("<<Cut>>"), menu2=context)
        edit.item("Copy", "<Control-c>", lambda e=None: self.it.event_generate("<<Copy>>"), menu2=context)
        edit.item("Paste", "<Control-v>", lambda e=None: self.it.event_generate('<<Paste>>'), menu2=context)
        edit.item("Select All", "<Control-a>", lambda e=None: self.it.event_generate('<<SelectAll>>'), menu2=context)
        edit.item("Select Message", "<Control-Alt-w>", None, menu2=context)
        edit.item("Select Block", "<Control-Shift-w>", None, menu2=context)
        edit.separator()
        edit.item("Find", "<Control-f>", lambda e=None: self.it.find())
        edit.item("Find Next", "<Control-g>", lambda e=None: self.it.find_next())
        edit.item("Find Previous", "<Control-Shift-G>", lambda e=None: self.it.find_previous())
        edit.separator()
        edit.item("Insert Current Time", "<Control-Shift-I>", insert_current_time)
        edit.item("Remove Incomplete", None, None)
        edit.item("Copy Title", None, None)

        view = self.submenu("View")
        view.item("Show System Prompt", "<Alt-Shift-S>", ui.system_pane.fold)
        view.item("Show Tree", "<Alt-Shift-T>", ui.tree_pane.fold)
        view.item("Show Detail", "<Alt-Shift-D>", ui.detail_pane.fold)
        view.item("Show Console", "<Alt-Shift-C>", ui.console_pane.fold)
        view.item("Show Status Bar", "<Alt-Shift-I>", ui.status_hider.hide)
        view.item("Full Screen", "<F11>", ui.toggle_fullscreen)
        view.item("Update Window Title", "<Control-u>", ui.update_window_title)
        view.item("Update Tab Title", "<Control-Shift-B>", ui.sheet_tree.update_tab_title, menu2=context)
        view.item("Model Usage", None, web("https://platform.openai.com/account/usage"))
        view.separator()
        view.item("Increase Font Size", "<Control-plus>", lambda e=None: Sheet.font_size_all(1))
        view.item("Decrease Font Size", "<Control-minus>", lambda e=None: Sheet.font_size_all(-1))
        view.item("Reset Font Size", "<Control-period>", lambda e=None: Sheet.font_size_all(0))
        view.item("Toggle Monospace", "<Control-Shift-O>", toggle_font_mono)
        view.separator()
        view.item("Toggle Scrolling Output", "<Control-e>", toggle_scroll_output)
        view.item("Ring Bell When Finished", "<Control-Alt-o>", toggle_ring_bell)
        view.item("Toggle Wrap Lines", "<Control-l>", lambda e=None: self.it.configure(wrap=(NONE if self.it.cget("wrap") != NONE else WORD)))
        view.item("Calculate Cost", None, None)
        view.item("Show Hidden Prompts", "<Control-Shift-H>", ui.toggle_show_hidden_prompts)
        view.item("Show Messages", None, toggle_log_messages_to_console)

        mask = self.submenu("Mask")
        mask.item("All", None, None)
        mask.item("None", None, None)
        mask.item("Invert", None, None)
        mask.item("Selection", "<Alt-Shift-M>", lambda e=None: self.it.toggle_tag("mask"))

        navigate = self.submenu("Navigate")
        # navigate.item("Next Panel", "<Control-Tab>", lambda e=None: self.tk_focusNext().focus_set())#  .widget.sheet_tree.tk_focusPrev() or e.widget.tk_focusPrev())
        navigate.item("Previous Panel", "<Control-Shift-Tab>", lambda e=None: self.tk_focusPrev().focus_set())
        navigate.item("Next Sheet", "<Tab>", lambda e=None: e.widget.focusNextSheet())
        navigate.item("Previous Sheet", "<Shift-Tab>", lambda e=None: e.widget.focusPrevSheet())
        navigate.item("Next Tab", "<Control-Next>", lambda e=None: e.widget.focusNextTab(), to=TreeSheet)#  .widget.sheet_tree.tk_focusPrev() or e.widget.tk_focusPrev())
        navigate.item("Previous Tab", "<Control-Prior>", lambda e=None: e.widget.focusPrevTab(), to=TreeSheet)
        navigate.item("Next Similar Line", "<Control-j>", lambda e=None: self.it.jump_to_similar_line(direction=1))
        navigate.item("Previous Similar Line", "<Control-Shift-J>", lambda e=None: self.it.jump_to_similar_line(direction=-1))
        navigate.separator()
        navigate.item("Search with Google", "<Control-Alt-g>", search_web, menu2=context)
        context.separator()

        chat = self.submenu("Chat")
        chat.item("Continue Line", "<Control-space>", lambda e=None: ui.chat(inline=True))
        chat.item("Next Line", "<Shift-Return>", lambda e=None: ui.chat(1, "\n", "\n"))
        chat.item("Next Paragraph", "<Control-Return>", lambda e=None: ui.chat(1, "\n\n", "\n\n"))
        chat.item("Fork Conversation", "<Control-Alt-F>", lambda e=None: self.it.fork())
        chat.item("Complete in Branch", "<Control-Shift-Return>", lambda e=None: branch())
        chat.separator()
        chat.item("Complete Alternatives", "<Alt-Shift-Return>", lambda e=None: ui.chat(-1, "\n"))
        chat.item("Insert Completion", "<Control-Alt-space>", lambda e=None: ui.chat(insert=True), menu2=context)
        chat.item("Replace by Completion", "<Control-Shift-space>", lambda e=None: ui.chat(replace=True), menu2=context)
        chat.item("Refer to cursor location", "<Control-Alt-o>", lambda e=None: ui.chat(1, "\n\n", "\n", location=True))
        chat.separator()
        context.separator()
        chat.item("Complete 3 Times", "<Control-Alt-Key-3>", lambda e=None: ui.chat(3), add=True)
        [self.bind_class("Text", f"<Control-Alt-Key-{digit}>", lambda e=None, i=digit: ui.chat(i)) for digit in [2, 4, 5, 6, 7, 8, 9]]
        chat.item("Complete Multiple...", "<Control-Shift-M>", lambda e=None: ui.chat(0))
        chat.item("Complete Multiple Again", "<Control-m>", lambda e=None: ui.chat(-1))
        chat.separator()
        # chat.item("Mark as Assistant Message", "<Control-Alt-a>", mark_as_assistant_message)
        chat.item("Cancel", "<Escape>", ui.cancel_models)


        prompt = self.submenu("Prompt")
        prompt.item("Solve this Problem", "<Alt-Return>", None, menu2=context)
        prompt.item("Ask About This", "<Control-Shift-A>", ui.ask, menu2=context)
        prompt.item("Improve", "<Control-I>", ui.improve, menu2=context)
        prompt.item("Drill Down", "<Control-D>", ui.drill_down, menu2=context)
        prompt.item("Remove from Text")
        prompt.item("Select Text")
        prompt.item("Change Text")
        prompt.item("Annotate Text")
        prompt.item("Comment Text")
        prompt.item("Insert transitioning sentence")
        prompt.item("Insert Emoji")
        prompt.item("Iterate Over Range", "<Control-Alt-I>", lambda e=None: IterateRangeForm(self.it))
        prompt.separator()
        prompt.item('Prompt "ok"', "<Control-Alt-K>", lambda e=None: ui.chat(hidden_command="ok"))
        prompt.item('Prompt "next"', "<Control-Alt-N>", lambda e=None: ui.chat(hidden_command="next"))
        prompt.item('Prompt "continue"', "<Control-Alt-U>", lambda e=None: ui.chat(hidden_command="continue"))
        prompt.separator()
        prompt.item("Automatically continue")
        prompt.item("Continue until...")



        query = self.submenu("Query")
        query.item("Temperature...", "<Control-Shift-T>", ui.configure_temperature)
        query.item("Increase Temperature", None, None)
        query.item("Decrease Temperature", None, None)
        query.item("Temperature 0.0", None, None)
        query.item("Max Tokens...", "<Control-Shift-L>", ui.configure_max_tokens)
        query.item("API Key...", None, None)


        text = self.submenu("Text")
        text.item("Count Tokens", "<Control-Alt-m>", ui.count_text_tokens)
        text.item("Run Code Block", "<Control-Shift-R>", lambda e=None: self.it.run_code_block(), menu2=context)
        text.separator()
        text.item('Role "system"', None, lambda e=None: self.it.role("system"))
        text.item('Role "user"', None, lambda e=None: self.it.role("user"))
        text.item('Role "assistant"', None, lambda e=None: self.it.role("assistant"))
        text.item('Role "function"', None, lambda e=None: self.it.role("function"))
        text.separator()
        text.item('Duplicate Tab', None, lambda e=None: self.it.role("function"))


        format_menu = self.submenu("Format")
        format_menu.item("Bold", "<Control-b>", lambda e=None: self.it.toggle_tag("bold"))
        format_menu.item("Strikethrough", "<Control-d>", lambda e=None: self.it.toggle_tag("strikethrough"))

        self.models_menu = self.add_menu(ModelsMenu(self, ui, "Models"))

        self.add_menu(WindowsMenu(self, "Windows"))

        help_menu = self.submenu("Help")
        help_menu.item("Introduction", "<Shift-F1>", None)
        help_menu.item("Text Keymap", "<F1>", lambda e=None: Keys.show_text_keys_help(self.ui))
        help_menu.item("Technical documentation", "<F2>", web("https://platform.openai.com/docs/introduction"))
        help_menu.item("OpenAI Chat API", None, web("https://platform.openai.com/docs/api-reference/chat"))
        help_menu.item("GPT Models", None, web("https://platform.openai.com/docs/models"))
        help_menu.item("OpenAI Pricing", None, web("https://openai.com/pricing"))
        help_menu.item("Debug Info", "<Control-Alt-Shift-I>", debug_info, to="all")
        # help_menu.item("Inspect Application", "<Control-Alt-Shift-B>", inspect_application)
        help_menu.item("About", "<Control-F1>", lambda e=None: AboutDialog(self.ui))

        ui.bind_class("Text", "<Control-Button-4>", lambda e=None: Sheet.font_size_all(1))
        ui.bind_class("Text", "<Control-Button-5>", lambda e=None: Sheet.font_size_all(-1))

        ui.bind_class("Text", "<Button-3>", context.show_context_menu)
        ui.bind_class("Text", "<Menu>", context.show_context_menu)




'''
Recht gute Wahl für underline Werte für menuitems.
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
