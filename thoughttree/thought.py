#!/usr/bin/env python3
import os
import sys
from datetime import datetime

import openai
from configargparse import ArgumentParser

from tools import maybe_file


class Thought:
    def __init__(self):
        parser = ArgumentParser(prog="thought",
            description='Interact with a large language model on the command line')
        add = parser.add_argument
        add('prompt',                    nargs='?',              default="",   type=str, help='Prompt for the model, text to be completed')
        add('-p', '--prompt-file',       dest='promptFile',      default="",   type=str, help='File containing the prompt')
        add('-s', '--system-prompt',     dest='systemPrompt',    default="",   type=str, help='System prompt for the model')
        add('-f', '--system-prompt-file',dest='systemPromptFile',default="",   type=str, help='File containing the system prompt')
        add('-o', '--output',            dest='outputFile',      default="",   type=str, help='File to write the output to')
        add('-d', '--derive-name',       dest='deriveName',      action='store_true',    help='Derive output name from prompt name')
        add('-d', '--suffix',            dest='suffix',          default="-out",   type=str, help='Suffix to add to output name')
        add('-d', '--dated',             dest='datedOutputFile', action='store_true',    help='Add time and date to output name')
        add('-t', '--temperature',       dest='temperature',     default=0.0,  type=float,help='Temperature')
        add('-g', '--gpt-model',         dest='model',           default="gpt-4",type=str, help='Model of gpt-4 or gpt-3.5 (ChatGPT) to use ')
        add('-m', '--max-tokens',        dest='max_tokens',      default=250,    type=int, help='Maximal number of tokens to use per query, 0 for inf')
        add('-n', '--n-completions',     dest='number',          default=1,    type=int, help='Number of completions to request')
        add('-a', '--api-key',           dest='apiKey',          default="",   type=str, help='API key for the OpenAI API')

        args = parser.parse_args()


        openai.api_key = args.apiKey or os.getenv("OPENAI_API_KEY")

        prompt = args.prompt or maybe_file(args.promptFile)
        systemPrompt = args.systemPrompt or maybe_file(args.systemPromptFile)

        try:
            completion = self.complete(prompt, systemPrompt, args.temperature, args.max_tokens, args.model)
        except KeyboardInterrupt:
            sys.exit(1)

        if args.outputFile:
            if args.datedOutputFile:
                filename, ext = os.path.splitext(args.outputFile)
                now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                outputFile = f"{filename}_{now}{ext}"
            else:
                outputFile = args.outputFile


            with open(outputFile, 'w') as f:
                f.write(completion)


    def complete(self, prompt, system="", temperature=0.5, max_tokens=250, model="gpt-4"):
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

        return "".join(texts)


if __name__ == "__main__":
    Thought()
