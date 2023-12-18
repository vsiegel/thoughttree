from os.path import exists

from Tooltip import Tooltip
from tree_help_texts import tree_help


class TreeTooltip(Tooltip):
    def __init__(self, tree):
        self.tree = tree
        super().__init__(tree, None,("monospace", 9))

    def refresh_tooltip_text(self, event=None):
        max_lines = 40
        max_columns = 100
        iid = self.tree.tree.identify('item', event.x, event.y)
        text = ""
        toplevel_node = "Tree." + iid
        if toplevel_node in tree_help:
            text = tree_help[toplevel_node].strip()
        else:
            values = self.tree.tree.item(iid)["values"]
            item = values and values[0]
            if item and exists(item):
                with open(item, encoding="utf-8") as f:
                    text = f.read()
                    lines = text.splitlines()
                    lines = lines[:max_lines]
                    lines = [line[:max_columns] for line in lines]
                    text = "\n".join(lines)
        if text.strip():
            self.label.configure(text=text)

    # def bind_tip(self):
    #     self.tree.tree.bind("<Leave>", self.hide, add=True)
    #     self.tree.tree.bind("<Motion>", self.update, add=True)
