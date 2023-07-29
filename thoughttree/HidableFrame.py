import tkinter as tk
from tkinter import BOTTOM, X


class HidableFrame(tk.Frame):
    def __init__(self, master, hidden=False, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.hidden = hidden
        self.child_pack_info = None
        self.own_pack_info = None


    def hide(self, e=None):
        child = list(self.children.values())[0]
        if self.hidden:
            # for widget, pack_info in self.info.items():
            #     self.info[widget.name] = widget.pack_info()

            child.pack(self.child_pack_info)
            self.pack(self.own_pack_info)
            # print(f'    hidden: {self.master.pack_slaves()}')
        else:
            # slaves = self.master.pack_slaves()
            # self.info = {}
            # for widget in slaves:
            #     self.info[widget.name] = widget.pack_info()

            # print(f'not hidden: {self.master.pack_slaves()}')
            self.child_pack_info = child.pack_info()
            self.own_pack_info = self.pack_info()
            child.pack_forget()
            self.pack_forget()


        self.hidden = not self.hidden
