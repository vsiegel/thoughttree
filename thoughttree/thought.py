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
        add('-o', '--out-dir',           dest='outDir',          default="",   type=str, help='Directory for output files')
        add('-l', '--log-dir',           dest='logDir',          default="",   type=str, help='Write log to files in this directory')
        add('-t', '--temperature',       dest='temperature',     default=0.0,  type=float,choices=(0.0, 2.0),help='Temperature')
        add('-m', '--max-tokens',        dest='max_tokens',      default=0,    type=int, help='Maximal number of tokens to use per query, 0 for inf')
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
