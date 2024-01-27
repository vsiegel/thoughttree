import difflib
import re
import tkinter as tk
from tkinter import INSERT

from Sheet import Sheet
from tools import fail


class ExploreOutline():
    def __init__(self, outline_level_spec, title=None, iid=None):
        self.iid = iid or id(self)
        self.title = title or self.iid
        self.valid = True
        self.outline_level_items = []
        self.parse(outline_level_spec)

    def __bool__(self):
        return self.valid


    def parse(self, outline_level_spec):
        LABELED_LINE_PATTERN = "(?m)^([A-Z]\w+): (.*)$"
        try:
            pattern = "(?m)^ *([0-9]+\.[0-9.]*)\s+(.*)$"
            matches = re.findall(pattern, outline_level_spec)
            matches or fail(f'No match for "{pattern}"')

            for groups in matches:
                outline_id = groups[0]
                outline_title = groups[1]
                self.outline_level_items.append((outline_id, outline_title))
            # print(f'{self.outline_level_items=}')
        except Exception as ex:
            self.valid = False
            print(f'{ex=}')
            print(f'{outline_level_spec}')
