import os
from tkinter import Widget

from git import Repo


class PeriodicGitCommit():
    def __init__(self, parent: Widget, periodSeconds, committed_files, git_dir):
        self.repo = Repo.init(git_dir, bare=True)
        parent.after(periodSeconds * 1000, )

    class FileWriter():
        def __init__(self, file_path):
            self.content = None

        def collect_content(self):
            pass

        def write(self, file_name):
            old = self.content.__hash__()
            self.collect_content()
            if old == self.content.__hash__():
                return

            with open(file_name, "w") as f:
                f.write(self.content)
            self.content = None
