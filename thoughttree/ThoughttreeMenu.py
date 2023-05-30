import tkinter as tk
from datetime import datetime
from tkinter import font as tkfont

import prompts
from ChatFileManager import ChatFileManager
from Menu import Menu
from Text import Text


class ThoughttreeMenu(Menu):
    def __init__(self, thoughttree, new_window_callback):
        super().__init__(thoughttree.root, tearoff=0)
        self.new_window_callback = new_window_callback
        self.tt = thoughttree
        self.root = thoughttree.root
        self.create_menu()


    @property
    def focus(self) -> Text:
        return self.root.focus_get()


    def create_menu(self):

        def save(save_dialog, status_bar_label):
            file_name = save_dialog(self.tt.chat)
            if not file_name:
                return
            base_name = file_name.split("/")[-1]
            self.tt.status_bar.main_text(status_bar_label + base_name)
            return base_name

        def save_chat(e=None):
            name = save(ChatFileManager.save_chat_dialog, "Chat saved to ")
            self.root.title(name)

        def save_section(e=None):
            save(ChatFileManager.save_section_dialog, "Section saved to ")

        def save_code_block(e=None):
            save(ChatFileManager.save_code_block_dialog, "Code block saved to ")

        def new_window(event=None) :
            self.new_window_callback()

        def show_context_menu(event, menu) :
            widget = self.root.winfo_containing(event.x_root, event.y_root)
            if widget :
                widget.focus_set()
            menu.tk_popup(event.x_root, event.y_root)

        def cut_text(event=None) :
            self.focus.event_generate("<<Cut>>")

        def copy_text(event=None) :
            self.focus.event_generate("<<Copy>>")

        def paste_text(event=None) :
            text = self.focus
            text.event_generate("<<Paste>>")
            text.see(tk.INSERT)

        def select_all(event=None):
            txt = self.focus
            if type(txt) == Text:
                txt.tag_add(tk.SEL, "1.0", tk.END)
                txt.mark_set(tk.INSERT, "1.0")
                txt.see(tk.INSERT)

        def edit_undo(event=None):
            try:
                self.focus.edit_undo()
            except tk.TclError:
                pass # nothing to undo

        def edit_redo(event=None):
            try:
                self.focus.edit_redo()
            except tk.TclError:
                pass # nothing to redo

        def change_text_size(delta):
            txt = self.focus
            if delta == 0:
                name, size = Text.FONT
            else:
                name, size = txt.cget("font").split()
            txt.config(font=(name, int(size) + delta))

        def insert_current_time(event=None):
            self.focus.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        def debug_info(event=None):

            def add_bboxes(bbox1, bbox2):
                x1, y1, w1, h1 = bbox1
                x2, y2, w2, h2 = bbox2
                x = min(x1, x2)
                y = min(y1, y2)
                w = max(x1 + w1, x2 + w2) - x
                h = max(y1 + h1, y2 + h2) - y
                return x, y, w, h

            bbox_start = self.focus.bbox('1.0')
            bbox_end = self.focus.bbox("end - 1 char")
            total_bbox = add_bboxes(bbox_start, bbox_end)
            print(f"{bbox_start=}")
            print(f"{bbox_end=}")
            print(f"{total_bbox=}")
            dlineinfo_start = self.focus.dlineinfo('1.0')[:4]
            dlineinfo_end = self.focus.dlineinfo("end - 1 char")[:4]
            total_dlineinfo = add_bboxes(dlineinfo_start, dlineinfo_end)
            print(f"{dlineinfo_start=}")
            print(f"{dlineinfo_end=}")
            print(f"{total_dlineinfo=}")
            print(f"{self.focus.bbox(tk.INSERT)=}")
            print(f"{self.focus.dlineinfo(tk.INSERT)=}")
            print(f"{self.focus.tag_ranges(tk.SEL)=}")

            print(f'{self.focus.compare(tk.INSERT, "==", tk.END)=}')
            dumped = self.focus.dump("insert - 1 char", window=True)
            print(f'{ dumped=}')
            if dumped:
                print(f'{dumped[0][1].endswith("label")=}')
                # print(f'{self.focus.window_configure("insert - 1 char" )=}')
            print()

        def menu_test(event=None):
            frame = tk.Frame(self.focus)
            txt = Text(frame)
            txt.pack(fill='both', expand=True)
            self.focus.window_create(tk.END, window=frame)
            txt.insert(tk.END, prompts.TITLE_GENERATION_PROMPT)


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


            # Bind the <Configure> event to the on_resize function
            self.focus.bind('<Configure>', on_resize)

            txt.bind('<<Modified>>', on_text_change)
            pass

        def item(label, keystroke, command, bind_key=True, context_menu=None):
            menu.item(label, keystroke, command, bind_key, context_menu)

        bar = Menu(self.tt.root)

        menu = Menu(bar, "File")
        item("New Window", "<Control-n>", new_window)
        item("Load Chat", None, lambda: ChatFileManager.load_chat_dialog(self.tt.chat))
        item("Save Chat", "<Control-s>", save_chat)
        item("Save Section", "<Control-Shift-S>", save_section)
        item("Save Code Block", "<Control-Shift-B>", save_code_block)
        item("Quit", "<Control-q>", self.tt.close)

        menu = Menu(bar, "Edit")
        edit_menu = menu
        item("Cut", "<Control-x>", cut_text)
        item("Copy", "<Control-c>", copy_text)
        item("Paste", "<Control-v>", paste_text)
        menu.add_separator()
        item("Undo", "<Control-z>", edit_undo)
        item("Redo", "<Control-Shift-Z>", edit_redo)
        item("Select All", "<Control-a>", select_all)
        menu.add_separator()
        item("Insert Current Time", "<Alt-Shift-T>", insert_current_time)

        menu = Menu(bar, "View")
        item("Show System Prompt", "", None)
        item("Show Tree", "", None)
        item("Count Tokens", "<Control-t>", self.tt.count_tokens)
        item("Run Code Block", "", None)
        item("Update Window Title", "<Control-u>", self.tt.update_window_title)
        item("Increase Font Size", "<Control-plus>", lambda e: change_text_size(1))
        item("Decrease Font Size", "<Control-minus>", lambda e: change_text_size(-1))
        item("Reset Font Size", "<Control-period>", lambda e: change_text_size(0))
        self.root.bind("<Control-Button-4>", lambda event: change_text_size(1))
        self.root.bind("<Control-Button-5>", lambda event: change_text_size(-1))

        menu = Menu(bar, "Navigate")
        item("Jump to Similar Line", "<Control-j>", self.tt.jump_to_similar_line)

        menu = Menu(bar, "Model")
        item("Send Chat Message", "<Control-Return>", lambda e: self.tt.chat_continue("\n\n", "\n\n"))
        item("Complete Directly", "<Shift-Return>", lambda e: self.tt.chat_continue("", ""))
        menu.add_separator()
        item("Complete 2 Times", "<Control-Key-2>", lambda e: self.tt.chat_continue("", "", 2))
        item("Complete 3 Times", "<Control-Key-3>", lambda e: self.tt.chat_continue("", "", 3))
        item("Complete 5 Times", "<Control-Key-5>", lambda e: self.tt.chat_continue("", "", 5))
        item("Complete Multiple...", "<Control-m>", lambda e: self.tt.chat_continue("", "", 0))
        item("Complete Multiple Again", "<Alt-Return>", lambda e: self.tt.chat_continue("", "", -1))
        item("Cancel", "<Escape>", self.tt.gpt.cancel)
        menu.add_separator()
        for model_name in self.tt.gpt.get_available_models() :
            if model_name == "gpt-4":
                key = "<Control-Alt-Key-4>"
            elif model_name == "gpt-3.5-turbo":
                key = "<Control-Alt-Key-3>"
            else:
                key = None
            item(f"{model_name}", key, lambda e, m=model_name: self.tt.set_model(m))

        menu = Menu(bar, "Help")
        item("Test", "<Control-Shift-T>", menu_test)
        item("Debug Info", "<Control-i>", debug_info)
        item("About", None, None)

        self.root.bind_class("Text", "<Button-3>", lambda event: show_context_menu(event, edit_menu))
