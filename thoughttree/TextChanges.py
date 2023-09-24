import re

from TextChange import TextChange


class TextChanges():
    def __init__(self, multiple_change_spec):
        self.text_changes = []
        self.parse(multiple_change_spec)

    @staticmethod
    def parse(change_spec) -> [TextChange]:
        textChanges = []
        change_matches = re.findall(TextChange.multi_change_pattern_with_attributes, change_spec)
        if not change_matches:
            print(f'No match for "{TextChange.multi_change_pattern_with_attributes}"'[:120])
            return

        for m in change_matches:
            textChanges.append(TextChange(m.group(0)))
