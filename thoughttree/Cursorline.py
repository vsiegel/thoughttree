class Cursorline:
    def __init__(self, sheet):
        self.sheet = sheet
        self.sheet.tag_config('cursorline', background='#fcfaed', borderwidth=1, relief="raised", selectbackground="#4682b4", selectforeground="white")
        self.sheet.bindtags(self.sheet.bindtags() + ("cursorline_last",))
        if not self.sheet.bind_class("cursorline_last"):
            self.sheet.bind_class("cursorline_last", '<KeyRelease>', self.show)
            self.sheet.bind_class("cursorline_last", '<Button-1>',   self.show)
            self.sheet.bind_class("cursorline_last", "<FocusIn>",    self.show)
            self.sheet.bind_class("cursorline_last", "<FocusOut>",   self.clear)

    def show(self, e=None, add=True):
        if not e.widget.winfo_exists():
            return
        if e.widget.cget("takefocus") == "0":
            return
        e.widget.tag_remove('cursorline', 1.0, "end")
        if add:
            e.widget.tag_add('cursorline', 'insert display linestart', 'insert display lineend+1c')

    def clear(self, e=None):
        from TreeSheet import TreeSheet
        try:
            if not isinstance(e.widget, TreeSheet) or isinstance(e.widget.focus_get(), TreeSheet):
                self.show(e, add=False)
        except KeyError:
            pass

