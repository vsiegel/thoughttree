import re
import textwrap
from tkinter.messagebox import showerror
from typing import Tuple
from datetime import datetime
from pathlib import Path

import tiktoken
import openai

OPENAI_PRICING_USD_PER_1K_TOKENS = {
    'prompt': {
        'gpt-3.5-turbo': 0.002,
        'gpt-4-32k': 0.06,
        'gpt-4': 0.03,
    },
    'completion': {
        "gpt-3.5-turbo": 0.002,
        'gpt-4-32k': 0.12,
        'gpt-4': 0.06,
    }
}
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
        self.model_name = model_name
        self.used_tokens_in = 0
        self.used_tokens_out = 0

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
        self.observe_tokens_in(history)
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
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
                    self.observe_tokens_out(text)
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


    def count_tokens(self, text):
        enc = tiktoken.encoding_for_model(self.model_name)
        return len(enc.encode(text))


    def observe_tokens_in(self, history):
        for item in history:
            text = item['content']
            self.used_tokens_in += self.count_tokens(text)


    def observe_tokens_out(self, text):
        self.used_tokens_out += self.count_tokens(text)


    def get_tokens_used_in(self):
        return self.used_tokens_in


    def get_tokens_used_out(self):
        return self.used_tokens_out


    def get_tokens_used_total(self):
        return self.used_tokens_in + self.used_tokens_out

    def get_tokens_cost_in(self):
        return (self.used_tokens_in * OPENAI_PRICING_USD_PER_1K_TOKENS['prompt'][self.model_name])/1000.0


    def get_tokens_cost_out(self):
        return (self.used_tokens_out * OPENAI_PRICING_USD_PER_1K_TOKENS['completion'][self.model_name])/1000.0


    def get_tokens_cost_total(self):
        return self.get_tokens_cost_in() + self.get_tokens_cost_out()
