from tools import shorter, log_length


def print_history_compact(history):
    for message in history:
        text = message['content']
        print(f"{message['role']}: {shorter(text, 60)} {log_length(text, 60)}")
    print()

