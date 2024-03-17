import difflib
import random
import re
import tkinter as tk
from textwrap import dedent
from tkinter import INSERT, END

from InsertionIcon import InsertionIcon
from Sheet import Sheet, OUTPUT
from StructuredInteraction import StructuredInteraction
from Ui import Ui
from WaitCursor import WaitCursor
from tools import fail


class OutlineExploration(StructuredInteraction):
    def __init__(self, outline_level_spec, title=None, outline_id: str=None, parent_id=None):
        super().__init__()
        self.outline_id: str = str(outline_id) or str(random.randint(1000000, 9999999))
        self.parent_id = parent_id or outline_id

        self.title = title
        self.valid = False
        self.outline_level_items = []
        self.parse(outline_level_spec)

    def __str__(self):
        return "oa" + self.outline_id

    def parse(self, outline_level_spec):
        LABELED_LINE_PATTERN = "(?m)^([A-Z]\w+): (.*)$"
        OUTLINE_ITEM_PATTERN = "(?m)^ *([0-9]+\.[0-9.]*)\s+(.*)$"
        try:
            matches = re.findall(LABELED_LINE_PATTERN, outline_level_spec)
            matches or fail(f'No match for LABELED_LINE_PATTERN "{LABELED_LINE_PATTERN}"')
            map = {key: value for key, value in matches}
            id = map.get("Id", "").strip("'" + '"')
            # print(f'{id=} {type(id)=} {len(id)=} {type(self.outline_id)=}')
            id == self.outline_id or fail(f'Id mismatch: {id=} != {self.outline_id=}')
            self.title = map.get("Title", "")

            matches = re.findall(OUTLINE_ITEM_PATTERN, outline_level_spec)
            matches or fail(f'No match for OUTLINE_ITEM_PATTERN "{OUTLINE_ITEM_PATTERN}"')

            for groups in matches:
                outline_id = groups[0]
                outline_title = groups[1]
                self.outline_level_items.append((outline_id, outline_title))
        except Exception as ex:
            print(f'{ex=}')
            return
        self.valid = True

    def __bool__(self):
        return self.valid

    def add_to_tree(self, tree):
        iid = self.parent_id
        if tree.exists(iid):
            parent = iid
        else:
            parent = tree.append("Outlines", text=self.title, iid=iid, type="outline_exploration.root", tags=("outline",), open=True)

        for outline_id, outline_title in self.outline_level_items:
            tree.append(parent, text=outline_id + " " + outline_title, type="outline_exploration.item", tags=("outline",), open=True)
