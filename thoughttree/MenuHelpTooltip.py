from Tooltip import Tooltip
from tools import text_block


class MenuHelpTooltip(Tooltip):
    def __init__(self, widget, menu_help):
        Tooltip.__init__(self, widget, None)
        self.menu_help = menu_help
        self.previous_missing_item = None


    def refresh_tooltip(self, event=None):
        if event:
            self.last_y = event.y
        if self.tooltip:
            px = self.root.winfo_pointerx() + 75
            py = self.root.winfo_pointery() + 25
            self.tooltip.wm_geometry(f"+{px}+{py}")

            try:
                menu_item = self.widget.entrycget(f'@{self.last_y}', 'label')
                if menu_item in self.menu_help:
                    help_text = self.menu_help[menu_item]
                    text = text_block(help_text)
                else:
                    text = menu_item
                    if menu_item and self.previous_missing_item != menu_item:
                        self.previous_missing_item = menu_item
                        print(f'No help text for "{menu_item}"')
                self.label.configure(text=text)
            except Exception as ex: # Menu separators have no "label"
                self.label.configure(text="-")

