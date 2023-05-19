#!/usr/bin/env python
import os
import tkinter as tk
from argparse import Namespace
from tkinter import ttk, font
from tkinter import font as tkfont
from tkinter.messagebox import showinfo, showerror
from tkinter.scrolledtext import ScrolledText

from tkinter import filedialog

from ToolTip import ToolTip
from GPT import GPT
from StatusBar import StatusBar
from Menu import Menu

CHATGPT_ICON = "chatgpt-icon.png"

DEFAULT_SYSTEM_PROMPT_FILE = "thoughttree-system.txt"
system_prompt = """Allways be terse.
Never apologize.
Use markdown to make it more readable.
"""
# open(DEFAULT_SYSTEM_PROMPT_FILE, 'r').read()

conf = Namespace()
conf.show_finish_reason = True
conf.ring_bell_after_completion = False
conf.scroll_during_completion = True

#NODE_OPEN = '\u25B6'
#NODE_CLOSED = '\u25BC'
NODE_OPEN = '*'
NODE_CLOSED = '|'


class ChatFileManager:
    @staticmethod
    def save_chat(text_widget, filename) :
        # ROLE_SYMBOLS = {"user":"❯ ", "ai":"⚙ "}
        ROLE_SYMBOLS = {"user":"", "ai":""}
        content = text_widget.dump(1.0, tk.END, text=True, tag=True)
        with open(filename, 'w') as f :
            drop_nl = False
            for item in content :
                if item[0] == "tagon" :
                    if item[1] == "assistant" :
                        f.write(ROLE_SYMBOLS["ai"])
                elif item[0] == "tagoff" :
                            if item[1] == "assistant" :
                                f.write("\n" + ROLE_SYMBOLS["user"])
                                drop_nl = True
                elif item[0] == "text" :
                    if drop_nl :
                        drop_nl = False
                        if item[1] == "\n":
                            continue
                    f.write(item[1])

    @staticmethod
    def save_chat_dialog(text_widget) :
        file = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile="chat.txt", title="Save chat")
        if file :
            ChatFileManager.save_chat(text_widget, file)
        return file

    @staticmethod
    def save_code_section(text_widget: tk.Text, filename, index=tk.INSERT) :
        try :
            range = text_widget.tag_prevrange("assistant", index)#[0]
            if not range :
                raise Exception("No code section found")
            code_message = text_widget.get(*range)
            with open(filename, 'w') as f :
                f.write(code_message)
        except Exception as e :
            showerror(title="Error", message="Cannot save code section\n" + str(e))

    @staticmethod
    def save_code_section_dialog(text_widget) :
        file = filedialog.asksaveasfilename(
            defaultextension=".py", initialfile="code-section.py", title="Save code section")
        if file :
            ChatFileManager.save_code_section(text_widget, file)
        return file

    @staticmethod
    def load_chat(text_widget, filename) :
        with open(filename, 'r') as f :
            content = f.readlines()

        text_widget.delete(1.0, tk.END)
        for line in content:
            if ':' in line:
                tag, text = line.strip().split(': ', 1)
                text_widget.insert(tk.END, text)
                text_widget.tag_add(tag, text_widget.index(tk.END + '-1c linestart'), text_widget.index(tk.END + '-1c lineend'))
            else:
                text_widget.insert(tk.END, line)

    @staticmethod
    def load_chat_dialog(text_widget) :
        file = filedialog.askopenfilename(defaultextension=".txt")
        if file :
            ChatFileManager.load_chat(text_widget, file)


