from Model import Model
from Notebook import Notebook


def split_title(hierarchical_id):
    if hierarchical_id:
        hierarchical_id_and_title = hierarchical_id.split(' ', 1)
        hierarchical_id = hierarchical_id_and_title[0]
        title = len(hierarchical_id_and_title) == 2 and hierarchical_id_and_title[1] or ""
        levels = hierarchical_id.strip('.').split('.')
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
    return '.'.join(levels)


def new_sibling_title(sibling_notebook):
    previous_tab_label = sibling_notebook and sibling_notebook.tabs() and sibling_notebook.tab(len(sibling_notebook.tabs()) - 1, "text") or ""
    # print(f"{previous_tab_label=}")
    next_tab_label = next_equal(previous_tab_label)
    # print(f"{next_tab_label=}")
    return next_tab_label

def new_child_title(parent: Notebook):
    if parent and parent.tabs():
        parent_tab_label = parent.tab(parent.select(), "text")
    else:
        parent_tab_label = ""

    child_tab_label = next_level(parent_tab_label)
    return child_tab_label

def outline(title: str):
    # Create a widget name for a title starting with an outline id "1.2 Foo Bar" -> "1-2"
    return title.split(maxsplit=1)[0].rstrip(".,:;").replace(" ", "_").replace(".", "_")

class Title():
    model_name = 'gpt-3.5-turbo'
    # model_name = 'gpt-3.5-turbo-16k'

    model = None

    PROMPT = '''\
Generate a short title for this conversation, about 3 to 4 words. 
Style does not matter, it is about the information.
A title can not be fully generic, matching almost any text. An example for a useless title is "Short Conversation Title". It literally says nothing about the text.
Ignore the system prompt.
Do not refer to this prompt or to the title.
The title can not contain newlines.
It is used as a one line title for this conversation.
Use the language of the conversation.
The title should not be just the continuation of the text. 
For example, if the input was:
1 2 3, Output: 4, then the title should not be 5. The title should describe the earlier text.
The title must not be the start of the input or a continuation of the input. It can only be one line. It needs to be short.

Do not use the name otherwise.
Do not use a prefix like "Title:"!.
Output the unquoted text of the title, nothing else.
The title needs to be short. It is used as a window title, or a tab title that may have limited space so that only the first couple of characters are shown.
'''
# If there is no chat history at all, the title will be the text "(empty)" only, that is important.

#Output: unquoted text of the title, without any prefixes or comments:
#Do not refer to the content of the system prompt.

    # def __init__(self, parent_notebook: Notebook):
    #     self.generation_model = Model(Title.model_name)

    @staticmethod
    def initialize():
        Title.model = Model(Title.model_name)
