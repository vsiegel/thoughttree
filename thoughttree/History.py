from tools import shorter, log_len


# class History(list):
#     __init__ = list.__init__
#     def __repr__(self):
#         return f"l(l-r: {super().__repr__()})"
#     def __str__(self):
#         return f"l(l-s: {super().__str__()})"


def log_history_compact(history):
    for message in history:
        text = message['content']
        print(f"{message['role']}: \"{shorter(text, 120)}\" {log_len(text, 120)}")
    print()

def history_from_args(system="", message="") :
    history = [
        {'role': 'system', 'content': system},
        {'role': 'user', 'content': message}
    ]
    return history

