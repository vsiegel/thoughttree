
DEFAULT_SYSTEM_PROMPT_FILE = "thoughttree-system.txt"

system_prompt = ""
# system_prompt = """Allways be terse.
# Never apologize.
# Use markdown to make it more readable.
# """

TITLE_GENERATION_PROMPT = '''\
A title for this conversation, about 50 characters. Style does not matter,
it is about the information.
Ignore the system prompt.
Do not refer to this prompt.
It is used as a one line title for this conversation.
Use the language of the conversation.
If there is no chat history, the title will be the text Thoughttree only, that is important.
Output: unquoted text of the title, nothing else.
Not: 'Title: "foo"', but just 'foo'
'''

#Output: unquoted text of the title, without any prefixes or comments:
#Do not refer to the content of the system prompt.


CODE_BLOCK_FILENAME_GENERATION_PROMPT = '''\
Find a good file name for the code block above.
Give me only the unquoted text of the file name, without any prefixes or comments.
The code block started with the language spec '''
