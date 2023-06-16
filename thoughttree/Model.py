import re
import textwrap
from tkinter.messagebox import showerror
from typing import Tuple
from datetime import datetime
from pathlib import Path

import openai

import History
from TokenCounter import TokenCounter


class Model:

    logfile_name = f"thoughttree-chat-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log"

    MODEL_PATTERN = "gpt"

    available_models = None
    finish_reasons = {
        "stop": {"symbol": "", "tool_tip": ""},
        "length": {"symbol": "…", "tool_tip": "The completion reached max_tokens tokens. It can be continued."},
        "canceled": {"symbol": "☒", "tool_tip": "The completion was canceled."},
        "error": {"symbol": "⚠", "tool_tip": "An error occurred while processing the completion."},
    }

    def __init__(self, model_name):
        self.name = model_name
        self.counter = TokenCounter(model_name)

        self.logdir = Path.home() / "logs" / "thoughttree"
        self.max_tokens = 1500
        self.temperature = 0.5

        self.is_canceled = False
        if not self.logdir.exists():
            self.logdir.mkdir(parents=True, exist_ok=True)
        self.chat_log = open(self.logdir/self.logfile_name, "w")


    def chat_complete(self, history, output_delta_callback, max_tokens=None, temperature=None) -> Tuple[str, str]:
        """:return: Tuple[str, str] - (finish_reason, message)"""
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
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
                # request_timeout=60, # undocumented
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

            if self.is_canceled :
                finish_reason = 'canceled'
            else :
                finish_reason = last_event['choices'][0]['finish_reason']
            self.log("\n" + finish_reason + ":\n")
            return finish_reason, ""
        except Exception as ex:
            return self.error(f"{last_event=}", "Error receiving completion response", ex)


    def error(self, message, title, ex):
        message = f"Exception: {ex}\n\n{message}"
        message = textwrap.fill(message, 200)
        self.log("\n\nerror:\n" + message + '\n')
        showerror(title, message) #, master=
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
