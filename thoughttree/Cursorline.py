class Cursorline:
    def __init__(self, sheet):
        self.sheet = sheet
        self.configure_cursorline()

    def cursorline(self, e, add=True):
        if not e.widget.winfo_exists():
            return
        takefocus = not e.widget.cget("takefocus") == "0"
        if not takefocus:
            return
        e.widget.tag_remove('cursorline', 1.0, "end")
        if add:
            e.widget.tag_add('cursorline', 'insert display linestart', 'insert display lineend+1c')

    def cursorline_remove(self, e):
        self.cursorline(e, add=False)

    def configure_cursorline(self):
        self.sheet.tag_config('cursorline', background='#FCFAED', selectbackground="#4682b4", selectforeground="white")
        # self.sheet.tag_config('cursorline', borderwidth=1, relief="solid", selectbackground="#4682b4", selectforeground="white")
        self.sheet.bindtags(self.sheet.bindtags() + ("last",))
        self.sheet.bind_class("last", '<KeyRelease>', self.cursorline)
        self.sheet.bind_class("last", '<Button-1>', self.cursorline)
        self.sheet.bind_class("last", "<FocusIn>", self.cursorline)
        self.sheet.bind_class("last", "<FocusOut>", self.cursorline_remove)
