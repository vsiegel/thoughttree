import difflib
import re
import tkinter as tk
from tkinter import INSERT

from Sheet import Sheet
from tools import fail

p1 ="""
Bring the input text in a better form for a naive reader.
Create an outline of possible enhancements of the text, choosing and organizing the kind of enhancements based on the individual text. The outline should present kinds of changes, variants applicable to the input, concrete changes that could be applied, as text replacement in the form of 

Title:
Description:
Reason:
Effect of change:
Old:
New:
Old:
New:
...

Give all possible replacement pairs for each item.
Produce a large number of items.
Start with a decimal outline of the structure, then refine the outline, and then generate the full text including all fields of each item.
Like:

1. Reds
    1.1 Tomatoes
    1.2 Strawberies
2. Greens
...

Refining to more levels, including the titles of actual items.
"""
p2 = """
We want to create a detailed set of appropriate text changes for the input. They can change the text in multiple ways for multiple purposes.
Which kinds of changes are appropriate for the input depends very much on the input. All texts may require typo fixes, but not any text can be 
made "less formal" (for example a log file) or less aggressive (a list of ingredients). To later organize the change items, we organize the structure
as a hierarchical outline.
This outline is not general, it is specifically tailored to the input.

The outline will be used in the following way: The outline items on the deepest levels will be items that describe possible text changes, in the following way:

Title:
Description:
Reason:
Effect of change:
Old:
New:
Old:
New:
...

That is not what should be generated now - currently it is only about the outline structure (Use a decimal outline, like 1.1.1.1.1).
"""

class Improvement():
    def __init__(self, change_spec):
        self.valid = True
        self.title = ""
        self.replacements = {}
        self.parse(change_spec)


    def __bool__(self):
        return self.valid


    def parse(self, change_spec):
        try:
            # title_pattern = "Title:\ ?\n?((['\"`]{1,3})([\s\S]*?)\2)" #?
            title_pattern = r"""(?x)
                Title:\ ?\n?
                    ((['"`]{1,3})
                        ([\s\S]*?)
                    \2)"""

            title_matches = re.findall(title_pattern, change_spec)
            title_matches or fail(f'No match for "{title_pattern}"'[:80])
            self.title = title_matches[0][2].strip("'"+'"')

            # change_pattern = "Old:\ ?\n?((['\"`]{1,3})([\s\S]*?)\2)\n+New:\ ?\n?((['\"`]{1,3})([\s\S]*?)\5)" #?
            change_pattern = r"""(?x)
                Old:\ ?\n?
                    ((['"`]{1,3})
                        ([\s\S]*?)
                    \2)
                \n+
                New:\ ?\n?
                    ((['"`]{1,3})
                        ([\s\S]*?)
                    \5)"""
            change_matches = re.findall(change_pattern, change_spec)
            change_matches or fail(f'No match for "{change_pattern}"'[:80])

            for groups in change_matches:
                old = groups[2].strip("'"+'"')
                new = groups[5].strip("'"+'"')
                self.replacements[old] = new
        except Exception as ex:
            self.valid = False
            print(f'{ex=}')
            print(f'{change_spec}')


    def apply(self, sheet: Sheet):
        for old, new in self.replacements.items():
            location = sheet.search(old, "1.0")
            while location:
                sheet.delete(location, f"{location}+{len(old)}c")
                sheet.insert(location, new)
                location = sheet.search(old, location)

    def __str__(self):
        return f"{self.replacements}"


    def load_diff(self, sheet: Sheet, old_text, new_text, pos=INSERT):
        sheet.mark_set(INSERT, pos)
        sheet.delete(pos, f"{pos}+{len(old_text)}c")

        old_words = old_text.split()
        new_words = new_text.split()
        matcher = difflib.SequenceMatcher(None, old_words, new_words, autojunk=False)
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == "equal":
                sheet.insert(INSERT, " ".join(old_words[i1:i2]) + " ")
            elif op == "insert":
                sheet.insert(INSERT, " ".join(new_words[j1:j2]) + " ", "added")
            elif op == "delete":
                sheet.insert(INSERT, " ".join(old_words[i1:i2]) + " ", "deleted")
            elif op == "replace":
                sheet.insert(INSERT, " ".join(old_words[i1:i2]) + " ", "deleted")
                sheet.insert(INSERT, " ".join(new_words[j1:j2]) + " ", "added")


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
    change = Improvement(text)
    root = tk.Tk()
    root.geometry("500x500")
    s = Sheet(root)
    s.insert(INSERT, " aa c e g i")
    s.pack()
    print(f"{change}")

    change.apply(s)

    root.mainloop()