class Thoughttree:
    MIN_WIDTH = 250
    MIN_HEIGHT = 100
    CHAT_WIDTH = 400
    ROOT_GEOMETRY = "1000x600"
    TEXT_FONT = ("monospace", 10)
    finish_reasons = {
        "stop" : {"symbol": "", "tool_tip": ""},
        "length" : {"symbol": "…", "tool_tip": "The completion reatched max_tokens tokens. It can be continued."},
        "canceled" : {"symbol": "☒", "tool_tip": "The completion was canceled."},
        "error": {"symbol": "⚠", "tool_tip": "An error occurred while processing the completion."},
    }

    def __init__(self, root):
        self.root = root
        self.gpt = GPT()
        self.is_root_destroyed = False
        self.root.protocol("WM_DELETE_WINDOW", self.on_root_close)
        self.set_icon()
        self.create_ui()

    def set_icon(self) :
        def get_icon_file_name(icon_file_name) :
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), icon_file_name)

        try :
            abs_name = str(get_icon_file_name(CHATGPT_ICON))
            self.root.iconphoto(False, tk.PhotoImage(file=abs_name)) # Note: has no effect when running in PyCharm IDE
        except Exception as e :
            print("Error loading icon:", e)

    def set_model(self, model_name) :
        if model_name in self.gpt.get_available_models() :
            self.gpt.set_model(model_name)
            self.status_bar.set_right_text(model_name)
        else :
            showerror(title="Error", message=f"Invalid model: {model_name}")

    def on_root_close(self) :
        self.is_root_destroyed = True
        self.root.destroy()

    def new_window(self, event=None):
        Thoughttree(tk.Tk())

    def show_context_menu(self, event) :
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def cut_text(self, event=None) :
        self.chat.event_generate("<<Cut>>")

    def copy_text(self, event=None) :
        self.chat.event_generate("<<Copy>>")

    def paste_text(self, event=None) :
        self.chat.event_generate("<<Paste>>")

    def create_ui(self):
        self.root.title("Thoughttree")

        font_sizes = {
            # "TkDefaultFont" : 10,
            # "TkTextFont" : 24,
            # "TkFixedFont" : 24,
            "TkMenuFont" : 24,
            # "TkHeadingFont" : 24,
            # "TkCaptionFont" : 24,
            # "TkSmallCaptionFont" : 24,
            # "TkIconFont" : 24,
            # "TkTooltipFont" : 24
        }
        for fontname, size in font_sizes.items() :
            default_font = font.nametofont(fontname)
            default_font.configure(size=size, family="Arial")

        self.root.geometry(Thoughttree.ROOT_GEOMETRY)
        self.root.minsize(Thoughttree.MIN_WIDTH, Thoughttree.MIN_HEIGHT)
        font_height = tkfont.Font(font=Thoughttree.TEXT_FONT).metrics("linespace")
        style = ttk.Style(self.root)

        style.configure("Treeview", rowheight=2 * font_height + 0)
        # style.configure("Treeview", font=Thoughttree.TEXT_FONT)
        style.configure("Treeview.Cell", anchor=tk.NW)
        style.configure("Treeview.Cell", padding=(1, 1))

        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.set_right_text(self.gpt.model)
        self.status_bar.set_main_text(f"Max tokens: {self.gpt.max_tokens} T: {self.gpt.temperature}")

        SASHWIDTH = 8
        self.hPaned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=SASHWIDTH)
        self.hPaned.pack(fill=tk.BOTH, expand=True)
        self.vPaned = tk.PanedWindow(self.hPaned, orient=tk.VERTICAL, sashwidth=SASHWIDTH)

        tree = ttk.Treeview(self.hPaned, columns=("C1"), show="tree")
        self.tree = tree
        tree.column("#0", width=160, minwidth=60, anchor=tk.W, stretch=tk.NO)
        tree.column("#1", width=30, minwidth=60, anchor=tk.W, stretch=tk.NO)
        tree.heading("C1", text="")

        self.current_cell_editor = None

        #UNICODE = tkfont.Font(family="unicode", size=10)
        #tree.tag_configure('closed', font=UNICODE, foreground='blue')
        #tree.tag_configure('leaf', font=UNICODE)

        # Bind the click event to toggle the tree handle icon
        def on_treeview_click(event) :
            item = tree.identify('item', event.x, event.y)
            print(item)
            if item :
                if 'closed' in tree.item(item, 'tags') :
                    replaced = tree.item(item, 'text').replace(NODE_CLOSED, NODE_OPEN, 1)
                    print(replaced)
                    tree.item(item, text=replaced)
                    tree.item(item, tags='opened')
                elif 'opened' in tree.item(item, 'tags') :
                    tree.item(item, text=tree.item(item, 'text').replace(NODE_OPEN, NODE_CLOSED, 1))
                    tree.item(item, tags='closed')

        #tree.bind('<Double-Button-1>', on_treeview_click)

        self.create_dummy_data(tree)
        tree.bind_class("Treeview", "<KeyPress-Return>", lambda _ : None)
        tree.bind_class("Treeview", "<KeyRelease-Return>", lambda _ : None)
        # tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        self.hPaned.add(tree)
        self.hPaned.add(self.vPaned)
        self.hPaned.sash_place(0, 0, 0)

        tree.focus(tree.get_children()[0])
        tree.bind("<Double-Button-1>", self.edit_tree_entry)
        tree.bind("<Return>", self.edit_tree_entry)


        self.system_txt = self.create_textbox(self.vPaned, system_prompt)
        self.system_txt.config(pady=5)

        self.chat = self.create_textbox(self.vPaned, "")

        self.vPaned.add(self.system_txt)
        self.vPaned.add(self.chat)
        self.chat.focus_set()

        self.create_menu()

    def create_menu(self) :
        def save_file(e=None) :
            file_name = ChatFileManager.save_chat_dialog(self.chat)
            if not file_name:
                return
            base_name = file_name.split("/")[-1]
            self.root.title(base_name)

        def save_code_section(e=None):
            file_name = ChatFileManager.save_code_section_dialog(self.chat)
            if not file_name:
                return
            # base_name = file_name.split("/")[-1]
            self.status_bar.set_main_text("Code section saved to " + file_name)

        def select_all(event=None):
            focus = self.root.focus_get()
            if type(focus) == tk.scrolledtext.ScrolledText :
                focus.tag_add(tk.SEL, "1.0", tk.END)
                focus.mark_set(tk.INSERT, "1.0")
                focus.see(tk.INSERT)

        def update_window_title(event=None):
            progress_title = "[Generating...]"

            def output_response_delta_to_title(content):
                if self.is_root_destroyed:
                    return
                current_title = self.root.title()
                if current_title == progress_title:
                    current_title = ""
                self.root.title(current_title + content)
                self.chat.update()

            self.root.title(progress_title)
            self.chat.update()
            history = self.chat_history_from_textboxes(
                "A title for this conversation, about 70 characters. Style does not matter,"
                " it is about the information. Ignore the system prompt. Do not refer to the content of the system prompt."
                " If there is no chat history, the title will be empty."
                " It is used as a one line title for this conversation."
                " Give me only the unquoted text of the title, without any prefixes or comments:")
            self.gpt.chat_complete(history, output_response_delta_to_title, 30, 1)

        def menu_test(event=None):
            notebook = ttk.Notebook(self.chat, height=200, padding=(0, 0, 0, 0))
            t1 = self.create_textbox(notebook, "Foo")
            t2 = self.create_textbox(notebook, "Bar")
            t1.configure(height=20, padx=0, pady=0)
            t2.configure(height=20, padx=0, pady=0)
            notebook.add(t1, text='One')
            notebook.add(t2, text='Two')

            def insert_with_newline(txt, widget, pos="insert") :
                txt.insert(pos, '\n')
                txt.window_create(pos, window=widget)
                txt.insert(pos, '\n')

            insert_with_newline(self.chat, notebook)
            insert_with_newline(self.chat, tk.Label(self.chat, text="Foo"), tk.INSERT + " + 2 lines")

        bar = Menu(self.root)

        menu = Menu(bar, "File")
        menu.item("New Window", "<Control-n>", self.new_window)
        menu.item("Load Chat", None, lambda : ChatFileManager.load_chat_dialog(self.chat))
        menu.item("Save Chat", "<Control-s>", save_file)
        menu.item("Save Code Section", "<Control-Shift-s>", save_code_section)
        menu.item("Quit", "<Control-q>", self.close)

        context = self.context_menu = Menu(self.chat)
        context.item("Undo", "<Control-z>", self.chat.edit_undo, False)
        context.item("Redo", "<Control-Shift-z>", self.chat.edit_redo, False)
        context.add_separator()
        context.item("Cut", "<Control-x>", self.cut_text, False)
        context.item("Copy", "<Control-c>", self.copy_text, False)
        context.item("Paste", "<Control-v>", self.paste_text, False)

        menu = Menu(bar, "Edit")
        menu.item("Undo", "<Control-z>", self.chat.edit_undo, False)
        menu.item("Redo", "<Control-Shift-z>", self.chat.edit_redo, False)
        menu.item("Select All", "<Control-a>", command=select_all)
        # self.chat.bind("<Control-a>", select_all)

        menu = Menu(bar, "View")
        menu.item("Show System Prompt", "", None)
        menu.item("Show Tree", "", None)
        menu.item("Count Tokens", "<Control-t>", self.count_tokens)
        # self.chat.bind("<Control-t>", self.count_tokens, False)
        menu.item("Run Code", "", None)
        menu.item("Update Window Title", "<Control-u>", update_window_title)
        menu.item("Highlight Importance", "", self.highlight_importance)

        menu = Menu(bar, "Navigate")
        menu.item("Jump to Similar Line", "<Control-b>", self.jump_to_section_or_definition)

        menu = Menu(bar, "Output")
        menu.item("Cancel", "<Escape>", self.gpt.cancel)

        menu = Menu(bar, "Models")
        for model_name in self.gpt.get_available_models() :
            menu.item(f"{model_name}", None, lambda m=model_name : self.set_model(m))

        menu = Menu(bar, "Help")
        menu.item("Test", "<Control-Shift-t>", menu_test)
        menu.item("About", None, None)

        self.chat.bind("<Button-3>", self.show_context_menu)


    def jump_to_section_or_definition(self, event=None) :

        def find_matching_line(target_line, line_nr, lines):
            num_lines = len(lines)
            if num_lines == 0:
                return 0
            stripped_target_line = target_line.strip()
            start = line_nr + 1
            for i, line in enumerate(lines[start:] + lines[:start], 1):
                if line.strip() == stripped_target_line:
                    # if i == line_nr:
                    #     return 0
                    # print(f" {i=} {num_lines=} {start=} {line.strip()=} {stripped_target_line=}")
                    return (i + start) % num_lines
            return 0

        # print()
        # print(f" {self.chat.index('insert')=}")
        # print(f" {self.chat.index('insert + 1 chars')=}")
        line_nr = int(self.chat.index('insert + 1 chars').split('.')[0])
        current_line = self.chat.get(f"{line_nr}.0", f"{line_nr}.end")
        if not current_line.strip():
            return
        lines = self.chat.get(1.0, tk.END).splitlines()
        jump_line = find_matching_line(current_line, line_nr, lines)
        if jump_line :
            jump_index = f"{jump_line}.{0}"
            self.chat.mark_set(tk.INSERT, jump_index)
            self.chat.see(jump_index)
            # print(f" {jump_line=} {jump_index=} {self.chat.get(f'{line_nr}.0', f'{line_nr}.end')=}")

    def create_textbox(self, parent, text) :

        def change_text_size(event, text, delta):
            name, size = text.cget("font").split()
            size = int(size)
            text.config(font=(name, size + delta))

        lines = len(text.splitlines())
        txt = ScrolledText(parent, insertwidth=3, undo=True,
                      wrap=tk.WORD, height=lines, padx=1, pady=1,
                      font=self.TEXT_FONT, bd=0, background="white",
                      highlightbackground='black', highlightcolor='green',
                      selectbackground="#66a2d4", selectforeground="white")
        txt.vbar.config(width=16)
        txt.pack(pady=0, fill=tk.X, expand=True)
        # txt.tag_configure("user", background="white", selectbackground="#5692c4", selectforeground="white")
        txt.tag_configure("assistant", background="#F0F0F0", selectbackground="#4682b4", selectforeground="white")
        txt.bind("<Control-Return>", lambda e : self.chatWithGpt())
        txt.bind("<Shift-Return>", lambda e : self.chatWithGpt(""))
        txt.bind("<Control-plus>", lambda event: change_text_size(event, txt, 1))
        txt.bind("<Control-minus>", lambda event: change_text_size(event, txt, -1))
        txt.bind("<Control-Button-4>", lambda event: change_text_size(event, txt, 1))
        txt.bind("<Control-Button-5>", lambda event: change_text_size(event, txt, -1))
        txt.insert(tk.END, text, "user")
        return txt

    def chatWithGpt(self, postfix="\n\n") :

        def insert_label(text, label_text, tool_tip_text=""):
            label = tk.Label(text, text=label_text, padx=8, bg="#F0F0F0", fg="grey")
            if tool_tip_text:
                ToolTip(label, tool_tip_text)
            # label.pack(expand=True, fill="both")
            text.window_create(tk.END, window=label)

        def output_response_delta_to_chat(content) :
            if self.is_root_destroyed :
                return
            self.chat.insert(tk.END, content, "assistant")
            if conf.scroll_during_completion:
                self.chat.see(tk.END)
            self.chat.update()

        if postfix :
            self.chat.insert(tk.END, postfix)
            self.chat.update()
        history = self.chat_history_from_textboxes()
        finish_reason = self.gpt.chat_complete(history, output_response_delta_to_chat)
        if self.is_root_destroyed:
            return
        if conf.show_finish_reason:
            symbol = self.finish_reasons[finish_reason]["symbol"]
            tool_tip = self.finish_reasons[finish_reason]["tool_tip"]
            if finish_reason not in ["stop", "length", "canceled"] :
                print(f"{finish_reason=}")
            if symbol :
                insert_label(self.chat, symbol, tool_tip)
        self.chat.insert(tk.END, "\n", "assistant")
        self.chat.mark_set(tk.INSERT, tk.END)
        self.chat.see(tk.END)
        if conf.ring_bell_after_completion:
            self.root.bell()

    def chat_history_from_textboxes(self, additional_message=None) :
        system = self.system_txt.get(1.0, 'end - 1c').strip()
        history = [{'role': 'system', 'content': system}]
        content = self.chat.dump(1.0, tk.END, text=True, tag=True)
        section = ""
        for item in content :
            if item[0] == "tagon" and item[1] == "assistant":
                section = section.strip()
                history += [{'role' : 'user', 'content' : section}]
                section = ""
            elif item[0] == "tagoff" and item[1] == "assistant":
                section = section.strip()
                history += [{'role' : 'assistant', 'content' : section}]
                section = ""
            elif item[0] == "text" :
                section += item[1]
        if section!= "" :
            section = section.strip()
            if history[-1]['role'] == "user" :
                history += [{'role' : 'assistant', 'content' : section}]
            elif history[-1]['role'] in ["assistant", "system"] :
                history += [{'role' : 'user', 'content' : section}]
        if additional_message:
            history += [{'role': 'user', 'content': additional_message}]
        return history

    def resize_textbox(self, txt) :
        n_lines = int(txt.index('end - 1c').split('.')[0])  # Get the total number of lines in the text box
        wrapped_lines = 0
        for line in range(1, n_lines + 1) :
            wrapped_line = txt.count(f"{line}.0", f"{line}.0 lineend", "displaylines")
            if wrapped_line:
                wrapped_lines += int(wrapped_line[0])
        n_lines += wrapped_lines
        if n_lines != txt.cget('height') :
            txt.config(height=n_lines)

    def on_key_release(self, event) :
        # if event.keysym in ('Return', 'BackSpace', 'Delete') :  # Check if the newline character was added
        txt = self.tree.focus_get()
        self.resize_textbox(txt)

    def count_tokens(self, event=None) :
        try :
            text = self.chat.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError :
            text = self.chat.get(1.0, tk.END)
        self.status_bar.set_main_text("Counting tokens (loading model)")
        num_tokens = self.gpt.count_tokens(text)
        num_lines = text.count("\n")
        num_words = len(text.split())
        num_chars = len(text)
        self.status_bar.set_main_text("")
        showinfo("Count Tokens",
                 f"The length of the text is:\n"
                 f"{num_tokens} tokens\n"
                 f"{num_lines} lines\n"
                 f"{num_words} words\n"
                 f"{num_chars} characters")
        return "break"

    def create_dummy_data(self, tree):
        for r in range(10):
            key = f"R{r}"
            parent_id = tree.insert("", "end", key, text=key, values=(r,))
            tree.item(key, tags='closed')
            if r % 2 == 0:
                for c in range(2):
                    child_key = f"R{r}_C{c}"
                    tree.insert(parent_id, "end", child_key, text=child_key, values=(c,))
                    tree.item(child_key, open=True, tags='opened')
                    for g in range(2):
                        grandchild_key = f"{child_key}_G{g}"
                        tree.insert(child_key, "end", grandchild_key, text=grandchild_key, values=(g,))
                        tree.item(grandchild_key, tags='closed')

    def close(self, event=None):
        self.is_root_destroyed = True
        self.root.destroy()

    def edit_tree_entry(self, event):
        row_id = self.tree.focus()
        if not row_id:
            return
        column = self.tree.identify_column(event.x)
        if column != "#1":  # Only allow editing the "Messages" column
            return
        x, y, width, height = self.tree.bbox(row_id, column)
        char_width = tkfont.Font(font=self.TEXT_FONT).measure('0')
        line_height = tkfont.Font(font=self.TEXT_FONT).metrics("linespace")
        width = max(self.tree.column(column)["width"], width)
        height = max(line_height, height)

        cur_text = self.tree.item(row_id, "values")[0]
        w = width // char_width
        h = height // line_height
        txt = tk.Text(self.tree, wrap=tk.WORD, width=w, height=h, font=self.TEXT_FONT,
                      highlightthickness=0, highlightbackground="black", padx=4, pady=0)
        txt.insert(tk.END, cur_text)
        txt.place(x=x, y=y)
        txt.focus_set()

        def save_text(event):
            print(event.type)
            if event.type == tk.EventType.FocusOut or int(event.state) & 0x4 == 0 :  # Check if Control key is not pressed
                text = txt.get(1.0, tk.END).strip()
                self.tree.set(row_id, column, text)
                txt.destroy()

        # txt.bind("<FocusOut>", save_text)
        txt.bind("<Return>", lambda e: e.state & 0x4 == 0 and save_text(e) or self.tree.focus_set())
        txt.bind("<Control-Return>", lambda e: txt.insert(tk.INSERT, "\n") or "break")
        # txt.bind("<Control-Key>", lambda e : "break")
        # txt.bind("<Control_L>", lambda e : "break")

    def highlight_importance(self) :
        self.chat.tag_configure('importance1', background='lightyellow')
        self.chat.tag_configure('importance2', background='bisque')
        self.chat.tag_configure('importance3', background='lightsalmon')

        content = self.chat.get(1.0, tk.END)
        content_lines = content.split('\n')

        for i, line in enumerate(content_lines) :
            if '¹' in line :
                start_index = line.index('¹')
                end_index = line.index('¹', start_index + 1)
                start = f"{i + 1}.{start_index + 1}"
                end = f"{i + 1}.{end_index}"
                self.chat.tag_add('importance1', start, end)
            if '²' in line :
                start_index = line.index('²')
                end_index = line.index('²', start_index + 1)
                start = f"{i + 1}.{start_index + 1}"
                end = f"{i + 1}.{end_index}"
                self.chat.tag_add('importance2', start, end)
            if '³' in line :
                start_index = line.index('³')
                end_index = line.index('³', start_index + 1)
                start = f"{i + 1}.{start_index + 1}"
                end = f"{i + 1}.{end_index}"
                self.chat.tag_add('importance3', start, end)


if __name__ == "__main__":
    root = tk.Tk()
    Thoughttree(root)
    root.mainloop()
