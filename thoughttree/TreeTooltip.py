from os.path import isfile

from Tooltip import Tooltip
from tree_help_texts import tree_help


class TreeTooltip(Tooltip):
    def __init__(self, tree):
        self.tree = tree
        super().__init__(tree, None,("monospace", 9))

    def refresh_tooltip_text(self, event=None):
        max_lines = 40
        max_columns = 100
        iid = self.tree.identify('item', event.x, event.y)
        # bbox = self.tree.bbox(iid)
        text = ""
        toplevel_node = "Tree." + iid
        if toplevel_node in tree_help:
            text = tree_help[toplevel_node].strip()
        else:
            values = self.tree.item(iid)["values"]
            item = values and values[0]
            if item and isfile(item):
                with open(item, encoding="utf-8") as f:
                    text = f.read()
                    lines = text.splitlines()
                    lines = lines[:max_lines]
                    lines = [line[:max_columns] for line in lines]
                    text = "\n".join(lines)
        if text.strip():
            self.tip.deiconify()
            self.label.configure(text=text)
        else:
            self.label.configure(text="(hidden)")
            self.tip.withdraw()

    def update(self, event):
        self.refresh_tooltip_text(event)
        super().update(event)

    # def bind_tip(self):
    #     self.tree.bind("<Leave>", self.hide, add=True)
    #     self.tree.bind("<Motion>", self.update, add=True)
