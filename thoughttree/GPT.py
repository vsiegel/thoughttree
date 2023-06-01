import re
import textwrap
from tkinter.messagebox import showerror
from typing import Tuple
from datetime import datetime
from pathlib import Path

import openai
import tiktoken


class GPT:
    logdir = Path.home()/"logs"/"thoughttree"
    logfile_name = f"thoughttree-chat-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log"
    max_tokens = 1500
    temperature = 0.5

    # model = 'gpt-4'
    _model = 'gpt-3.5-turbo'
    # internal_generation_model = 'gpt-3.5-turbo'
    # internal_generation_model = 'gpt-4'
    internal_generation_model = ''

    is_canceled = False

    MODEL_PATTERN = "gpt"

    available_models = None
    tokenizer = None
    finish_reasons = {
        "stop": {"symbol": "", "tool_tip": ""},
        "length": {"symbol": "…", "tool_tip": "The completion reached max_tokens tokens. It can be continued."},
        "canceled": {"symbol": "☒", "tool_tip": "The completion was canceled."},
        "error": {"symbol": "⚠", "tool_tip": "An error occurred while processing the completion."},
    }


    def __init__(self):
        if not GPT.logdir.exists():
            GPT.logdir.mkdir(parents=True, exist_ok=True)
        self.chat_log = open(GPT.logdir/self.logfile_name, "w")
        self.used_tokens_in = {}
        self.used_tokens_out = {}

    def chat_complete(self, history, output_delta_callback, max_tokens=None, temperature=None, model=None) -> Tuple[str, str]:
        """:return: Tuple[str, str] - (finish_reason, message)"""
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        model = model or self.model
        self.is_canceled = False
        self.count_tokens_in(history, self._model)
        try:
            response = openai.ChatCompletion.create(
                model=self._model,
                messages=history,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                # request_timeout=60, # undocumented
            )
        except Exception as e:
            return self.error("", "Error in openai.ChatCompletion.create()", e)

        last_event = None
        try:
            for event in response :
                if self.is_canceled:
                    return 'canceled', ""
                delta = event['choices'][0]['delta']
                if 'content' in delta :
                    text = delta["content"]
                    self.log(text)
                    self.count_tokens_out(text, self._model)
                    output_delta_callback(text)
                last_event = event

            if self.is_canceled :
                finish_reason = 'canceled'
            else :
                finish_reason = last_event['choices'][0]['finish_reason']
            self.log("\n" + finish_reason + ":\n")
            return finish_reason, ""
        except Exception as e:
            return self.error(f"{last_event=}", "Error receiving completion response", e)


    def error(self, message, title, e):
        message = f"Exception: {e}\n\n{message}"
        message = textwrap.fill(message, 200)
        self.log("\n\nerror:\n" + message + '\n')
        showerror(title, message)
        return "error", message


    def log(self, text):
        chat_log = self.chat_log
        if chat_log:
            chat_log.write(text)
            # chat_log.write('\n')
            chat_log.flush()


    @staticmethod
    def print_history(history):
        for item in history:
            print(item)
        print()

    def count_tokens(self, text):
        enc = tiktoken.encoding_for_model(self.model)
        num_tokens = len(enc.encode(text))
        return num_tokens

    def count_tokens_in(self, history, model):
        used = self.used_tokens_in
        if not model in used:
            used[model] = 0
        for item in history:
            used[model] += self.count_tokens(item['content'])

    def count_tokens_out(self, text, model):
        self.used_tokens_in[model] += self.count_tokens(text)

    def cancel(self, event=None):
        self.is_canceled = True

    def get_available_models(self):
        if not self.available_models:
            self.available_models = [m["id"] for m in openai.Model.list()["data"] if re.search(self.MODEL_PATTERN, m["id"])]
        return self.available_models

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, model):
        self._model = model

