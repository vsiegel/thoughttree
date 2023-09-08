#!/usr/bin/env python3
from glob import glob
import os
import re
import sys
from datetime import datetime
from os.path import splitext, join

import openai
from configargparse import ArgumentParser, Namespace

from tools import maybe_file, read_all_stdin_lines, git


# thought -P 2.6_neuronale_netze.tex -S ~/PycharmProjects/GPT-3-interaction/thoughttree/prompts/manuskript_report_prompt.txt

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
        self.max_tokens = 2500
        self.dry_run = False
        self.replace = None
        self.apiKey = ""


default_config_files = ["~/.config/thoughttreerc"]

class Thought:
    def __init__(self):

        def existing_file_arg(path):
            if os.path.isfile(path):
                return path
            else:
                raise FileNotFoundError(path)

        parser = ArgumentParser(prog="thought", add_config_file_help=True, add_env_var_help=True, default_config_files=default_config_files,
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
        add('-e', '--suffix',        dest='suffix',          type=str, default="-out",help='Suffix to add to output name at the end')
        add('-d', '--dated',         dest='datedOutputFile', action='store_true',     help='Add time and date to output name')
        add('-g', '--gpt-model',     dest='model',           type=str,default="gpt-4",help='Model of gpt-4 or gpt-3.5 (ChatGPT) to use')
        add('-t', '--temperature',   dest='temperature',     type=float,default=0.5,  help='Query temperature')
        add('-m', '--max-tokens',    dest='max_tokens',      type=int,  default=1500, help='Maximal number of tokens to use per query, 0 for inf')
        add(      '--dry-run',       dest='dry_run',         action='store_true',     help='Dry run')
        add(      '--placeholder',   dest='placeholder',     type=str,  nargs=1,      help='Placeholder for --replace option.')
        add('-r', '--replace',       dest='replace',         type=str,  nargs='*',    help='Values to replace the placeholder in (system) prompts')
        add('-r2', '--replace2',       dest='replace2',      type=str,  nargs='*',    help='Values to replace the placeholder in (system) prompts')
        add('-r3', '--replace3',       dest='replace3',      type=str,  nargs='*',    help='Values to replace the placeholder in (system) prompts')
        add('-R', '--multi-replace', dest='multiReplace',    type=str,  nargs='*',    help='Additional placeholders and inserted values')
        add('-c', '--change-prompt-file',dest='changesToPromptFile',type=str, nargs='*', help='Apply a change to the prompt file')
        add('-C', '--commit-to-git', dest='commit',          action='store_true',     help='Apply a change to the prompt file')
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
        args.replace2 = None
        args.replace3 = None
        args.placeholder = "[<replace>]"
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

        def out_file_name2(promptFile, systemFile):
            if args.overwrite:
                return promptFile
            file = None
            if args.outputFile:
                file = args.outputFile
            if args.suffix:
                name, ext = splitext(file)
                file = f"{name}{args.suffix}{ext}"
            if args.datedOutputFile:
                name, ext = splitext(file)
                now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                file = f"{name}-{now}{ext}"
            elif args.deriveName and promptFile:
                name, ext = splitext(promptFile)
            return file


        def next_numbered(filename):
            print(f"{(filename)=}")
            print(f"{os.path.exists(filename)=}")
            if not filename or not os.path.exists(filename):
                return filename
            pattern = "(?m)^(.*?)(\d+)(\D*?)$|^(.+)(\..+)$|^(\D+?)$"
            dir, basename = os.path.split(filename)
            m = re.match(pattern, basename)
            prefix, number, ext, nonum_prefix, nonum_ext, noext_prefix = m.groups()
            prefix = prefix or nonum_prefix or noext_prefix
            ext = ext or nonum_ext or ""
            number = number or "00"
            # similar_numbered_files = glob(join(dir, prefix + "*" + ext))
            all_files = glob(join(dir, "*"))
            all_files = [os.path.split(f)[1] for f in all_files]
            similar_pattern = f"(?m)^{'.' * len(prefix)}(\d*){'.' * len(ext)}$"
            files = [f for f in all_files if re.match(similar_pattern, f)]

            # filename = join(dir, filename)
            # raise Exception(f"File '{filename}' already exists")
            # return ""
            len_ext = not ext and 0 or len(ext)
            len_prefix = not prefix and 0 or len(prefix)
            numbers = [f[len_prefix:len(f)-len_ext] for f in files]
            print(f"{prefix=}")
            print(f"{ext=}")
            print(f"{files=}")
            print(f"{numbers=}")
            numbers = [int(0 if s == '' else s) for s in numbers]
            print(f"{numbers=}")
            previous = max(numbers)
            next = f"{previous + 1:02d}"
            new_file_name = f"{prefix}{next}{ext}"
            print(f"{filename=}")
            print(f"{new_file_name=}")
            return new_file_name


        def apply_changes(input_files, change_files):
            for input_file in input_files:
                for change_file in change_files:
                    with open(change_file, 'r') as f:
                        changes_string = f.read()
                        with open(input_file, 'r') as f:
                            input_string = f.read()
                            description_pattern = '(?m)(?:Titel|Title): (.*)\s+(?:Beschreibung|Description): (.*)\s*((?:\w+: .*\n)+)'
                            multiple_changes_pattern = '(?m)Derzeitig: "(.*)"\s+Vorschlag: "(.*)"'
                            output = input_string
                            for m in re.finditer(multiple_changes_pattern, changes_string):
                                derzeitig, vorschlag, attributes = m.groups()
                                output = output.replace(derzeitig, vorschlag, 1)
                            if output == input_string:
                                print(f"Could not apply changes from {change_file} to {input_file}", file=sys.stderr)
                            else:
                                with open(input_file, 'w') as f:
                                    f.write(output)
                                if args.commit:
                                    m = re.search(description_pattern, changes_string)
                                    if m:
                                        title, beschreibung = m.groups()
                                        commitmessage = f'''{title}\n\n{beschreibung}\n\n{attributes}'''
                                        commit_file = f"commitmessage-tmp.txt"
                                        with open(commit_file, "w") as f:
                                            f.write(commitmessage)
                                        print(git('diff', '--word-diff', '--color', input_file))
                                        git('commit', '-F', commit_file, input_file)

                                    else:
                                        print(f"No description found in {change_file}", file=sys.stderr)


        if args.changesToPromptFile:
            apply_changes(args.promptFiles, args.changesToPromptFile)
            sys.exit(0)

        prompts = get_prompts(args)
        systems = get_systems(args)

        try:
            for promptFile, orig_prompt in prompts:
                for systemFile, orig_system in systems:
                    prompt = orig_prompt
                    system = orig_system

                    outputFile = args.outputFile or out_file_name(promptFile, systemFile)
                    replacement_message = ""
                    for replace in [args.replace, args.replace2, args.replace3]:
                        if replace:
                            replacement = replace[0]
                            prompt = prompt.replace(args.placeholder, replacement, 1)
                            system = system.replace(args.placeholder, replacement, 1)
                            outputFile = outputFile.replace(args.placeholder, replacement, 1)
                            replacement_message = replacement_message + (replacement and "\n  with replacement " + replacement or "")
                    outputFile = next_numbered(outputFile)
                    print(f"Complete\n    '{promptFile}'{replacement_message}\n with system prompt\n    '{systemFile}' to\n    '{outputFile or 'stdout'}'")
                    if not args.dry_run:
                        completion = Thought.complete(prompt, system, args.temperature, args.max_tokens, args.model)
                        with open(outputFile, 'w') as f:
                            f.write(completion)
                        if args.commit:
                            apply_changes(args.promptFiles, [outputFile])
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
