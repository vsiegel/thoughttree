import tkinter as tk
from tkinter import filedialog
from tkinter.messagebox import showerror


class ChatFileManager:
    @staticmethod
    def save_chat(text_widget, filename):
        # ROLE_SYMBOLS = {"user":"❯ ", "ai":"⚙ "}
        ROLE_SYMBOLS = {"user": "", "ai": ""}
        content = text_widget.dump(1.0, tk.END, text=True, tag=True)
        with open(filename, 'w') as f:
            drop_nl = False
            for item in content:
                if item[0] == "tagon":
                    if item[1] == "assistant":
                        f.write(ROLE_SYMBOLS["ai"])
                elif item[0] == "tagoff":
                    if item[1] == "assistant":
                        f.write("\n" + ROLE_SYMBOLS["user"])
                        drop_nl = True
                elif item[0] == "text":
                    if drop_nl:
                        drop_nl = False
                        if item[1] == "\n":
                            continue
                    f.write(item[1])

    @staticmethod
    def save_chat_dialog(text_widget):
        file = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile="chat.txt", title="Save chat")
        if file:
            ChatFileManager.save_chat(text_widget, file)
        return file

    @staticmethod
    def save_section(text_widget: tk.Text, filename, index=tk.INSERT):
        raise "not implemented yet"

    @staticmethod
    def save_code_section(text_widget: tk.Text, filename, index=tk.INSERT):
        try:
            text_range = text_widget.tag_prevrange("assistant", index)
            if not text_range:
                raise Exception("No code section found")
            start, end = text_range
            print(f"{start=}, {end=}")
            code_section = text_widget.get(*text_range)
            if code_section[:3] == "```":
                code_section = code_section[3:]
            if code_section[:-4] == "```\n":
                code_section = code_section[3:]
            with open(filename, 'w') as f:
                f.write(code_section)
        except Exception as e:
            showerror(title="Error", message="Cannot save code section\n" + str(e))

    @staticmethod
    def save_section_dialog(text_widget):
        file = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile="section.txt", title="Save section")
        if file:
            ChatFileManager.save_section(text_widget, file)
        return file

    @staticmethod
    def save_code_section_dialog(text_widget):
        file = filedialog.asksaveasfilename(
            defaultextension=".py", initialfile="code-section.py", title="Save code section")
        if file:
            ChatFileManager.save_code_section(text_widget, file)
        return file

    @staticmethod
    def load_chat(text_widget, filename):
        with open(filename, 'r') as f:
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
    def load_chat_dialog(text_widget):
        file = filedialog.askopenfilename(defaultextension=".txt")
        if file:
            ChatFileManager.load_chat(text_widget, file)
