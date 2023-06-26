
# The help text are generated by GPT-4, based on the source code of the menu (which does
# not contain comments) and minimal prompting.

menu_help = {
    "New Window": "Opens a new Thoughttree window, allowing you to work on multiple chats simultaneously.",
    "New Main Tab": "Opens a new main tab in the current window, providing a separate workspace within the same window.",
    "Save Chat": "Saves the entire chat content to a file, allowing you to store and review conversations later.",
    "Save Section": "Saves a selected section of the chat to a file, useful for extracting specific parts of a conversation.",
    "Save Code Block": "Saves a selected code block to a file, enabling you to reuse or share code snippets.",
    "Close Empty Tab": "Closes the current tab if it is empty, helping to declutter your workspace.",
    "Quit": "Closes the Thoughttree application, ending all active sessions.",
    "Cut": "Cuts the selected text and stores it in the clipboard, allowing you to move text within or between documents.",
    "Copy": "Copies the selected text to the clipboard without removing it from the document, useful for duplicating content.",
    "Paste": "Pastes the text from the clipboard at the cursor position, inserting copied or cut content.",
    "Delete": "Deletes the selected text or the character at the cursor position without storing it in the clipboard.",
    "Undo": "Reverts the last text edit, allowing you to correct mistakes or revert unwanted changes.",
    "Redo": "Reapplies the previously undone text edit, restoring the text to its state before the undo action.",
    "Select All": "Selects all the text in the current text widget, making it easy to copy, cut, or delete the entire content.",
    "Search at Google": "Searches the selected text on Google, providing quick access to search results for the highlighted text.",
    "Insert Current Time": "Inserts the current date and time at the cursor position, useful for timestamping notes or messages.",
    "Include Date in System Prompt": "Includes the current date in the system prompt, providing a reference for when the prompt was generated.",
    "Copy Title": "Copies the title of the current chat to the clipboard, allowing you to easily share or reference the chat title.",
    "Show System Prompt": "Toggles the visibility of the system prompt, allowing you to hide or display the prompt as needed.",
    "Show Tree": "Toggles the visibility of the tree view, enabling you to show or hide the tree structure of your chats.",
    "Count Tokens": "Counts the tokens in the current text, providing an estimate of the text's complexity and cost for text generation.",
    "Run Code Block": "Runs the selected code block, executing any embedded code within the chat.",
    "Update Window Title": "Updates the window title based on the current chat, providing a clear identifier for the active chat.",
    "Increase Font Size": "Increases the font size of the text, making it easier to read.",
    "Decrease Font Size": "Decreases the font size of the text, allowing you to fit more content on the screen.",
    "Reset Font Size": "Resets the font size to its default value, restoring the original text appearance.",
    "Toggle Monospace": "Toggles between monospace and proportional fonts, allowing you to switch between fixed-width and variable-width characters.",
    "Toggle Scrolling Output": "Toggles automatic scrolling of the output, enabling you to control whether the output scrolls as new content is generated.",
    "Ring Bell When Finished": "Rings a bell when the text generation is completed, providing an audible notification of completion.",
    "Toggle Wrap Lines": "Toggles line wrapping in the text widget, allowing you to control whether long lines wrap to the next line or extend off-screen.",
    "Generate Titles": "Generates titles for the current text, providing suggestions for descriptive headings.",
    "Calculate Cost": "Calculates the cost of generating the current text, estimating the resources required for text generation.",
    "Next Similar Line": "Jumps to the next line with similar content, allowing you to quickly navigate between related lines.",
    "Previous Similar Line": "Jumps to the previous line with similar content, enabling you to move backward through related lines.",
    "Next Message": "Jumps to the next message in the chat, providing a quick way to navigate between messages.",
    "Previous Message": "Jumps to the previous message in the chat, allowing you to move backward through messages.",
    "Next Paragraph": "Completes the current text and starts a new paragraph, providing a clear separation between ideas.",
    "Next Line": "Completes the current text and starts a new line, continuing the conversation on a new line.",
    "Continue Directly": "Continues the current text without starting a new line or paragraph, generating a seamless continuation of the conversation.",
    "Fork Conversation": "Forks the current conversation into a new branch, allowing you to explore alternative paths in the chat.",
    "Complete in Branch": "Completes the current text in a new conversation branch, generating text that diverges from the main conversation.",
    "Complete Alternatives": "Generates alternative completions for the current text, providing a variety of potential responses.",
    "Complete 2 Times": "Generates 2 completions for the current text, offering two different options for continuing the conversation.",
    "Complete 3 Times": "Generates 3 completions for the current text, providing three unique options for continuing the conversation.",
    "Complete 5 Times": "Generates 5 completions for the current text, offering a greater variety of potential responses.",
    "Complete Multiple...": "Prompts for the number of completions to generate, allowing you to specify the desired number of alternatives.",
    "Complete Multiple Again": "Generates the same number of completions as the last multiple completion, providing consistency in the number of alternatives.",
    "Cancel": "Cancels the current text generation, stopping the generation process and discarding the generated content.",
    "Max Tokens...": "Configures the maximum number of tokens for text generation, allowing you to control the length and complexity of generated text.",
    "Temperature...": "Configures the temperature for text generation, adjusting the randomness and creativity of the generated content.",
    "Increase Temperature": "Increases the temperature for text generation, resulting in more random and creative output.",
    "Decrease Temperature": "Decreases the temperature for text generation, producing more focused and conservative output.",
    "Temperature 0.0": "Sets the temperature for text generation to 0.0, generating deterministic and highly focused output.",
    "API Key...": "Configures the API key for the text generation service, enabling access to the text generation features.",
    "Test": "Runs a test function, useful for debugging and experimentation.",
    "Debug Info": "Displays debug information, providing insights into the internal workings of the application.",
    "About": "Displays information about the Thoughttree application, including version and developer details."
}

