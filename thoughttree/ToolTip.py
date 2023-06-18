import tkinter as tk


class ToolTip :
    def __init__(self, widget, text) :
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)


    def show_tooltip(self, event=None) :
        if self.tooltip is not None :
            return

        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = tooltip = tk.Toplevel(self.widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tooltip, text=self.text, background="#FFFFE0", relief="solid",
                borderwidth=1, justify=tk.LEFT, padx=4, pady=4)
        label.pack()


    def hide_tooltip(self, event=None) :
        if self.tooltip:
            self.tooltip.destroy()
        self.tooltip = None
