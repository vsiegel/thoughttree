import tkinter as tk
from textwrap import dedent
from tkinter import filedialog
from tkinter.messagebox import showerror
import re

code_block_extensions = {
    "python": ".py",
    "javascript": ".js",
    "java": ".java",
    "c": ".c",
    "cpp": ".cpp",
    "ruby": ".rb",
    "php": ".php",
    "swift": ".swift",
    "go": ".go",
    "csharp": ".cs",
    "html": ".html",
    "css": ".css",
    "sql": ".sql",
    "xml": ".xml",
    "json": ".json",
    "markdown": ".md",
    "bash": ".sh",
    "powershell": ".ps1",
    "typescript": ".ts",
    "kotlin": ".kt",
    "rust": ".rs",
    "scala": ".scala",
    "perl": ".pl",
    "lua": ".lua",
    "groovy": ".groovy",
    "r": ".r",
    "dart": ".dart",
    "yaml": ".yml",
    "ini": ".ini",
    "toml": ".toml",
    "dockerfile": "Dockerfile",
    "coffeescript": ".coffee",
    "elixir": ".ex",
    "elm": ".elm",
    "erlang": ".erl",
    "fsharp": ".fs",
    "haskell": ".hs",
    "julia": ".jl",
    "matlab": ".m",
    "objective-c": ".m",
    "pascal": ".pas",
    "raku": ".raku",
    "shell": ".sh",
    "vimscript": ".vim",
    "tex": ".tex",
    "latex": ".tex",
}

class ChatFileManager:

    @staticmethod
    def save_chat_dialog(text_widget):

        def save_chat(text_widget, filename) :
            # ROLE_SYMBOLS = {"user":"❯ ", "ai":"⚙ "}
            ROLE_SYMBOLS = {"user" : "", "ai" : ""}
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
                            if item[1] == "\n" :
                                continue
                        f.write(item[1])

        file = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile="chat.txt", title="Save chat")
        if file:
            save_chat(text_widget, file)
        return file


    @staticmethod
    def save_section(text_widget: tk.Text, filename, index=tk.INSERT):
        try :
            text_range = text_widget.tag_prevrange("assistant", index)
            if not text_range :
                raise Exception("No section found")
            start, end = text_range
            section = text_widget.get(*text_range)

            with open(filename, 'w') as f :
                f.write(section)
        except Exception as e :
            showerror(title="Error", message="Cannot save section\n" + str(e))


    @staticmethod
    def save_section_dialog(text_widget):
        file = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile="section.txt", title="Save section")
        if file:
            ChatFileManager.save_section(text_widget, file)
        return file

    @staticmethod
    def save_code_section(text_widget: tk.Text, filename, index=tk.INSERT):

        def extract_code_block(text) :
            code_blocks = re.findall(r'```(.*?)```', text, re.DOTALL)

            if not code_blocks :
                raise ValueError('No code blocks found')

            if len(code_blocks) > 1 :
                raise ValueError('Multiple code blocks found')

            if len(code_blocks) == 1 :
                code_block = code_blocks[0]
                file_type = None
                match = re.search(r'^([a-zA-Z0-9]+)\n', code_block)
                if match :
                    file_type = match.group(1)
                    code_block = re.sub(r'^[a-zA-Z0-9]+\n', '', code_block)
                code_block = dedent(code_block)
                return code_block, file_type

        try:
            text_range = text_widget.tag_prevrange("assistant", index)
            if not text_range:
                raise Exception("No code section found")
            start, end = text_range
            code_section = text_widget.get(*text_range)
            code_block, file_type = extract_code_block(code_section)

            with open(filename, 'w') as f:
                f.write(code_block)
        except Exception as e:
            showerror(title="Error", message="Cannot save code section\n" + str(e))

    @staticmethod
    def save_code_block_dialog(text_widget):
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
                tag, text = line.lstrip().split(': ', 1)
                text_widget.insert(tk.END, text)
                text_widget.tag_add(tag, text_widget.index(tk.END + '-1c linestart'), text_widget.index(tk.END + '-1c lineend'))
            else:
                text_widget.insert(tk.END, line)

    @staticmethod
    def load_chat_dialog(text_widget):
        file = filedialog.askopenfilename(defaultextension=".txt")
        if file:
            ChatFileManager.load_chat(text_widget, file)
