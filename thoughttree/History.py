from tools import shorter, logarithmic_length


# class ExtendedList(list):
#     def __init__(self, initial_data):
#         super().__init__(initial_data)  # call the parent class (list) constructor
#
# my_list = ExtendedList([1, 2, 3, 4, 5])


def log_history_compact(history):
    for message in history:
        text = message['content']
        print(f"{message['role']}: {shorter(text, 60)} {logarithmic_length(text, 60)}")
    print()

def history_from_args(system="", message="") :
    history = [
        {'role': 'system', 'content': system},
        {'role': 'user', 'content': message}
    ]
    return history

