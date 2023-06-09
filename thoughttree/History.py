from tools import shorter, logarithmic_length


def log_history_compact(history):
    for message in history:
        text = message['content']
        print(f"{message['role']}: {shorter(text, 60)} {logarithmic_length(text, 60)}")
    print()

