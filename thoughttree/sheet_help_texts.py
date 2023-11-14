
def sheet_help(label):
    return label, sheet_help_texts[label]

sheet_help_texts = {
    "System prompt - [?]":
        "Enter a system prompt for ChatGPT in this text box. This prompt will guide the model's responses."
        " For instance, if you want the model to speak like Shakespeare, you could use a prompt like"
        " 'You are an AI trained in the style of Shakespeare.' Be as specific as possible to get the best results.",

    "User prompt - Chat - [?]":
        "In this text box, you need to input your general prompt for ChatGPT. This is essentially your conversation"
        " starter or question, which will guide the AI model's responses. For example, if you want to write a story,"
        " your prompt could be 'Once upon a time in a kingdom far away...'. If you're looking for answers to a specific"
        " question, simply type your question here, such as 'What is the process of photosynthesis?'. Remember, the more"
        " specific and detailed your prompt, the more accurate and helpful the model's response will be. This can include"
        " setting a context, defining a role, or asking a question. Don't hesitate to experiment with different types"
        " of prompts to see the various responses!"
}
