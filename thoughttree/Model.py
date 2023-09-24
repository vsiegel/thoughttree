import sys
import tkinter as tk
import re
import textwrap
from os.path import exists
from tkinter.messagebox import showerror
from typing import Tuple
from datetime import datetime
from pathlib import Path

import openai

import History
from TextDialog import TextDialog
from TokenCounter import TokenCounter

import os

from tools import log, shorter, log_len


def log_file_size(path):
    log(f'Size: {path} {os.path.getsize(path)} bytes')

DEFAULT_API_KEY_ENV = "OPENAI_API_KEY"
DEFAULT_API_KEY_FILE = "openai-api-key.txt"

class Model():
    MODEL_PATTERN = "gpt"

    def __init__(self, model_name):
        self.name = model_name
        self.counter = TokenCounter(model_name)

        logdir = Path.home()/"logs"/"thoughttree"
        if not logdir.exists():
            logdir.mkdir(parents=True, exist_ok=True)

        logfile_name = f"thoughttree-chat-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{model_name}.log"
        self.chat_log_path = logdir/logfile_name
        self.chat_log = open(self.chat_log_path, "a")

        self.max_tokens = tk.IntVar(value=1500)
        self.temperature = tk.DoubleVar(value=0.5)
        self.is_canceled = False
        self.available_models = None


    def complete(self, history, on_increment, max_tokens=None, temperature=None) -> Tuple[str, str]:
        """:return: Tuple[str, str] - (finish_reason, message)"""
        max_tokens = max_tokens or self.max_tokens.get()
        temperature = temperature or self.temperature.get()
        self.is_canceled = False
        self.counter.go()
        self.counter.observe_prompt(history)
        History.log_history_compact(history)
        try:
            response = openai.ChatCompletion.create(
                model=self.name,
                messages=history,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                request_timeout=5 # undocumented #todo
            )
        except Exception as ex:
            return self.error("", "Error in openai.ChatCompletion.create()", ex)

        last_event = None
        try:
            texts = []
            for event in response :
                if self.is_canceled:
                    return 'canceled', ""
                delta = event['choices'][0]['delta']
                if 'content' in delta :
                    text = delta["content"]
                    on_increment(text)
                    self.counter.observe_completion(text)
                    self.log(text)
                    texts.append(text)
                last_event = event
            full_text = "".join(texts)
            print(f"result: {shorter(full_text, 120)} {log_len(full_text, 120)}")

            print(f"{last_event['model']}")
            if self.is_canceled:
                finish_reason = 'canceled'
            else:
                finish_reason = last_event['choices'][0]['finish_reason']
            self.log(f"\n{last_event['model']}: {finish_reason}\n")
            return finish_reason, ""
        except Exception as ex:
            return self.error(f"{last_event=}", "Error receiving completion response", ex)


    def error(self, message, title, ex):
        message = f"Exception: {ex}\n\n{message}"
        # message = textwrap.fill(message, 200)
        self.log("\n\nerror:\n" + message + '\n')
        TextDialog(message, title)
        return "error", message


    def log(self, text):
        chat_log = self.chat_log
        if chat_log:
            chat_log.write(text)
            # chat_log.write('\n')
            chat_log.flush()


    def cancel(self):
        self.is_canceled = True

    def get_available_models(self):
        try:
            if not self.available_models:
                self.available_models = [m["id"] for m in openai.Model.list()["data"] if re.search(self.MODEL_PATTERN, m["id"])]
        except openai.error.AuthenticationError as ex:
            print(ex, file=sys.stderr)
            return []
        except Exception as ex:
            print("Error: " + str(ex), file=sys.stderr)
            return []
        return self.available_models

    @staticmethod
    def set_api_key(api_key_or_file_or_env=DEFAULT_API_KEY_ENV):
        api_key_or_file_or_env = api_key_or_file_or_env or ""
        if os.getenv(api_key_or_file_or_env):
            openai.api_key = os.getenv(api_key_or_file_or_env)
        elif exists(api_key_or_file_or_env):
            with open(api_key_or_file_or_env) as f:
                openai.api_key = f.read().strip()
        elif not api_key_or_file_or_env or api_key_or_file_or_env == DEFAULT_API_KEY_ENV and exists(DEFAULT_API_KEY_FILE):
            with open(DEFAULT_API_KEY_FILE) as f:
                openai.api_key = f.read().strip()
        else:
            openai.api_key = api_key_or_file_or_env
