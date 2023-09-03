#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from os.path import splitext

import openai
from configargparse import ArgumentParser, Namespace

from tools import maybe_file, read_all_stdin_lines


class Args(Namespace):
    def __init__(self):
        super().__init__()
        self.prompt = ""
        self.promptFiles = []
        self.overwrite = False
        self.system = ""
        self.systemFiles = []
        self.number = 1
        self.outputFile = ""
        self.listFiles = []
        self.deriveName = False
        self.suffix = "-out"
        self.datedOutputFile = False
        self.model = "gpt-4"
        self.temperature = 0.5
        self.max_tokens = 1500
        self.dry_run = False
        self.replace = None
        self.apiKey = ""


placeholder = "[<replace>]"


class Thought:
    def __init__(self):

        def existing_file_arg(path):
            if os.path.isfile(path):
                return path
            else:
                raise FileNotFoundError(path)

        parser = ArgumentParser(prog="thought",
            description='Interact with ChatGPT more than once')
        add = parser.add_argument
        add('-p', '--prompt',        dest='prompt',          type=str,  default="",   help='Prompt for the model, text to be completed')
        add('-P', '--prompt-files',  dest='promptFiles',     type=existing_file_arg,  nargs="+",    help='File(s) containing the prompt')
        add('-s', '--system',        dest='system',          type=str,  default="",   help='System prompt for the model')
        add('-S', '--system-files',  dest='systemFiles',     type=existing_file_arg,  nargs="+",    help='File(s) containing the system prompt')
        add('-o', '--output',        dest='outputFile',      type=str,  default="",   help='File to write the output to')
        add(      '--overwrite-prompt-files',dest='overwrite',action='store_true',    help='Replace the prompt with output')
        add('-n', '--n-completions', dest='number',          type=int,  default=1,    help='Number of repetition of each completion')
        add('-l', '--list-files',    dest='listFiles',       type=str,  nargs='*',    help='A list of files that are used as part of the prompt')
        add('-i', '--derive-name',   dest='deriveName',      action='store_true',     help='Derive output name from input prompt name')
        add('-e', '--suffix',        dest='suffix',          type=str,  default="-out",help='Suffix to add to output name at the end')
        add('-d', '--dated',         dest='datedOutputFile', action='store_true',     help='Add time and date to output name')
        add('-g', '--gpt-model',     dest='model',           type=str,  default="gpt-4",help='Model of gpt-4 or gpt-3.5 (ChatGPT) to use')
        add('-t', '--temperature',   dest='temperature',     type=float,default=0.5,  help='Query temperature')
        add('-m', '--max-tokens',    dest='max_tokens',      type=int,  default=1500, help='Maximal number of tokens to use per query, 0 for inf')
        add(      '--dry-run',       dest='dry_run',         action='store_true',     help='Dry run')
        add(      '--replace',       dest='replace',         type=str,  nargs='*',    help='Values to replace the placeholder "' + placeholder + '" in (system) prompts')
        add('-a', '--api-key',       dest='apiKey',          type=str,  default="",   help='API key for the OpenAI API')

        args = Namespace()
        args.prompt = ""
        args.promptFiles = []
        args.overwrite = False
        args.system = ""
        args.systemFiles = []
        args.number = 1
        args.outputFile = ""
        args.listFiles = []
        args.deriveName = False
        args.suffix = "-out"
        args.datedOutputFile = False
        args.model = "gpt-4"
        args.temperature = 0.5
        args.max_tokens = 1500
        args.dry_run = False
        args.replace = None
        args.apiKey = ""

        args = parser.parse_args(namespace=args)

        openai.api_key = args.apiKey or os.getenv("OPENAI_API_KEY")

        def get_prompts(args):
            if args.prompt:
                return [(None, args.prompt)]
            elif args.promptFiles:
                return [(f, maybe_file(f)) for f in args.promptFiles]
            else:
                return [('-', read_all_stdin_lines())]


        def get_systems(args):
            if args.system:
                return [(None, args.system)]
            elif args.systemFiles:
                return [(f, maybe_file(f)) for f in args.systemFiles]
            else:
                return [(None, "")]


        prompts = get_prompts(args)
        systems = get_systems(args)



        def out_file_name(promptFile, systemFile):
            now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            file_name = None
            if args.outputFile:
                name, ext = splitext(args.outputFile)
                if args.datedOutputFile:
                    infix = f"-{now}"
                else:
                    infix = ""
                file_name = f"{name}{infix}{ext}"
            elif args.deriveName and promptFile:
                name, ext = splitext(promptFile)
                if args.datedOutputFile:
                    infix = f"-{now}"
                else:
                    infix = f"-{args.suffix}"
                file_name = f"{name}{infix}{ext}"
            return file_name


        try:
            for promptFile, prompt in prompts:
                for systemFile, system in systems:
                    # for replacement in args.replace:
                    if args.replace:
                        replacement = args.replace[0]
                    else:
                        replacement = ""
                    modified_prompt = prompt.replace(placeholder, replacement) if replacement else prompt
                    modified_system = system.replace(placeholder, replacement) if replacement else system
                    outputFile = args.outputFile or out_file_name(promptFile, systemFile)
                    replacement_message = replacement and "\n  with replacement " + replacement or ""
                    print(f"Complete\n    '{promptFile}'{replacement_message} with system prompt\n    '{systemFile}' to\n    '{outputFile or 'stdout'}'")
                    if not args.dry_run:
                        completion = Thought.complete(modified_prompt, modified_system, args.temperature, args.max_tokens, args.model)
                        with open(outputFile, 'w') as f:
                            f.write(completion)
        except KeyboardInterrupt:
            print("Cancelled", file=sys.stderr, flush=True)
            sys.exit(130)


    @staticmethod
    def complete(prompt, system="", temperature=0.5, max_tokens=250, model="gpt-4"):
        history = [{'role': 'system', 'content': system}]
        history += [{'role': 'user', 'content': prompt}]

        response = openai.ChatCompletion.create(
            model=model,
            messages=history,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
            request_timeout=30, # undocumented #todo
        )


        texts = []
        for event in response:
            delta = event['choices'][0]['delta']
            if 'content' in delta:
                text = delta["content"]
                print(text, end='', flush=True)
                texts.append(text)

        print("", flush=True)
        return "".join(texts)


if __name__ == "__main__":
    Thought()

'''
f=was-sind-sprachmodelle.tex 
r=was-sind-sprachmodelle-report.tex # use $f 
b="review-$f"
h=$(git log --pretty=format:%h -n 1 $f)

git checkout -B $b $h
# AI proposes changes in the file: was-sind-sprachmodelle.tex 
git commit -m "Proposed changes to $f" $r
# AI creates report file: was-sind-sprachmodelle-report.tex 
git add $r
git commit -m "Report about $f" $r
gvim $f
git commit -m "Separate proposed change according to $r\nApply by cherry picking." $f
'''
