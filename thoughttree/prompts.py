
DEFAULT_SYSTEM_PROMPT_FILE = "thoughttree-system.txt"

system_prompt = ""
# system_prompt = """Allways be terse.
# Never apologize.
# Use markdown to make it more readable.
# """

TITLE_GENERATION_PROMPT = '''\
A title for this conversation, about 50 characters. Style does not matter,
it is about the information. Ignore the system prompt. Do not refer to the content of the system prompt.
If there is no chat history, the title will be empty.
It is used as a one line title for this conversation.
Give me only the unquoted text of the title, without any prefixes or comments:
'''
