# Sources:
# https://platform.openai.com/docs/models/gpt-4
# https://platform.openai.com/docs/models/gpt-3-5
# https://openai.com/pricing
# as of 2023-06-09

MODEL_DATA = {
    'gpt-3.5-turbo': {
        '1k_token_usd': {
            'prompt': 0.0015,
            'completion': 0.002,
        },
        'max_tokens': 4096,
    },
    'gpt-3.5-turbo-16k': {
        '1k_token_usd': {
            'prompt': 0.003,
            'completion': 0.004,
        },
        'max_tokens': 16384,
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
