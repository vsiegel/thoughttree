import tkinter as tk
from datetime import datetime
from tkinter import font as tkfont, NONE, WORD

import prompts
from Files import Files
from Menu import Menu
from Text import Text
from tools import list_all_bindings, add_bboxes


class ThoughttreeMenu(Menu):
    def __init__(self, thoughttree, new_window_callback):
        super().__init__(thoughttree, tearoff=0)
        self.new_window_callback = new_window_callback
        self.ui = thoughttree
        self.create_menu()


    @property
    def it(self) -> Text:
        return self.ui.focus_get()


    def create_menu(self):

        def save(save_dialog, status_bar_label):
            file_name = save_dialog(self.ui.chat)
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

        def save_code_block(e=None):
            save(Files.save_code_block_dialog, "Code block saved to ")

        def new_window(event=None) :
            self.new_window_callback()

        def show_context_menu(event, menu) :
            widget = self.ui.winfo_containing(event.x_root, event.y_root)
            if widget :
                widget.focus_set()
            menu.tk_popup(event.x_root, event.y_root)

        def cut_text(event=None) :
            self.it.event_generate("<<Cut>>")

        def copy_text(event=None) :
            self.it.event_generate("<<Copy>>")

        def paste_text(event=None) :
            txt = self.it
            txt.event_generate("<<Clear>>")
            txt.event_generate("<<Paste>>")
            txt.see(tk.INSERT)

        def select_all(event=None):
            txt = self.it
            if type(txt) == Text:
                txt.tag_add(tk.SEL, "1.0", tk.END)
                txt.mark_set(tk.INSERT, "1.0")
                txt.see(tk.INSERT)

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
            self.it.insert(tk.INSERT, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        def debug_info(event=None):

            print(f"{self.it=}")
            print(f"{self.it.cget('font')=}")


            return
            # print(f"{list_all_bindings(self.tt)=}")
            print(f"{self.it.bbox(tk.INSERT)=}")
            print(f"{self.it.dlineinfo(tk.INSERT)=}")
            print(f"{self.it.tag_ranges(tk.SEL)=}")

            print(f'{self.it.compare(tk.INSERT, "==", tk.END)=}')
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
            dumped = self.it.dump("1.0", tk.INSERT, all=True)
            for item in dumped:
                print(f'{item=}')


        def menu_test(event=None):

            def on_text_change(event):
                print(event)
                new_height = int(txt.index('end-1c').split('.')[0]) + 1
                print(f"{new_height=}")
                txt.configure(height=new_height)
                txt.edit_modified(False)


            def on_resize(event):
                char_width = tkfont.Font(font=txt.cget("font")).measure('0')
                parent_width = event.width
                txt.configure(width=int(parent_width / char_width))

            print(event)
            frame = tk.Frame(self.it)
            txt = Text(frame)
            txt.pack(fill='both', expand=True)
            self.it.window_create(tk.END, window=frame)

            self.it.bind('<Configure>', on_resize)
            txt.bind('<<Modified>>', on_text_change)
            pass

        def branch_conversation():
            self.it.split_conversation()
            self.ui.update()
            self.ui.complete()

        def item(label, keystroke, command, bind_key=True, context_menu=None, variable=None):
            menu.item(label, keystroke, command, bind_key, context_menu, variable)

        def toggle_show_system_prompt(event=None):
            print(f"{event=}")
            print(f"{self=}")
            current = self.ui.system_and_chat_pane.sash_coord(0)
            print(f"{current=}")
            if current[1] > 1:
                print(f"Open:  {self.ui.system_and_chat_pane_old_sash=}")
                self.ui.system_and_chat_pane_old_sash = current
                self.ui.system_and_chat_pane.sash_place(0, 1, 1)
            else:
                print(f"Closed {self.ui.system_and_chat_pane_old_sash=}")
                x, y = self.ui.system_and_chat_pane_old_sash
                self.ui.system_and_chat_pane.sash_place(0, x ,y)

        def toggle_scroll_output(event=None):
            self.ui.scroll_output = not self.ui.scroll_output

        def toggle_font_mono(event=None):
            font = tkfont.Font(font=self.it.cget("font"))
            size = font.cget("size")
            if font.measure('I') != font.measure('M'):
                family = Text.FONT_NAME_MONOSPACE
            else:
                family = Text.FONT_NAME_PROPORTIONAL
            self.it.configure(font=(family, size))
            return "break"


        menu = Menu(self, "File")
        item("New Window", "<Control-n>", new_window)
        # item("Save Chat", "<Control-s>", Files.save_chat)
        item("Save Chat", "<Control-s>", save_chat)
        item("Save Section", "<Control-Shift-S>", save_section)
        item("Save Code Block", "<Control-Alt-s>", save_code_block)
        item("Quit", "<Control-q>", self.ui.close)

        menu = Menu(self, "Edit")
        edit_menu = menu
        item("Cut", "<Control-x>", cut_text)
        item("Copy", "<Control-c>", copy_text)
        item("Paste", "<Control-v>", paste_text)
        menu.add_separator()
        item("Undo", "<Control-z>", edit_undo)
        item("Redo", "<Control-Shift-Z>", edit_redo)
        item("Select All", "<Control-a>", select_all)
        menu.add_separator()
        item("Insert Current Time", "<Control-Shift-I>", insert_current_time)

        menu = Menu(self, "View")
        item("Show System Prompt", "<Alt-Shift-P>", toggle_show_system_prompt)
        item("Show Tree", "", None)
        item("Count Tokens", "<Control-t>", self.ui.count_text_tokens)
        item("Run Code Block", "", None)
        item("Update Window Title", "<Control-u>", self.ui.update_window_title)
        item("Increase Font Size", "<Control-plus>", lambda e: font_size(1))
        item("Decrease Font Size", "<Control-minus>", lambda e: font_size(-1))
        item("Reset Font Size", "<Control-period>", lambda e: font_size(0))
        item("Toggle Monospace", "<Control-Shift-O>", toggle_font_mono)
        menu.add_separator()
        item("Toggle Scrolling Output", "<Control-o>", toggle_scroll_output)
        item("Toggle Wrap Lines", "<Control-l>", lambda e: self.it.configure(wrap=(NONE if self.it.cget("wrap") != NONE else WORD)))
        item("Generate Titles", "", None)
        item("Calculate Cost", "", None)

        menu = Menu(self, "Navigate")
        item("Split Conversation", "<Control-b>", lambda e: self.it.split_conversation())
        item("Jump to Similar Line", "<Control-Shift-J>", lambda e: self.it.jump_to_similar_line(-1))
        item("Jump to Similar Line", "<Control-j>", lambda e: self.it.jump_to_similar_line(1))

        menu = Menu(self, "Chat")
        item("Send Chat Message", "<Control-Return>", lambda e: self.ui.complete(1, "\n\n", "\n\n"))
        item("Complete Directly", "<Control-space>", lambda e: self.ui.complete())
        item("Complete in Branch", "<Alt-Return>", lambda e: branch_conversation())
        item("Continue Alternatives", "<Alt-Shift-Return>", lambda e: self.ui.complete(-1, "\n"))
        menu.add_separator()
        item("Complete 2 Times", "<Control-Key-2>", lambda e: self.ui.complete(2))
        item("Complete 3 Times", "<Control-Key-3>", lambda e: self.ui.complete(3))
        item("Complete 5 Times", "<Control-Key-5>", lambda e: self.ui.complete(5))
        item("Complete Multiple...", "<Control-Shift-M>", lambda e: self.ui.complete(0))
        item("Complete Multiple Again", "<Control-m>", lambda e: self.ui.complete(-1))
        item("Cancel", "<Escape>", self.ui.cancelModels)

        menu = Menu(self, "Model")
        self.models_items(item)
        menu.add_separator()
        item("Max Tokens...", "<Control-Shift-L>", lambda e: self.ui.configure_max_tokens())
        item("Temperature...", "<Control-Shift-T>", lambda e: self.ui.configure_temperature())
        item("Increase Temperature", "<Alt-plus>", None)
        item("Decrease Temperature", "<Alt-minus>", None)
        item("Temperature 0.0", "<Control-Key-0>", None)
        menu.add_separator()
        item("API Key...", "", None)

        menu = Menu(self, "Help")
        item("Test", "<Alt-Shift-T>", menu_test)
        item("Debug Info", "<Control-i>", debug_info)
        item("About", None, None)

        self.ui.bind("<Control-Button-4>", lambda event: font_size(1))
        self.ui.bind("<Control-Button-5>", lambda event: font_size(-1))

        self.ui.bind_class("Text", "<Button-3>", lambda event: show_context_menu(event, edit_menu))


    def models_items(self, item):
        for model_name in self.ui.model.get_available_models():
            if model_name == "gpt-4":
                key = "<Control-Alt-Key-4>"
            elif model_name == "gpt-3.5-turbo":
                key = "<Control-Alt-Key-3>"
            else:
                key = None
            item(f"{model_name}", key, lambda e, m=model_name: self.ui.set_model(m))
