import re

import tiktoken

from MODEL_DATA import MODEL_DATA


class TokenCounter:
    def __init__(self, model_name):
        self.model_name = model_name

        self.prompt_tokens_total = 0
        self.prompt_tokens_at_go = 0
        self.completion_tokens_total = 0
        self.completion_tokens_at_go = 0

    def go(self):
        self.prompt_tokens_at_go = self.prompt_tokens_total
        self.completion_tokens_at_go = self.completion_tokens_total


    def prompt_tokens_since_go(self):
        return self.prompt_tokens_total - self.prompt_tokens_at_go

    def completion_tokens_since_go(self):
        return self.completion_tokens_total - self.completion_tokens_at_go

    def tokens_since_go(self):
        return self.prompt_tokens_since_go() + self.completion_tokens_since_go()

    def tokens_total(self):
        return self.prompt_tokens_total + self.completion_tokens_total

    def prompt_cost_since_go(self):
        return self.prompt_cost(self.prompt_tokens_since_go())

    def completion_cost_since_go(self):
        return self.completion_cost(self.completion_tokens_since_go())

    def prompt_cost_total(self):
        return self.prompt_cost(self.prompt_tokens_total)

    def completion_cost_total(self):
        return self.completion_cost(self.completion_tokens_total)

    def cost_since_go(self):
        return self.prompt_cost_since_go() + self.completion_cost_since_go()

    def cost_total(self):
        return self.prompt_cost(self.prompt_tokens_total) + self.completion_cost(self.completion_tokens_total)


    def count_tokens(self, text):
        enc = tiktoken.encoding_for_model(self.model_name)
        return len(enc.encode(text))

    def observe_prompt(self, history):
        for item in history:
            text = item['content']
            self.prompt_tokens_total += self.count_tokens(text)

    def observe_completion(self, text):
        self.completion_tokens_total += self.count_tokens(text)

    def token_cost(self, tokens, direction):
        model_name = self.model_name
        if model_name not in MODEL_DATA:
            match = re.match(r"^(.*)(-[0-9]{4}$)", self.model_name)
            if match:
                model_name = match.group(1)
        if model_name not in MODEL_DATA:
            return -1
        else:
            return (tokens * MODEL_DATA[model_name]['1k_token_usd'][direction]) / 1000.0

    def prompt_cost(self, tokens):
        return self.token_cost(tokens, 'prompt')

    def completion_cost(self, tokens):
        return self.token_cost(tokens, 'completion')

    def summary_since_go(self):
        return f"{self.model_name} query:   {self.prompt_tokens_since_go():6d}+{self.completion_tokens_since_go():6d}={self.tokens_since_go():6d}t "\
               + f"{self.prompt_cost_since_go():.3f}+{self.completion_cost_since_go():.3f}={self.cost_since_go():.3f}$"

    def summary_total(self):
        return f"{self.model_name} session: {self.prompt_tokens_total:6d}+{self.completion_tokens_total:6d}={self.tokens_total():6d}t "\
               + f"{self.prompt_cost_total():.3f}+{self.completion_cost_total():.3f}={self.cost_total():.3f}$"

    def summary(self):
        return self.summary_since_go() + "\n" + self.summary_total()

    def summarize(self):
        print(self.summary())
