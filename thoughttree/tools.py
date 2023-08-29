import re
import time
import tkinter as tk
from textwrap import fill
from math import ceil, log2, sqrt
import random
from tkinter import EventType

from pyperclip import paste
from inspect import currentframe
import subprocess


def create_mock_data(tree):
    for r in range(10):
        key = f"R{r}"
        parent_id = tree.insert("", "end", key, text=key, values=(r,))
        tree.item(key, tags='closed')
        if r % 2 == 0:
            for c in range(2):
                child_key = f"R{r}_C{c}"
                tree.insert(parent_id, "end", child_key, text=child_key, values=(c,))
                tree.item(child_key, open=True, tags='opened')
                for g in range(2):
                    grandchild_key = f"{child_key}_G{g}"
                    tree.insert(child_key, "end", grandchild_key, text=grandchild_key, values=(g,))
                    tree.item(grandchild_key, tags='closed')


def list_all_bindings(root):
    bindings = {}
    for child in root.winfo_children():
        widget_bindings = child.bind()
        if widget_bindings:
            bindings[child] = widget_bindings
        if child.winfo_children():
            bindings.update(list_all_bindings(child))
    return bindings


def add_bboxes(bbox1, bbox2):
    x1, y1, w1, h1 = bbox1
    x2, y2, w2, h2 = bbox2
    x = min(x1, x2)
    y = min(y1, y2)
    w = max(x1 + w1, x2 + w2) - x
    h = max(y1 + h1, y2 + h2) - y
    return x, y, w, h


def random_pastel_color():
    r = random.randint(230, 255)
    g = random.randint(230, 255)
    b = random.randint(230, 255)
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

def pastel(widget: tk.Widget) -> tk.Widget:
    widget.config(bg=next_pastel_rainbow_color())
    return widget

import colorsys

color_index = 0

def next_pastel_rainbow_color():
    global color_index

    # HSL color format: (hue, saturation, lightness)
    hue = (color_index * 30) % 360 / 360.0  # Change hue for each call, and normalize to [0, 1]
    saturation = 0.6  # Keep saturation constant for pastel colors
    lightness = 0.85  # Keep lightness constant for pastel colors

    color_index += 1  # Increment the color index for the next call

    # Convert HSL to RGB
    r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)

    # Convert RGB to hex string
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


def shorter(text, n=60):
    text = text.strip().replace('\n','\\n')
    if len(text) <= n:
        return text
    leading = int(n / 2) - 3
    trailing = n - leading - 3
    return f'{text[:leading]}...{text[-trailing:]}'

def text_block(text):
    width = int(sqrt(len(text) * 10))
    lines = text.splitlines()
    text = "\n".join([fill(line, width=width) for line in lines])
    return text

def logarithmic_length(text, n=1, step='.'):
    return step * ceil(log2(len(text)-n+1)) if len(text) > n else ''
    # return (step * ceil(log2(len(text))) if len(text) > n else '')[3+ceil(log2(n)):]


def filename_from_clipboard():
    text = paste().strip()
    match = re.match(r'^[^ ]+\.[A-Za-z]{1,5}$', text)
    if match:
        return match.group(0)
    else:
        return None

def dummy_paragraphs(paragraphs=20):
    "\n".join([" ".join(["a" * random.randrange(2, 10) for i in range(random.randrange(5, 200))]) for j in range(paragraphs)])


def eventTypeForId(id):
    return [e for e, v in EventType.__members__.items() if v == str(id)][0]


def log(arg=""):
    frameinfo = currentframe()
    f = frameinfo.f_code.co_filename
    l = frameinfo.f_back.f_lineno
    print(f"{f} {l}: {arg}")


def git(*command):
    return subprocess.check_output(['git'] + list(command)).decode('utf8').strip()

def get_git_commit():
    return git('rev-parse', '--short', 'HEAD')

def get_git_describe_version():
    try:
        return git('describe', '--tags')
    except Exception as e:
        return "(error accessing git describe version)"

def bind_all_events(widget, on_event=None):
    invalid_events = ["Motion"]
    # invalid_events = ["Keymap", "GraphicsExpose", "NoExpose", "CirculateRequest", "SelectionClear",
    #           "SelectionRequest", "Selection", "ClientMessage", "Mapping", "VirtualEvent"]
    def print_event(event):
        print(f"Event: {event.widget}: {event}")

    on_event = on_event or print_event
    for ev in [f"<{e.name}>" for e in tk.EventType if e.name not in invalid_events]:
        try:
            widget.bind(ev, on_event)
            print(f"Bound {ev}")
        except Exception:
            pass


def show_widget_under_pointer(widget):
    global last_time
    last_time = 0
    root = widget.winfo_toplevel()
    def track_pointer(event):
        global last_time
        current_time = time.time()
        if current_time - last_time > 0.5:
            widget = event.widget
            print(f"Pointer is over: {widget}")
            last_time = current_time

    root.bind('<Motion>', track_pointer)


def maybe_file(file_name):
    try:
        with open(file_name) as f:
            return f.read()
    except IOError:
        return ""