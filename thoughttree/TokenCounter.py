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
    token_count.count_promp(history)
    #
    #
    #
    token_count.count_complete(text)
