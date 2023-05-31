import tkinter as tk


class ToolTip :
    def __init__(self, widget, text) :
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)


    def show_tooltip(self, event=None) :
        if self.tooltip_window is not None :
            return

        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, background="#FFFFE0", relief="solid",
                borderwidth=1, justify=tk.LEFT, anchor=tk.W, padx=4, pady=4)
        label.pack()


    def hide_tooltip(self, event=None) :
        if self.tooltip_window is None :
            return

        self.tooltip_window.destroy()
        self.tooltip_window = None
