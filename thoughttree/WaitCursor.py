class WaitCursor():
    def __init__(self, widget):
        self.widget = widget
        self.saved_cursor = None

    def __enter__(self):
        self.saved_cursor = self.widget.cget('cursor')
        self.widget.config(cursor='watch')
        self.widget.update()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.widget.config(cursor=self.saved_cursor)
            self.widget.update()
        except:
            pass
