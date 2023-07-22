import tkinter as tk
import re
import textwrap
from tkinter.messagebox import showerror
from typing import Tuple
from datetime import datetime
from pathlib import Path

import openai

import History
from TokenCounter import TokenCounter

import os

from tools import log


def log_file_size(path):
    log(f'Size: {path} {os.path.getsize(path)} bytes')


class Model:

    logfile_name = f"thoughttree-chat-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log"

    MODEL_PATTERN = "gpt"

    available_models = None
    finish_reasons = {
        "stop": {"symbol": "", "tooltip": ""},
        "length": {"symbol": "…", "tooltip": "The completion reached max_tokens tokens. It can be continued."},
        "canceled": {"symbol": "☒", "tooltip": "The completion was canceled."},
        "error": {"symbol": "⚠", "tooltip": "An error occurred while processing the completion."},
    }

    def __init__(self, model_name):
        self.name = model_name
        self.counter = TokenCounter(model_name)

        logdir = Path.home()/"logs"/"thoughttree"
        if not logdir.exists():
            logdir.mkdir(parents=True, exist_ok=True)
        self.chat_log_path = logdir/self.logfile_name
        self.chat_log = open(self.chat_log_path, "a")

        self.max_tokens = tk.IntVar(value=1500)
        self.temperature = tk.DoubleVar(value=0.5)
        self.is_canceled = False


    def chat_complete(self, history, output_delta_callback, max_tokens=None, temperature=None) -> Tuple[str, str]:
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
                request_timeout=30, # undocumented #todo
            )
        except Exception as ex:
            return self.error("", "Error in openai.ChatCompletion.create()", ex)

        last_event = None
        try:
            for event in response :
                if self.is_canceled:
                    return 'canceled', ""
                delta = event['choices'][0]['delta']
                if 'content' in delta :
                    text = delta["content"]
                    self.log(text)
                    self.counter.observe_completion(text)
                    output_delta_callback(text)
                last_event = event

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
        message = textwrap.fill(message, 200)
        self.log("\n\nerror:\n" + message + '\n')
        showerror(title, message) #, master= #todo
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
        except openai.error.AuthenticationError:
            return []
        except Exception:
            return []
        return self.available_models
