#!/usr/bin/env python3
from glob import glob
import os
import re
import sys
from datetime import datetime
from os.path import splitext, join, dirname, exists
from os import listdir

import openai
import tiktoken
from configargparse import ArgumentParser, Namespace

from Model import Model
from tools import maybe_file, read_all_stdin_lines, git


# thought -P 2.6_neuronale_netze.tex -S ~/PycharmProjects/GPT-3-interaction/thoughttree/prompts/manuskript_report_prompt.txt

default_config_files = ["~/.config/thoughtrc"]



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
        add('-d', '--document',      dest='document',        type=str,  default="",   help='File that can be part of in- and output, e.g. it may be edited')
        add('-R', '--row',           dest='number',          type=int,  default=0,    help='Row in document')
        add('-C', '--column',        dest='number',          type=int,  default=0,    help='Column in document')
        add('-O', '--offset',        dest='offset',          type=int,  default=0,    help='Offset in document')
        add('-n', '--n-completions', dest='number',          type=int,  default=1,    help='Number of repetition of each completion')
        add('-l', '--list-files',    dest='listFiles',       type=str,  nargs='*',    help='A list of files that are used as part of the prompt')
        add('-N', '--derive-name',   dest='deriveName',      action='store_true',     help='Derive output name from input prompt name')
        add('-e', '--suffix',        dest='suffix',          type=str, default="-out",help='Suffix to add to output name at the end')
        add('-D', '--dated',         dest='datedOutputFile', action='store_true',     help='Add time and date to output name')
        add('-g', '--gpt-model',     dest='model',           type=str,default="gpt-4",help='Model of gpt-4 or gpt-3.5 (ChatGPT) to use')
        add('-t', '--temperature',   dest='temperature',     type=float,default=0.5,  help='Query temperature')
        add('-m', '--max-tokens',    dest='max_tokens',      type=int,  default=1500, help='Maximal number of tokens to use per query, 0 for inf')
        add(      '--dry-run',       dest='dry_run',         action='store_true',     help='Dry run')
        add(      '--placeholder',   dest='placeholder',     type=str,  nargs=1,      help='Placeholder for --replace option.')
        add('-r', '--replace',       dest='replace',         type=str,  nargs='*',    help='Values to replace the placeholder in (system) prompts')
        add('-r2', '--replace2',     dest='replace2',        type=str,  nargs='*',    help='Values to replace the placeholder in (system) prompts')
        add('-r3', '--replace3',     dest='replace3',        type=str,  nargs='*',    help='Values to replace the placeholder in (system) prompts')
        add('-M', '--multi-replace', dest='multiReplace',    type=str,  nargs='*',    help='Additional placeholders and inserted values')
        add('-c', '--change-prompt-file',dest='changePromptFile',type=str, nargs='*', help='Apply a change to the prompt file')
        add(      '--code-complete', dest='codeComplete',    action='store_true',     help='Code completion')
        add('-G', '--commit-to-git', dest='commit',          action='store_true',     help='Commit change to git')
        add('-a', '--api-key',       dest='apiKey',          type=str,  default="",   help='API key for the OpenAI API, or a file containing it.')
        add('-v', '--verbose',       dest='verbose',         action='store_true',     help='Show some information')
        add('-L'  '--prompt-lib',    dest='promptLib',       type=str,  default="",   help='Directory containing a library of standard prompts')
        add(      '--count-token',   dest='countTokens',     type=str,  nargs='*',    help='Count th number of tokens in files.')

        args = Namespace()
        args.prompt = ""
        args.promptFiles = []
        args.overwrite = False
        args.system = ""
        args.systemFiles = []
        args.document = ""
        args.codeComplete = False
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
        args.multiReplace = None
        args.changePromptFile = None
        args.placeholder = "[<replace>]"
        args.apiKey = "OPENAI_API_KEY"
        args.insertion_marker = "§"
        args.prompt_dir = join(dirname(__file__), "prompts")

        args = parser.parse_args(namespace=args)

        Model.set_api_key(args.apiKey)

        def get_prompts(args):
            if args.prompt:
                return [(None, args.prompt)]
            elif args.promptFiles:
                return [(f, maybe_file(f)) for f in args.promptFiles]
            elif not sys.stdin.isatty():
                return [('-', read_all_stdin_lines())]
            else:
                return [(None, "")]


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
            if not filename or not os.path.exists(filename):
                return filename
            pattern = "(?m)^(.*?)(\d+)(\D*?)$|^(.+)(\..+)$|^(\D+?)$"
            dir, basename = os.path.split(filename)
            m = re.match(pattern, basename)
            prefix, number, ext, nonum_prefix, nonum_ext, noext_prefix = m.groups()
            prefix = prefix or nonum_prefix or noext_prefix
            ext = ext or nonum_ext or ""
            number = number or "00"
            all_files = glob(join(dir, "*"))
            all_files = [os.path.split(f)[1] for f in all_files]
            similar_pattern = f"(?m)^{'.' * len(prefix)}(\d*){'.' * len(ext)}$"
            files = [f for f in all_files if re.match(similar_pattern, f)]

            len_ext = not ext and 0 or len(ext)
            len_prefix = not prefix and 0 or len(prefix)
            numbers = [f[len_prefix:len(f)-len_ext] for f in files]
            numbers = [int(0 if s == '' else s) for s in numbers]
            previous = max(numbers)
            next = f"{previous + 1:02d}"
            new_file_name = f"{prefix}{next}{ext}"
            return new_file_name


        def apply_changes(input_files, change_files):
            for input_file in input_files:
                for change_file in change_files:
                    with open(change_file, 'r') as f:
                        changes_string = f.read()
                        with open(input_file, 'r') as f:
                            input_string = f.read()
                            # description_pattern_with_attributes = '(?m)(?:Titel|Title): (.*)\s+(?:Beschreibung|Description): (.*)\s*((?:\w+: .*\n)+)'
                            # description_pattern = '(?m)(?:Titel|Title): (.*)\s+(?:Beschreibung|Description): (.*)'
                            # multiple_changes_pattern = '(?m)(?:Derzeitig|Old|Alt): "(.*)"\s+(?:Vorschlag|New|Neu): "(.*)"'
                            # single_change_pattern = '(?m)(?:Titel|Title): (.*)\s+(?:Beschreibung|Description): (.*)\s+(?:Derzeitig|Old|Alt): (".*"|"""[\s\S]*?""")\s+(?:Vorschlag|New|Neu): ("""[\s\S]*?"""|".*")'
                            single_change_pattern_with_attributes = '(?m)(?:Titel|Title): (.*)\n+(?:Beschreibung|Description): (.*)\s+((?:\n\w+: .*)*)\n+(?:Derzeitig|Old|Alt): (".*"|"""[\s\S]*?""")\n+(?:Vorschlag|New|Neu): ("""[\s\S]*?"""|".*")'
                            single_change_pattern_with_attributes = '(?m)(?:Titel|Title): (.*)\n+(?:Beschreibung|Description): (.*)\s+((?:\n\w+: .*)*)\n+(?:Derzeitig|Old|Alt): (".*"|"""[\s\S]*?""")\n+(?:Vorschlag|New|Neu): ("""[\s\S]*?"""|".*")'
                            single_change_pattern_with_attributes = '(?m)(?:Titel|Title): (.*)\n+(?:Beschreibung|Description): (.*)\s+((?:\n+\w+: .*)*?)\n+(?:Derzeitig|Old|Alt): (".*"|"""[\s\S]*?""")\n+(?:Vorschlag|New|Neu): ("""[\s\S]*?"""|".*")'
                            output = input_string
                            for m in re.findall(single_change_pattern_with_attributes, changes_string):
                                # derzeitig, vorschlag = m.groups()
                                title, description, attributes, old, new = m
                                old = old.strip("'"+'"')
                                new = new.strip("'"+'"')
                                output = output.replace(old, new, 1)
                            if output == input_string:
                                print(f"Could not apply changes from {change_file} to {input_file}", file=sys.stderr)
                            else:
                                with open(input_file, 'w') as f:
                                    f.write(output)
                                if args.commit:
                                    # m = re.search(description_pattern, changes_string)
                                    # if m:
                                    #     title, description = m.groups()
                                    commitmessage = f'''{title}\n\n{description}'''
                                    commit_file = f"commitmessage-tmp.txt"
                                    with open(commit_file, "w") as f:
                                        f.write(commitmessage)
                                    print(git('diff', '--word-diff', '--color', input_file))
                                    git('commit', '-F', commit_file, input_file)

                                    # else:
                                    #     print(f"No description found in {change_file}", file=sys.stderr)


        def insert_insertion_mark(document, row, column, insertion_marker):
            lines = document.splitlines(True)
            lines[row] = lines[row][:column] + insertion_marker + lines[row][column:]
            return "\n".join(lines)

        def complete_code(document, row, column):
            text = insert_insertion_mark(document, row, column, args.insertion_marker)
            #todo


        def count_tokens():
            # enc = tiktoken.encoding_for_model(self.model_name)
            with sys.stdin as f:
                text = f.read()
            enc = tiktoken.get_encoding('cl100k_base')
            return len(enc.encode(text))


        if args.changePromptFile:
            apply_changes(args.promptFiles, args.changePromptFile)
            sys.exit(0)
        elif args.codeComplete:
            complete_code(args.document, args.row, args.column)
            sys.exit(0)
        elif args.countTokens:
            count_tokens()
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
                    if args.verbose:
                        print(f"Complete\n    '{promptFile}'{replacement_message}\n with system prompt\n    '{systemFile}' to\n    '{outputFile or 'stdout'}'")
                    if not args.dry_run:
                        completion = Thought.complete(prompt, system, args.temperature, args.max_tokens, args.model)
                        if outputFile:
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
