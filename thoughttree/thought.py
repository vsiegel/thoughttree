from configargparse import ArgumentParser

from tools import maybe


class Thought:
    def __init__(self):
        parser = ArgumentParser(prog="thought",
            description='Interact with a large language model on the command line',
            exit_on_error=False)
        add = parser.add_argument
        add('prompt',                    nargs='?',              default="",   type=str, help='Prompt for the model, text to be completed')
        add('-p', '--prompt-file',       dest='promptFile',      default="",   type=str, help='File containing the prompt')
        add('-s', '--system-prompt',     dest='systemPrompt',    default="",   type=str, help='System prompt for the model')
        add('-f', '--system-prompt-file',dest='systemPromptFile',default="",   type=str, help='File containing the system prompt')
        add('-o', '--output',            dest='outputFile',      default="",   type=str, help='File to write the output to')
        add('-d', '--dated',             dest='datedOutputFile', nargs='?',    type=bool, help='Add time and date to output filename')
        add('-t', '--temperature',       dest='temperature',     default=0.0,  type=float,choices=(0.0, 2.0),help='Temperature')
        add('-g', '--gpt-model',         dest='model',           default="gpt-4", type=str, help='Model of gpt-4 or gpt-3.5 (ChatGPT) to use ')
        add('-m', '--max-tokens',        dest='max_tokens',      default=250,    type=int, help='Maximal number of tokens to use per query, 0 for inf')
        add('-n', '--n-completions',     dest='number',          default=1,    type=int, help='Number of completions to request')
        add('-k', '--api-key',           dest='apiKey',          default="",   type=str, help='API key for the OpenAI API')

        # args = parser.parse_args()
        # args = parser.parse_args("-h")
        args = parser.parse_args("-s /home/siegel/manuscript/review_prompt.txt -p /home/siegel/manuscript/2.6_neuronale_netze.tex")

        print(args)

        prompt = args.prompt or maybe(args.promptFile)
        systemPrompt = args.systemPrompt or maybe(args.systemPromptFile)



        print(prompt)

if __name__ == "__main__":
    Thought()
