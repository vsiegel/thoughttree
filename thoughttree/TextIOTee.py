import io


class TextIOTee(io.TextIOBase):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __del__(self):
        for s in (self.a, self.b):
            s.close()

    def write(self, data):
        for s in (self.a, self.b):
            s.write(data)

    def flush(self):
        for s in (self.a, self.b):
            s.flush()
