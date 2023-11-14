import tkinter as tk
from tkinter import INSERT, END



# class LineHandling(ScrolledText):
class LineHandling:

    def jump_to_similar_line(self, event=None, direction=1):

        def find_similar_line(target, line_nr_1, lines, direction):
            line_nr_0 = line_nr_1 - 1
            num_lines = len(lines)
            if num_lines == 0:
                return 0
            target = target.strip()
            d = direction == 1 and 1 or 0
            start = (line_nr_0 + d) % num_lines
            if direction == 1:
                numbered_lines = list(enumerate(lines[start:] + lines[:start]))
            else:
                numbered_lines = list(enumerate(lines[:start][::-1] + lines[start:][::-1]))
            for i, line in numbered_lines:
                if line.strip() == target:
                    if direction == 1:
                        return ((i + start) % num_lines) + 1
                    else:
                        return ((start - i + num_lines - 1) % num_lines) + 1
            return 0


        from Sheet import Sheet
        sheet: Sheet = self # todo ...
        cursor_pos = sheet.index(INSERT)
        line_nr = int(cursor_pos.split('.')[0])
        current_line = sheet.get(f"{line_nr}.0", f"{line_nr}.end")
        if not current_line.strip():
            return
        lines = sheet.get(1.0, END).splitlines()
        jump_line = find_similar_line(current_line, line_nr, lines, direction)
        if jump_line:
            jump_index = f"{jump_line}.{0}"
            sheet.mark_set(INSERT, jump_index)
            sheet.see(jump_index)

    def jump_to_limit(self, e: tk.Event):
        pos = self.vbar.get()
        top, bottom, *_ = pos
        if e.keysym == 'Prior' and top == 0.0:
            limit = "1.0"
        elif e.keysym == 'Next' and bottom == 1.0:
            limit = tk.END
        else:
            return

        self.mark_set(tk.INSERT, limit)
        self.see(tk.INSERT)
