import re

# Zusammenfassung is section 0
sections = ["Zusammenfassung", "Fehler", "Unstimmigkeiten.", "Argumentationslücken", "Unklarheiten", "Redundanzen", "Rechtschreibung", "Andere Problene", "Stil und Struktur", "Fehlende Informationen", "Fachsprache und Jargon", "Sonstige Empfehlungen"]

def replace_group(pattern, input, changes_string):

    end_of_previous_match = 0
    for m in re.finditer(pattern, changes_string):
        id, title, beschreibung, derzeitig, vorschlag, suffix, lookahead = m.groups()
        top_section = int(id.split(".")[0])
        title = title.strip()
        title = re.sub("^\s*\[.*?\]\s*", "", title)
        title = f"{sections[top_section]}{title and ': ' or ''}{title}"
        print(f"{id=}")
        print(f"{title=}")
        print(f"{beschreibung=}")
        print(f"{derzeitig=}")
        print(f"{vorschlag[:70]=}")
        found = input.find(derzeitig)
        print(f"Found: {found} {found == -1 and '-----------' or ''}")
        print()

        if m.start(0) > end_of_previous_match:
            print(f'Warning: Unmatched text: {m.start(0) - end_of_previous_match} characters: "{changes_string[end_of_previous_match:m.start(0)]}"')

        # if found > -1:
        #     output = input.replace(derzeitig, vorschlag, 1)
        #     open(f"2.6_neuronale_netze-cange-{id}.tex", "w").write(output)
        end_of_previous_match = m.end(0)

input_string = open("/home/siegel/ttt/manuscript/2.6_neuronale_netze.tex").read()
changes_string = open("/home/siegel/ttt/manuscript/2.6_neuronale_netze_manuscript_changes_one_section-all.txt").read()

# input_string = input_string[:1000]
# changes_string = changes_string[:4000]

changeSectionPattern = """(?sm)^(\d+\.\d+)\.?\s*(.*?)\s*Beschreibung: (.*?)(Bisher|Derzeitig): "(.*?)".*?Vorschlag: "(.*?)"(.*?)$"""

replace_group(changeSectionPattern, input_string, changes_string)

