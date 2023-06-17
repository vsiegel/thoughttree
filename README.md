# Thoughttree
Interact with large language models in alternative ways.

## Why?

#### Work with alternative branches of conversation
   - Your conversation can branch in two or more at any time
   - Avoid having irrelevant information context 
   - Easily make a new turn in the conversation, without giving up the old 
   - No need to delete something interesting  
   - A model has more answers if you ask it again

#### Know your cost
   - Your quota may be limited
   - The cost in tokens or money may be low - but  

#### Edit your history
   - Edit the history
   - Remove what is not important

#### Have the tools you need
   - Safe the code blocks with a generated file name
   - Run the code
   - Render the content, like LaTex or SVG
   - Open applications like CSV
   - see below under "Features" 

#### [Note: This is only partially implemented. See [ This software is not released](https://github.com/vsiegel/thoughttree/discussions/73) ]

A user interface for GPT-4 and ChatGPT, that supports the common way of chatting with the model, message by message in a linear way. But above that, it supports a whole new perspective: Branch the conversation for less related topics. And work with this conversation as something that is easy to change, instead of seeing it as the static history  of a session.


Prompts and linear chats are a powerful method. But there is not only one way a conversation can develop. Work in multiple timelines, without deleting what happened before. 

A conversation with **GPT-4** or **ChatGPT** can be linear, so that each line produced depends on everything that was input or output before. That happens - in scientific experiments, but much less often in real life use. If it is not linear, that means there are parts in the context of a completion that are not needed. The model spends just the same attention, it may distort your results. You pay for these tokens. And chances are that you even pay more for them than for the tokens you actually use. That is hard to avoid, with complex manual cut and paste work, or often even impossible. thoughttree solves this problem by providing the right tools. And a lot more.

   __An OpenAI API key is required.__  
   (https://platform.openai.com/signup, https://platform.openai.com/account/api-keys)

## Features

- Work with **multiple completions**, just like you would generate multiple images with a generative image AI.
- You can easily work in **alternative conversations**. Go **back** to try something else, without losing anything.
- You can **freely edit the history**: What the AI thinks you have said, and what the AI thinks it has said itself.
- You are working on **continuous text**, but the messages of you and the AI are kept separate.  
- You can change options like temperature or even **change the model** in the middle of the conversation.
- You have control of what happens: **Count tokens**, see current options, see why the previous completion ended.
- Manage **what needs to be in the context**, when it gets difficult. 
- **Navigate the history.** And the history tree.
- Handle code sections and files. **Save** them, **include** them, **run** them.
- **Save** sections to files 
- **Run** code blocks
- Create **documents** from code sections, like **PDF from LaTex** or **png from SVG**
- **Include** files
- **Reduce cost** by not including irrelevant text in the context, without deleting it.
- **Switch models by hotkey** in a second: Press Ctrl+4 to switch from ChatGPT to GPT-4.
- Use a **quick and cheap model first**, and just **rerun** the prompt on a better model. 
- Keep topics separate: If you have query on a new, related topic,  **have only the relevant parts** of the history in the context: Other parts may hinder, and cause costs. 

----

### Notes:
The program expects an OpenAI API key provided in the shell environment, for example in the file `~/.profile` as 
`export OPENAI_API_KEY="..."`

----

 - https://www.python.org/downloads/
 - https://pypi.org/project/thoughttree/
 - https://github.com/vsiegel/thoughttree
 - https://openai.com/chatgpt
 - https://openai.com/gpt-4
 - https://arxiv.org/abs/2303.08774
 - https://cdn.openai.com/papers/gpt-4.pdf
----

Feature requests are welcome - file a "feature request" issue.
