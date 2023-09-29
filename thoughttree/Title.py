from Notebook import Notebook


def split_title(hierarchical_id):
    if hierarchical_id:
        hierarchical_id_and_title = hierarchical_id.split(' ', 1)
        hierarchical_id = hierarchical_id_and_title[0]
        title = len(hierarchical_id_and_title) == 2 and hierarchical_id_and_title[1] or ""
        levels = hierarchical_id.split('.')
    else:
        title = ''
        levels = []
    return hierarchical_id, levels, title

def next_level(hierarchical_id):
    hierarchical_id, levels, title = split_title(hierarchical_id)
    levels += ['1']

    result = '.'.join(levels)
    if title:
        result += " " + title
    return result


def next_equal(hierarchical_id):
    hierarchical_id, levels, title = split_title(hierarchical_id)
    levels = levels or ['0']
    levels = levels[:-1] + [str(int(levels[-1]) + 1)]

    result = '.'.join(levels)
    if title:
        result += " " + title
    return result

def short(widget_names):
    return list(map(lambda s: s[-10:], widget_names))


def new_sibling_title(sibling_notebook):
    last_tab_label = sibling_notebook and sibling_notebook.tabs() and sibling_notebook.tab(len(sibling_notebook.tabs()) - 1, "text") or ""
    next_tab_label = next_equal(last_tab_label)
    return next_tab_label

def new_child_title(parent: Notebook):
    if parent and parent.tabs():
        parent_tab_label = parent.tab(parent.select(), "text")
    else:
        parent_tab_label = ""

    child_tab_label = next_level(parent_tab_label)
    return child_tab_label


class Title():

    PROMPT = '''\
A title for this conversation, about 50 characters. Style does not matter,
it is about the information.
Ignore the system prompt.
Do not refer to this prompt or to the title.
It is used as a one line title for this conversation.
Use the language of the conversation.
If there is no chat history, the title will be the text Thoughttree only, that is important.
Do not use the name otherwise.
Do not use a prefix like "Title:"!.
Output the unquoted text of the title, nothing else.
'''

#Output: unquoted text of the title, without any prefixes or comments:
#Do not refer to the content of the system prompt.

    GEN_THRESHOLD = 20
