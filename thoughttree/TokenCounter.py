import tiktoken


# Sources:
# https://platform.openai.com/docs/models/gpt-4
# https://platform.openai.com/docs/models/gpt-3-5
# https://openai.com/pricing
# as of 2023-06-09

MODEL_DATA = {
    'gpt-3.5-turbo': {
        '1k_token_usd': {
            'prompt': 0.002,
            'completion': 0.002,
        },
        'max_tokens': 4096,
    },
    'gpt-4': {
        '1k_token_usd': {
            'prompt': 0.03,
            'completion': 0.06,
        },
        'max_tokens': 8192,
    },
    'gpt-4-32k': {
        '1k_token_usd': {
            'prompt': 0.06,
            'completion': 0.12,
        },
        'max_tokens': 32768,
    },
}


class TokenCounter:
    def __init__(self, model_name, parent=None):
        if parent:
            self.prompt___tokens_sum = parent.prompt___tokens_sum
            self.complete_tokens_sum = parent.complete_tokens_sum
        else:
            self.prompt___tokens_sum = 0
            self.complete_tokens_sum = 0

        def start(self):
            self.span_start = TokenCounter(self)

        def since_start(self):
            pass



if __name__ == "__main__":
    token_count = TokenCounter("a model")
    #
    #
    #
    token_count.start()
    #
    #
    token_count.count_prompt(history)
    #
    #
    #
    token_count.count_complete(text)
