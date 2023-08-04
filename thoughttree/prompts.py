
DEFAULT_SYSTEM_PROMPT_FILE = "thoughttree-system.txt"

system_prompt = ""
# system_prompt = """Allways be terse.
# Never apologize.
# Use markdown to make it more readable.
# """


CODE_BLOCK_FILENAME_GENERATION = '''\
Find a good file name for the code block above.
Give me only the unquoted text of the file name, without any prefixes or comments.
The code block started with the language spec '''


CODE_BLOCK_MULTI_FILENAME_GENERATION = '''\
Generate three titles for the three blocks below.
The total length of the titels combined need to be less than 100 char.
In one row, sep by | like foo|bar - no spaces around "|":
---
1:

---
2:

---
3:

---
'''
