import re
from tkinter.messagebox import showerror
from typing import Tuple
from datetime import datetime

import openai
import tiktoken


class GPT:
    logfile_name = f"thoughttree-chat-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log"
    max_tokens = 1500
    temperature = 0.5
    model = 'gpt-3.5-turbo'
    # model = 'gpt-4'
    MODEL_PATTERN = "gpt"
    available_models = None
    tokenizer = None
    finish_reasons = {
        "stop": {"symbol": "", "tool_tip": ""},
        "length": {"symbol": "…", "tool_tip": "The completion reached max_tokens tokens. It can be continued."},
        "canceled": {"symbol": "☒", "tool_tip": "The completion was canceled."},
        "error": {"symbol": "⚠", "tool_tip": "An error occurred while processing the completion."},
    }


    is_canceled = False

    def __init__(self):
        self.chat_log = open(self.logfile_name, "w")

    def chat_complete(self, history, output_delta_callback, max_tokens=None, temperature=None) -> Tuple[str, str]:
        """:return: Tuple[str, str] - (finish_reason, message)"""
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        self.is_canceled = False
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=history,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
        except Exception as e:
            message = f"Exception: {e}"
            showerror("Error in openai.ChatCompletion.create()", message)
            return 'error', message

        last_event = None
        try:
            for event in response :
                if self.is_canceled:
                    return 'canceled', ""
                delta = event['choices'][0]['delta']
                if 'content' in delta :
                    text = delta["content"]
                    if self.chat_log:
                        self.chat_log.write(text)
                        self.chat_log.flush()
                    output_delta_callback(text)
                last_event = event

            if self.is_canceled :
                return 'canceled', ""
            else :
                return last_event['choices'][0]['finish_reason'], ""
        except Exception as e:
            message = f"Exception: {e}\n\n{last_event=}"
            showerror("Error receiving completion response", message)
            return 'error', message

    def count_tokens(self, text):
        enc = tiktoken.encoding_for_model(self.model)
        num_tokens = len(enc.encode(text))
        return num_tokens

    def cancel(self, event=None):
        self.is_canceled = True

    def get_available_models(self):
        if not self.available_models:
            self.available_models = [m["id"] for m in openai.Model.list()["data"] if re.search(self.MODEL_PATTERN, m["id"])]
        return self.available_models

    def set_model(self, model):
        self.model = model
