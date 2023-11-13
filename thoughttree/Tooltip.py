import tkinter as tk


class Tooltip :
    def __init__(self, widget: tk.Widget, text) :
        self.widget = widget
        self.root = widget.winfo_toplevel()

        self.text = text
        self.tip = None
        self.label = None
        self.timer = None
        self.last_y = None
        self.delay_ms = 1000

        widget.bind("<Enter>", self.create_tip_later, add=True)
        widget.bind("<Leave>", self.remove_tip, add=True)
        widget.bind("<Unmap>", self.remove_tip, add=True)
        widget.bind("<Destroy>", self.remove_tip, add=True)
        self.root.bind("<Motion>", self.update_tip, add=True)


    def create_tip_later(self, event):
        if self.tip:
            return
        self.timer = self.root.after(self.delay_ms, lambda ev=event: self.create_tip(ev))


    def create_tip(self, event=None):
        if not self.tip:
            self.tip = tk.Toplevel(self.root)
            self.tip.wm_overrideredirect(True)
            self.label = tk.Label(self.tip, text="", background="#FFFFE0", relief="solid",
                                  borderwidth=1, justify=tk.LEFT, padx=6, pady=5, font=("sans-serif", 11))
            self.label.pack()
            self.tip.bind("<Leave>", self.remove_tip, add=True)
            self.tip.bind("<Button-1>", self.remove_tip, add=True)
            self.label.bind("<Escape>", self.remove_tip, add=True)
            # self.widget.bind("<Destroy>", self.remove_tip)
            self.update_tip(event)


    def update_tip(self, event=None):
        if event:
            self.last_y = event.y
        if self.tip:
            x = self.root.winfo_pointerx() + 75
            y = self.root.winfo_pointery() + 25
            self.tip.wm_geometry(f"+{x}+{y}")
            self.tip.wm_attributes("-topmost", True)
            self.refresh_tooltip_text(event)


    def refresh_tooltip_text(self, event=None):
        self.label.configure(text=self.text)


    def remove_tip(self, event):
        if self.timer:
            self.root.after_cancel(self.timer)
        if self.tip:
            self.tip.destroy()
        self.tip = None


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Tooltip")
    root.geometry("500x500")
    Tooltip(root, "Tooltip Example")
    root.mainloop()
