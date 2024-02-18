import json

from tools import shorter, log_len
import tkinter as tk

# class History(list):
#     __init__ = list.__init__
#     def __repr__(self):
#         return f"l(l-r: {super().__repr__()})"
#     def __str__(self):
#         return f"l(l-s: {super().__str__()})"

class History(list):
    ROLE_SYMBOLS = {"user":"🅰️ ", "assistant":"💻️ ", "system":"⚙ ", "function":"📊 "} # 🗣⌨
    # ROLE_SYMBOLS = {"user": "", "assistant": "", "system": "", "function": ""}


    def __init__(self, text=None, system="", assistant="", user="", ignore_empty=False):
        super().__init__()
        self.first_system = None
        self.last = None
        self.ignore_empty = ignore_empty
        if system:
            self.system(system)
        if isinstance(text, tk.Text):
            items = text.dump(1.0, "end-1c", text=True, tag=True, window=True)
            content = ""
            role = "user"
            for item in items:
                text = item[1]
                designation = item[0]
                if ("tagon", "assistant") == (designation, text):
                    self.message(role, content)
                    role, content = "assistant", ""
                elif ("tagoff", "assistant") == (designation, text):
                    self.message(role, content)
                    role, content = "user", ""
                elif designation in ["tagon", "tagoff"] and (text in ["cursorline", "sel"] or text.startswith('model')):
                    pass
                elif designation == "text":
                    content += text
                elif designation == "window":
                    pass
                else:
                    print(f"Ignored item: {item}")
            # if not (role, content) == ("user", "\n"):
            self.message(role, content)
        elif text:
            self.user(str(text))
        if assistant:
            self.assistant(assistant)
        if user:
            self.user(user)


    def message(self, role, content):
        if content:
            if self.ignore_empty and content.strip() == "":
                return
            self.append({'role': role, 'content': content})


    def assistant(self, content):
        self.message('assistant', content)


    def user(self, content):
        self.message('user', content)
        if not self.last:
            self.last = content

    def system(self, content):
        self.message('system', content)
        if not self.first_system:
            self.first_system = content

    def limit(self, messages=2):
        messages = min(messages, len(self))
        if messages:
            if messages == 1:
                self[:] = self[-1:]
            else:
                last = messages - 1
                self[:] = self[0:1] + self[-last:]

    # def log_compact(self):
    #     for message in self:
    #         content = message['content']
    #         print(f"{message['role']}: \"{shorter(content, 120)}\" {log_len(content, 120)}")


    def log(self):
        for message in self:
            print(f'{History.ROLE_SYMBOLS[message["role"]]}{message["role"]}:\n"{message["content"]}"')


    def __add__(self, other):
        sum = History()
        sum.extend(self)
        if hasattr(other, '__iter__') and not isinstance(other, str):
            sum.extend(other)
        else:
            sum.append(other)
        return sum

    def __str__(self):
        abstract = json.loads(str(self))
        return json.dumps(abstract, indent=4)

    def __repr__(self):
        return self.__str__()
