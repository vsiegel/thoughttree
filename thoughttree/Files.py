import tkinter as tk
from textwrap import dedent
from tkinter import filedialog
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showerror
import re
import re
from clipboard import paste

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

def filename_from_clipboard():
    text = paste().strip()
    match = re.match(r'^[^ ]+\.[A-Za-z]{1,5}$', text)
    if match:
        return match.group(0)
    else:
        return None


class Files:

    @staticmethod
    def save_chat(e=None):

        def text_not_found_error():
            pass

        def find_text(txt):
            pass
            return "foo"

        def find_filename():
            return "bar"

        def ask_filename(initial_filename):
            return ""

        def write_text(text, filename):
            pass

        text = find_text(e.widget)
        if not text:
            text_not_found_error()
            return
        initial_filename = find_filename()
        filename = ask_filename(initial_filename)
        if not filename:
            return
        write_text(text, filename)



        print(e)
        print(e.widget)
        print(type(e.widget))
        # name = save(Files.save_chat_dialog, "Chat saved to ")
        # self.tt.title(name)


        # def save(save_dialog, status_bar_label):
        #     file_name = save_dialog(self.tt.chat)
        #     if not file_name:
        #         return
        #     base_name = file_name.split("/")[-1]
        #     self.tt.status_bar.note = status_bar_label + base_name
        #     return base_name


    @staticmethod
    def save_chat_dialog(txt):

        def write_chat(txt, filename) :
            try:
                # ROLE_SYMBOLS = {"user":"❯ ", "ai":"⚙ "}
                ROLE_SYMBOLS = {"user" : "", "ai" : ""}
                content = txt.dump(1.0, tk.END, text=True, tag=True)
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
            except Exception as e:
                showerror(title="Error", message="Cannot save chat\n" + str(e), master=txt)

        file = asksaveasfilename(defaultextension=".txt",
                initialfile="chat.txt", title="Save Chat", parent=txt)
        if file:
            write_chat(txt, file)
        return file


    @staticmethod
    def save_section_dialog(txt):

        def write_section(txt: tk.Text, filename, index=tk.INSERT):
            try:
                text_range = txt.tag_prevrange("assistant", index)
                if not text_range:
                    raise Exception("No section found")
                section = txt.get(*text_range)

                with open(filename, 'w') as f:
                    f.write(section)
            except Exception as e:
                showerror(title="Error", message="Cannot save section\n" + str(e), master=txt)

        file = asksaveasfilename(
            defaultextension=".txt", initialfile="section.txt", title="Save Section", parent=txt)
        if file:
            write_section(txt, file)
        return file

    @staticmethod
    def save_code_block_dialog(txt):

        def extract_code_block(text):
            code_blocks = re.findall(r'```(.*?)```', text, re.DOTALL)

            if not code_blocks:
                raise ValueError('No code blocks found')

            if len(code_blocks) > 1:
                raise ValueError('Multiple code blocks found')

            if len(code_blocks) == 1:
                block = code_blocks[0]
                file_type = None
                match = re.search(r'^([a-zA-Z0-9]+)\n', block)
                if match:
                    file_type = match.group(1)
                    block = re.sub(r'^[a-zA-Z0-9]+\n', '', block)
                block = dedent(block)
                return block, file_type

        def find_code_block(txt: tk.Text, index=tk.INSERT):
            text_range = txt.tag_prevrange("assistant", index)
            if not text_range:
                raise Exception("No code block found")
            code_block_section = txt.get(*text_range)
            code_block, file_type = extract_code_block(code_block_section)
            return code_block #, file_type

        try:
            code_block = find_code_block(txt)

            filename = asksaveasfilename(
                    defaultextension=".py", initialfile="code-block.py", title="Save Code Block", parent=txt)
            if filename:
                with open(filename, 'w') as f:
                    f.write(code_block)

            return filename
        except Exception as e:
            showerror(title="Error", message="Cannot save code block\n" + str(e), master=txt)
            return None

    @staticmethod
    def history_from_args(system="", message="") :
        history = [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': message}
        ]
        return history