menu_command_help_refined = { # "entries that you could describe in more detail"
    "New Window": "Opens a new Thoughttree window, allowing you to work on multiple chats simultaneously. Each new window operates independently, enabling you to manage and organize your conversations more efficiently.",
    "New Main Tab": "Opens a new main tab in the current window, providing a separate workspace within the same window. This allows you to keep multiple chats organized and accessible without opening additional windows.",
    "Save Chat": "Saves the entire chat content to a file, allowing you to store and review conversations later. The saved file can be opened and edited in any text editor, making it easy to share or reference the chat content.",
    "Save Section": "Saves a selected section of the chat to a file, useful for extracting specific parts of a conversation. This feature enables you to isolate and save important information, code snippets, or any other relevant content from the chat.",
    "Save Code Block": "Saves a selected code block to a file, enabling you to reuse or share code snippets. The saved code block can be imported into other projects or shared with collaborators, streamlining the development process.",
    "Close Empty Tab": "Closes the current tab if it is empty, helping to declutter your workspace. This feature prevents the accumulation of unnecessary empty tabs, ensuring a clean and organized working environment.",
    "Toggle Monospace": "Toggles between monospace and proportional fonts, allowing you to switch between fixed-width and variable-width characters. Monospace fonts are useful for aligning text, especially when working with code or tabular data, while proportional fonts provide a more natural reading experience for general text.",
    "Toggle Scrolling Output": "Toggles automatic scrolling of the output, enabling you to control whether the output scrolls as new content is generated. When enabled, the output will automatically scroll to show the latest generated content. When disabled, the output will remain stationary, allowing you to review previous content without interruption.",
    "Ring Bell When Finished": "Rings a bell when the text generation is completed, providing an audible notification of completion. This feature is helpful for multitasking, as it allows you to focus on other tasks while waiting for the text generation to finish.",
    "Fork Conversation": "Forks the current conversation into a new branch, allowing you to explore alternative paths in the chat. This feature enables you to generate multiple responses or scenarios based on the current conversation, providing a way to test different ideas or approaches without affecting the main chat.",
    "Complete in Branch": "Completes the current text in a new conversation branch, generating text that diverges from the main conversation. This feature allows you to explore alternative outcomes or responses without altering the original conversation, making it easy to compare and contrast different ideas.",
    "Complete Alternatives": "Generates alternative completions for the current text, providing a variety of potential responses. This feature enables you to explore multiple ways to continue the conversation, giving you greater flexibility and control over the chat content.",
    "Max Tokens...": "Configures the maximum number of tokens for text generation, allowing you to control the length and complexity of generated text. By setting a limit on tokens, you can ensure that the generated content stays within a specific length or complexity range, making it more manageable and easier to read.",
    "Temperature...": "Configures the temperature for text generation, adjusting the randomness and creativity of the generated content. A higher temperature results in more diverse and creative output, while a lower temperature produces more focused and conservative text. This setting allows you to fine-tune the balance between creativity and coherence in the generated content.",
    "API Key...": "Configures the API key for the text generation service, enabling access to the text generation features. By entering a valid API key, you can connect to the text generation service and use its capabilities to generate content within the Thoughttree application."
}

