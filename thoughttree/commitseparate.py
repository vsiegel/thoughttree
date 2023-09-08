#!/usr/bin/env python3
import re
import sys
from os.path import basename

from tools import git

# section as numbered in prompt:
# Zusammenfassung is section 0
sections = ["Zusammenfassung", "Fehler", "Unstimmigkeiten.", "Argumentationslücken", "Unklarheiten", "Redundanzen", "Rechtschreibung", "Andere Problene", "Stil und Struktur", "Fehlende Informationen", "Fachsprache und Jargon", "Sonstige Empfehlungen"]

def apply_changes(input_file, change_file, id_suffix):
    # up_to_two_quotes_pattern = "(?m)^(\d+\.\d+)\s*(.*"(.*)".*"(.*)".*)$|^(\d+\.\d+)\s*(.*"(.*)".*)$|^(\d+\.\d+)\s*(.*)$"
    pattern = """(?m)^(\d\d?\.\d\d?\.?)(.*)\n*Beschreibung: (.*)\n+(?:Bisher|Derzeitig): .*"(.*)".*\n+Vorschlag: .*"(.*)"([\s\S]*?)(?=(\d\d?\.\d\d?\.?)|\Z)"""
    input_string = open(input_file).read()
    changes_string = open(change_file).read()

    end_of_previous_match = 0
    for m in re.finditer(pattern, changes_string):
        id, title, beschreibung, derzeitig, vorschlag, suffix, lookahead = m.groups()
        top_section = int(id.split(".")[0])
        id = id + id_suffix
        title = title.strip()
        title = re.sub("^\s*\[.*?\]\s*", "", title)
        title = f"{sections[top_section]}{title and ': ' or ''}{title}"
        print(f"{id=}")
        print(f"{title=}")
        print(f"{beschreibung=}")
        print(f"{derzeitig=}")
        print(f"{vorschlag[:70]=}")
        found = input_string.find(derzeitig)
        print(f"Found: {found} {found == -1 and '-----------' or ''}")
        if m.start(0) > end_of_previous_match:
            print(f"{m.start(0)=} {end_of_previous_match=}")
            print(f'Warning: Unmatched text: {m.start(0) - end_of_previous_match} characters: \n######\n{changes_string[end_of_previous_match:m.start(0)]}\n######')
        end_of_previous_match = m.end(0)

        if found > -1:
            commitmessage = f'''{id} {title}\n\n{beschreibung}\n'''
            commit_file = f"commitmessage-tmp.txt"
            with open(commit_file, "w") as f:
                f.write(commitmessage)
            git('checkout', 'main')
            git('checkout', '--', input_file)
            hash = git("log", "--pretty=format:%h", "-n", "1", input_file)
            branch = f"proposal-{input_file}-{id}".rstrip('.')
            try:
                git("checkout", "-b", branch, hash)
                output = input_string.replace(derzeitig, vorschlag, 1)
                with open(input_file, "w") as f:
                    f.write(output)

                input("[Enter to commit]")
                git('commit', '-F', commit_file, input_file)
                git('checkout', 'main')
            except Exception:
                input("[Enter to continue after error]")
        print()


# input_string = input_string[:1000]
# changes_string = changes_string[:4000]



def commit_to_branches(input_file, change_files):

    for change_file in change_files:
        m = re.match(".*\d([a-z])[\w-]*\.txt", change_file)
        print(change_file)
        id_suffix = m and m.group(1) or ""

        print(id_suffix)

        apply_changes(input_file, change_file, id_suffix)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(f"{basename(sys.argv[0])} <input_file> <change_files> ...")
        sys.exit(1)

    input_file = sys.argv[1]
    change_files = sys.argv[2:]

    commit_to_branches(input_file, change_files)

