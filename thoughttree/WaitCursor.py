class WaitCursor():
    def __init__(self, widget):
        self.widget = widget

    def __enter__(self):
        self.widget.config(cursor='watch')
        self.widget.update()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.widget.config(cursor='')
            self.widget.update()
        except:
            pass