menu_command_help_refined_again = { # more entries that you could describe in more detail
    "Quit": "Closes the Thoughttree application, ending all active sessions and closing all open windows. Before quitting, ensure that you have saved any important chat content or settings to avoid losing your work.",
    "Select All": "Selects all the text in the current text widget, making it easy to copy, cut, or delete the entire content. This feature is useful for quickly selecting large amounts of text or when you want to replace the entire content of the text widget.",
    "Insert Current Time": "Inserts the current date and time at the cursor position, useful for timestamping notes or messages. The inserted timestamp is formatted as 'YYYY-MM-DD HH:MM:SS', providing a clear and concise representation of the current date and time.",
    "Include Date in System Prompt": "Includes the current date in the system prompt, providing a reference for when the prompt was generated. This feature is useful for tracking the date of specific prompts or for organizing your conversations based on the date.",
    "Copy Title": "Copies the title of the current chat to the clipboard, allowing you to easily share or reference the chat title. This feature is useful for sharing chat titles with collaborators, referencing chat titles in other documents, or for organizing your chats based on their titles.",
    "Show System Prompt": "Toggles the visibility of the system prompt, allowing you to hide or display the prompt as needed. Hiding the system prompt can help declutter your workspace, while displaying the prompt provides context and guidance for the conversation.",
    "Show Tree": "Toggles the visibility of the tree view, enabling you to show or hide the tree structure of your chats. The tree view provides a visual representation of the chat hierarchy, making it easy to navigate and manage complex conversations.",
    "Count Tokens": "Counts the tokens in the current text, providing an estimate of the text's complexity and cost for text generation. Token count is an important factor when working with text generation services, as it can affect the cost and processing time for generating content.",
    "Run Code Block": "Runs the selected code block, executing any embedded code within the chat. This feature is useful for testing and debugging code snippets, as well as for executing commands or scripts directly within the chat environment.",
    "Update Window Title": "Updates the window title based on the current chat, providing a clear identifier for the active chat. This feature ensures that the window title accurately reflects the content of the chat, making it easier to manage and navigate multiple chats.",
    "Increase Font Size": "Increases the font size of the text, making it easier to read. This feature is especially useful for users with visual impairments or for working with high-resolution displays where the default font size may be too small.",
    "Decrease Font Size": "Decreases the font size of the text, allowing you to fit more content on the screen. This feature is useful for working with large documents or for users who prefer smaller font sizes for readability.",
    "Toggle Wrap Lines": "Toggles line wrapping in the text widget, allowing you to control whether long lines wrap to the next line or extend off-screen. Line wrapping can improve readability by ensuring that text does not extend beyond the visible screen area, while disabling line wrapping can provide a more compact view of the text.",
    "Generate Titles": "Generates titles for the current text, providing suggestions for descriptive headings. This feature is useful for organizing your chats or for creating meaningful titles for sections of text, making it easier to navigate and understand the content.",
    "Calculate Cost": "Calculates the cost of generating the current text, estimating the resources required for text generation. This feature is useful for managing the cost and resource usage of text generation services, ensuring that you stay within your budget and resource limits.",
    "Next Message": "Jumps to the next message in the chat, providing a quick way to navigate between messages. This feature is useful for reviewing previous conversations or for quickly moving through a chat to find specific messages or content.",
    "Previous Message": "Jumps to the previous message in the chat, allowing you to move backward through messages. This feature is useful for reviewing earlier parts of a conversation or for finding specific messages or content that occurred earlier in the chat.",
    "Complete Multiple...": "Prompts for the number of completions to generate, allowing you to specify the desired number of alternatives. By entering a custom number, you can generate a specific number of alternative completions, providing a tailored set of options for continuing the conversation.",
    "Complete Multiple Again": "Generates the same number of completions as the last multiple completion, providing consistency in the number of alternatives. This feature is useful for generating a consistent set of options across multiple completions, ensuring a similar level of variety in each set of alternatives."
}