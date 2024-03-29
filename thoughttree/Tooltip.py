import tkinter as tk


class Tooltip:
    def __init__(self, widget: tk.Widget, text, font=("sans-serif", 11), above=False) :
        self.widget = widget
        self.root = widget.winfo_toplevel()
        self.font = font
        self.text = text
        self.above = above

        self.tip = None
        self.label = None
        self.show_timer = None
        self.show_delay_ms = 1000

        self.bind_tip()


    def bind_tip(self):
        self.widget.bind("<Unmap>", self.hide, add=True)
        self.widget.bind("<Destroy>", self.hide, add=True)
        self.widget.bind("<Leave>", self.hide, add=True)
        self.widget.bind("<Enter>", self.show_later, add=True)
        self.widget.bind("<Motion>", self.refresh, add=False)


    def show_later(self, event):
        if self.tip:
            return

        if self.show_timer:
            self.root.after_cancel(self.show_timer)
        self.show_timer = self.root.after(self.show_delay_ms, lambda ev=event: self.show(ev))


    def show(self, event=None):
        if not self.tip:
            self.tip = tk.Toplevel(self.root)
            self.tip.wm_overrideredirect(True)
            self.label = tk.Label(self.tip, text="", background="#FFFFE0", relief="solid",
                                  borderwidth=1, justify=tk.LEFT, padx=6, pady=5, font=self.font)
            self.label.pack()
            self.tip.bind("<Leave>", self.hide, add=True)
            self.tip.bind("<Button-1>", self.hide, add=True)
            self.label.bind("<Escape>", self.hide, add=True)

            self.refresh(event)


    def refresh(self, event=None):
        if self.tip:
            pointer_x = self.root.winfo_pointerx()
            pointer_y = self.root.winfo_pointery()
            x = pointer_x + 75
            if not self.above:
                y = pointer_y + 25
            else:
                y = pointer_y - self.tip.winfo_height() - 25
            self.tip.wm_geometry(f"+{x}+{y}")
            self.tip.wm_attributes("-topmost", True)
            self.refresh_tooltip_text(event)


    def refresh_tooltip_text(self, event=None):
        self.label.configure(text=self.text)


    def hide(self, event=None):
        if self.show_timer:
            self.root.after_cancel(self.show_timer)
        if self.tip:
            self.tip.destroy()
        self.tip = None


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Tooltip")
    root.geometry("500x500")
    Tooltip(root, "Tooltip Example")
    root.mainloop()
