import sys

from configargparse import Namespace, ArgumentParser

conf = Namespace()

conf.show_finish_reason = True


def main(argv):
    parser = ArgumentParser(prog="thoughttree",
        description='Interact with a large language model in alternative ways',
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
    add('-z', '--add-temperature-0', dest='addTemp0Sample',  default=False,type=bool,help='Add additional completion')
    add('-g', '--generate-titles',   dest='generateTitles',  default=False,type=bool,help='Generate titles')
    add('-b', '--blinking-caret',    dest='blinkingCaret',   default=True, type=bool,help='Should the text input caret blink')
    add('-a', '--autoscroll',        dest='autoscroll',      default=True, type=bool,help='Should the output scroll during completion')
    add('-r', '--ring-on-completion',dest='ringOnCompletion',default=False,type=bool,help='Ring bell on completion long')
    add('-d', '--display-reason',    dest='displayReason',   default=True, type=bool,help='Display finish reason as icon')
    add('-k', '--api-key',           dest='apiKey',          default="",   type=str, help='API key for the OpenAI API')

    args = parser.parse_args("-h")

    print(args)

if __name__ == "__main__":
    main(sys.argv)
