import tkinter as tk
from textwrap import dedent
from tkinter import SEL_FIRST, SEL_LAST
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.messagebox import showerror
import re

from TextSaver import TextSaver


class ChatLogSaver(TextSaver):

    def find_text(self):
        # Implement the method to find the chat log text from the widget
        pass

    def find_filename(self):
        # Implement the method to find the filename for the chat log
        return "chat.txt"

class SectionSaver(TextSaver):

    def find_text(self):
        # Implement the method to find the section text from the widget
        pass

    def find_filename(self):
        # Implement the method to find the filename for the section
        return "section.txt"

class CodeBlockSaver(TextSaver):

    def find_text(self):
        # Implement the method to find the code block text from the widget
        pass

    def find_filename(self):
        # Implement the method to find the filename for the code block
        return "code_block.py"


class Files:
    @staticmethod
    def open_file(e=None, title="Open File", initialfile=None):
        file = askopenfilename(defaultextension=".txt",
                initialfile=initialfile, title=title,
                filetypes=(('Text Files', '*.txt'), ('Python Files', '*.py'), ('All files', '*.*')))#, parent=sheet)
        if not file:
            return
        with open(file, "r") as f:
            text = f.read()
            return file, text


    # @staticmethod
    # def save_chat(e=None):
    #     chat_log_saver = ChatLogSaver(e.widget)
    #     chat_log_saver.save()
    #
    # @staticmethod
    # def save_section_dialog(sheet):
    #     section_saver = SectionSaver(sheet)
    #     section_saver.save()
    #
    # @staticmethod
    # def save_code_block_dialog(sheet):
    #     code_block_saver = CodeBlockSaver(sheet)
    #     code_block_saver.save()

    @staticmethod
    def save_chat(e=None):

        def text_not_found_error():
            pass

        def find_text(sheet):
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
    def save_chat_dialog(sheet):

        def write_chat(sheet, filename) :
            try:
                # ROLE_SYMBOLS = {"user":"❯ ", "ai":"⚙ "}
                ROLE_SYMBOLS = {"user" : "", "ai" : ""}
                content = sheet.dump(1.0, tk.END, text=True, tag=True)
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
                showerror(title="Error", message="Cannot save chat\n" + str(e), master=sheet)

        file = asksaveasfilename(defaultextension=".txt",
                initialfile="chat.txt", title="Save Chat", parent=sheet)
        if file:
            write_chat(sheet, file)
        return file


    @staticmethod
    def save_section_dialog(sheet):

        def write_section(sheet: tk.Text, filename, index=tk.INSERT):
            try:
                text_range = sheet.tag_prevrange("assistant", index)
                if not text_range:
                    raise Exception("No section found")
                section = sheet.get(*text_range)

                with open(filename, 'w') as f:
                    f.write(section)
            except Exception as e:
                showerror(title="Error", message="Cannot save section\n" + str(e), master=sheet)

        file = asksaveasfilename(
            defaultextension=".txt", initialfile="section.txt", title="Save Section", parent=sheet)
        if file:
            write_section(sheet, file)
        return file


    @staticmethod
    def save_selection_dialog(sheet):

        def write_section(sheet: tk.Text, filename, index=tk.INSERT):
            try:
                string = sheet.get(SEL_FIRST, SEL_LAST)

                with open(filename, 'w') as f:
                    f.write(string)
            except Exception as e:
                showerror(title="Error", message="Cannot save section\n" + str(e), master=sheet)

        file = asksaveasfilename(
            defaultextension=".txt", initialfile="selection.txt", title="Save Selection", parent=sheet)
        if file:
            write_section(sheet, file)
        return file

    @staticmethod
    def save_code_block_dialog(sheet):

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

        def find_code_block(sheet: tk.Text, index=tk.INSERT):
            text_range = sheet.tag_prevrange("assistant", index)
            if not text_range:
                raise Exception("No code block found")
            code_block_section = sheet.get(*text_range)
            code_block, file_type = extract_code_block(code_block_section)
            return code_block #, file_type

        try:
            code_block = find_code_block(sheet)

            ext = ".py"
            filename = asksaveasfilename(
                    defaultextension=ext, initialfile="code_block.py", title="Save Code Block", parent=sheet)
            if filename:
                if not re.match(".*\..{1,5}$", filename):
                    filename = filename + ext
                with open(filename, 'w') as f:
                    f.write(code_block)

            return filename
        except Exception as e:
            showerror(title="Error", message="Cannot save code block\n" + str(e), master=sheet)
            return None

    @staticmethod
    def save_file(filename, text):
        with open(filename, 'w') as f:
            f.write(text)
