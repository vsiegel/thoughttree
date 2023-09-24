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
            replacements_pattern = """(?x)
                (?:Derzeitig|Old|Alt):\ ?\n?
                    ((['"`]{1,3})
                        ([\s\S]*?)
                    \2)
                \n+
                (?:Vorschlag|New|Neu):\ ?\n?
                    ((['"`]{1,3})
                        ([\s\S]*?)
                    \5)"""
            replacement_matches = re.findall(replacements_pattern, replacements_section)
            if not replacement_matches:
                print(f'No match for "{replacements_pattern}"'[:120])
                return
            for old, new in replacement_matches:
                old = old.strip("'"+'"')
                new = new.strip("'"+'"')
                self.replacements[old] = new


    def apply_highlight(self, sheet: Sheet):
        # original = open("/home/siegel/manuscript/99_thoughttree.tex").read()
        # old = open("/home/siegel/manuscript/a.txt").read()
        # new = open("/home/siegel/manuscript/b.txt").read()

        # sheet.insert(start, original)
        print(f'"{self.replacements=}"')
        for old, new in self.replacements.items():
            location = sheet.search(old, "1.0")
            if location:
                sheet.delete(location, f"{location}+{len(old)}c")
                sheet.insert(location, new)
                print(f'"{location=}"')

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
    change = TextChange("""Titel: A\nBeschreibung: B\nDerzeitig: 'a'\nVorschlag: 'b'\nDerzeitig: 'c'\nVorschlag: 'd'\nDerzeitig: 'e'\nVorschlag: 'f'\nDerzeitig: 'g'\nVorschlag: 'h'""")
    root = tk.Tk()
    root.geometry("500x500")
    s = Sheet(root)
    s.insert(INSERT, " aa c e g i")
    s.pack()
    change.apply_highlight(s)

    root.mainloop()

