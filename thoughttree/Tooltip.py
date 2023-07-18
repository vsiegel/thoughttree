import textwrap
import tkinter as tk



class Tooltip :
    def __init__(self, widget, text) :
        self.widget = widget
        self.root = widget.winfo_toplevel()
        self.text = text
        self.tooltip = None
        self.label = None
        self.timer = None
        self.last_y = None
        self.delay_ms = 1000

        widget.bind("<Enter>", self.add_tooltip)
        widget.bind("<Motion>", self.refresh_tooltip)
        widget.bind("<Leave>", self.remove_tooltip)
        widget.bind("<Unmap>", self.remove_tooltip)


    def add_tooltip(self, event):
        if self.tooltip:
            return
        self.timer = self.root.after(self.delay_ms, self.create_tooltip)


    def create_tooltip(self, event=None):
        if not self.tooltip:
            self.tooltip = tk.Toplevel(self.root)
            self.tooltip.wm_overrideredirect(True)
            self.label = tk.Label(self.tooltip, text="text", background="#FFFFE0", relief="solid",
                             borderwidth=1, justify=tk.LEFT, padx=6, pady=5, font=("sans-serif", 11))
            self.label.pack()
            self.tooltip.bind("<Leave>", self.remove_tooltip)
            self.refresh_tooltip()


    def refresh_tooltip(self, event=None):
        if event:
            self.last_y = event.y
        if self.tooltip:
            px = self.root.winfo_pointerx() + 75
            py = self.root.winfo_pointery() + 25
            self.tooltip.wm_geometry(f"+{px}+{py}")

            self.label.configure(text=self.text)



    def remove_tooltip(self, event):
        if self.timer:
            self.root.after_cancel(self.timer)
        if self.tooltip:
            self.tooltip.destroy()
        self.tooltip = None


    # def show_tooltip(self, event=None) :
    #     if self.tooltip is not None :
    #         return
    #
    #     x, y, _, _ = self.widget.bbox("insert")
    #     x += self.widget.winfo_rootx() + 25
    #     y += self.widget.winfo_rooty() + 25
    #
    #     self.tooltip = tooltip = tk.Toplevel(self.widget)
    #     tooltip.wm_overrideredirect(True)
    #     tooltip.wm_geometry(f"+{x}+{y}")
    #
    #     label = tk.Label(tooltip, text=self.text, background="#FFFFE0", relief="solid",
    #             borderwidth=1, justify=tk.LEFT, padx=4, pady=4)
    #     label.pack()
    #
    #
    # def hide_tooltip(self, event=None) :
    #     if self.tooltip:
    #         self.tooltip.destroy()
    #     self.tooltip = None
