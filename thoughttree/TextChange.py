import difflib
import re
import tkinter as tk
from tkinter import INSERT

from Sheet import Sheet


class TextChange():
    # multi_change_pattern_with_attributes = """(?m)(?:Titel|Title): (.*)\n+(?:Beschreibung|Description): (.*)\s+((?:\n+\w+: .*)*?)(\n+(?:Derzeitig|Old|Alt): (?:'.*'|".*"|"{3}[\s\S]*?"{3}|'{3}[\s\S]*?'{3})\n+(?:Vorschlag|New|Neu): (?:'.*'|".*"|"{3}[\s\S]*?"{3}|'{3}[\s\S]*?'{3}))+"""
    multi_change_pattern_with_attributes =   """(?m)(?:Titel|Title): (.*)\n+(?:Beschreibung|Description): (.*)((?:\s*\n\w+: .*)*?)?((?:\n+(?:Derzeitig|Old|Alt): (?:'.*'|".*"|"{3}[\s\S]*?"{3}|'{3}[\s\S]*?'{3})\n+(?:Vorschlag|New|Neu): (?:'.*'|".*"|"{3}[\s\S]*?"{3}|'{3}[\s\S]*?'{3}))+)"""


    def __init__(self, change_spec):
        self.title = None
        self.description = None
        self.attributes = {}
        self.replacements = {}

        self.parse(change_spec)


    def parse(self, change_spec):
        change_matches = re.findall(self.multi_change_pattern_with_attributes, change_spec)
        if not change_matches:
            print(f'No match for "{self.multi_change_pattern_with_attributes}"'[:120])
            return

        for title, description, attributes_section, replacements_section in change_matches:
            self.title = title
            self.description = description
            attribute_pattern = "\n(\w+): (.*)"
            attribute_matches = re.findall(attribute_pattern, attributes_section)
            if attribute_matches:
                for attribute, value in attribute_matches:
                    self.attributes[attribute] = value

            replacements_pattern = """(?:Derzeitig|Old|Alt): ('.*'|".*"|"{3}[\s\S]*?"{3}|'{3}[\s\S]*?'{3})\n+(?:Vorschlag|New|Neu): ('.*'|".*"|"{3}[\s\S]*?"{3}|'{3}[\s\S]*?'{3})"""
            replacements_pattern = """(?:Derzeitig|Old|Alt): ?[\n ]('.*'|".*"|"{3}[\s\S]*?"{3}|'{3}[\s\S]*?'{3}|```[\s\S]*?```)\n+(?:Vorschlag|New|Neu): ?[\n ]('.*'|".*"|"{3}[\s\S]*?"{3}|'{3}[\s\S]*?'{3}|```[\s\S]*?```)"""
            replacements_pattern = """(?:Derzeitig|Old|Alt): ?[\n ]((['"`]{1,3})([\s\S]*?)\2)\n+(?:Vorschlag|New|Neu): ?[\n ]((['"`]{1,3})([\s\S]*?)\4)"""
            replacements_pattern = r"""(?x)
                Old:\ ?\n?
                    ((['"`]{1,3})
                        ([\s\S]*?)
                    \2)
                \n+
                New:\ ?\n?
                    ((['"`]{1,3})
                        ([\s\S]*?)
                    \5)"""
            replacement_matches = re.findall(replacements_pattern, replacements_section)
            if not replacement_matches:
                print(f'No match for "{replacements_pattern}"'[:120])
                return

            for groups in replacement_matches:
                old = groups[2].strip("'"+'"')
                new = groups[5].strip("'"+'"')
                self.replacements[old] = new


    def apply(self, sheet: Sheet):
        for old, new in self.replacements.items():
            location = sheet.search(old, "1.0")
            while location:
                sheet.delete(location, f"{location}+{len(old)}c")
                sheet.insert(location, new)
                location = sheet.search(old, location)

    def __str__(self):
        # return f"{self.title=}\n{self.description=}\n{self.attributes=}\n{self.replacements=}"
        return f"{self.replacements}"


    def load_diff(self, sheet: Sheet, old_text, new_text, pos=INSERT):
        sheet.mark_set(INSERT, pos)
        sheet.delete(pos, f"{pos}+{len(old_text)}c")

        matcher = difflib.SequenceMatcher(
            None, old_text.split(), new_text.split(), autojunk=False)
            # None, [*old_text], [*new_text])
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == "equal":
                sheet.insert(INSERT, " ".join(old_text.split()[i1:i2]) + " ")
            elif op == "insert":
                sheet.insert(INSERT, " ".join(new_text.split()[j1:j2]) + " ", "added")
            elif op == "delete":
                sheet.insert(INSERT, " ".join(old_text.split()[i1:i2]) + " ", "deleted")
            elif op == "replace":
                sheet.insert(INSERT, " ".join(old_text.split()[i1:i2]) + " ", "deleted")
                sheet.insert(INSERT, " ".join(new_text.split()[j1:j2]) + " ", "added")


if __name__ == "__main__":
    text = """Titel: A
Beschreibung: B
Old: 'a'
New: 'b'
Old: 'c'
New: 'd'
Old: 'e'
New: 'f'
Old: 'g'
New: 'h'
"""
    change = TextChange(text)
    root = tk.Tk()
    root.geometry("500x500")
    s = Sheet(root)
    s.insert(INSERT, " aa c e g i")
    s.pack()
    print(f"{change}")

    change.apply(s)

    root.mainloop()

