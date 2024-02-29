import difflib
import random
import re
import tkinter as tk
from textwrap import dedent
from tkinter import INSERT, END

from InsertionIcon import InsertionIcon
from Sheet import Sheet, OUTPUT
from StructuredInteraction import StructuredInteraction
from WaitCursor import WaitCursor
from tools import fail


class OutlineExploration(StructuredInteraction):
    def __init__(self, outline_level_spec, title=None, outline_id=None, parent_id=None):
        super().__init__()
        self.outline_id = outline_id or random.randint(1000000, 9999999)
        self.parent_id = parent_id or outline_id

        self.title = title or self.outline_id
        self.valid = True
        self.outline_level_items = []
        self.parse(outline_level_spec)

    def __str__(self):
        return "oa" + self.outline_id

    def parse(self, outline_level_spec):
        LABELED_LINE_PATTERN = "(?m)^([A-Z]\w+): (.*)$"
        OUTLINE_ITEM_PATTERN = "(?m)^ *([0-9]+\.[0-9.]*)\s+(.*)$"
        try:
            matches = re.findall(LABELED_LINE_PATTERN, outline_level_spec)
            if matches:
                labled_lines = {key: value for key, value in matches}
                id = labled_lines["Id"].strip("'" + '"')
                # print(f'{id=} {type(id)=} {len(id)=} {type(self.outline_id)=}')
                id == self.outline_id or fail(f'Id mismatch: {id=} != {self.outline_id=}')
                self.title = labled_lines["Title"]

            matches = re.findall(OUTLINE_ITEM_PATTERN, outline_level_spec)
            matches or fail(f'No match for "{OUTLINE_ITEM_PATTERN}"')

            for groups in matches:
                outline_id = groups[0]
                outline_title = groups[1]
                self.outline_level_items.append((outline_id, outline_title))
        except Exception as ex:
            self.valid = False
            print(f'{ex=}')
            print(f'{outline_level_spec}')
