import io


class ExceptionBlockedIO(io.TextIOBase):
    def __init__(self, out):
        print(out)
        self.out = out

    def write(self, data):
        try:
            self.out.write(data)
        except Exception:
            pass
