import re

# Zusammenfassung is section 0
sections = ["Zusammenfassung", "Fehler", "Unstimmigkeiten.", "Argumentationslücken", "Unklarheiten", "Redundanzen", "Rechtschreibung", "Andere Problene", "Stil und Struktur", "Fehlende Informationen", "Fachsprache und Jargon", "Sonstige Empfehlungen"]

def replace_group(pattern, input, changes_string):

    m = re.findall(pattern, changes_string)
    # print(f"{m=}")
    # print(f"{m.groups()=}")

    for id, title, beschreibung, bisher, vorschlag, suffix in m:
        print()
        print(f"{id=}")
        print(f"{title=}")
        # print(f"{beschreibung=}")
        print(f"{bisher=}")
        # print(f"{vorschlag=}")

        found = input.find(bisher)
        print(f"{ found=}")
        if found > -1:
            output = input.replace(bisher, vorschlag, 1)
            open(f"2.6_neuronale_netze-cange-{id}.tex", "w").write(output)
            open(f"2.6_neuronale_netze-cange-{id}-revert.tex", "w").write(input)


input_string = open("/home/siegel/ttt/manuscript/2.6_neuronale_netze.tex").read()
changes_string = open("/home/siegel/ttt/manuscript/2.6_neuronale_netze_manuscript_changes_one_section-all.txt").read()

# input_string = input_string[:1000]
# changes_string = changes_string[:4000]

changeSectionPattern = """(?sm)^(\d+\.\d+)\.?\s*(.*?)\s*Beschreibung: (.*?)(Bisher|Derzeitig): "(.*?)".*?Vorschlag: "(.*?)"(.*?)$"""

replace_group(changeSectionPattern, input_string, changes_string)

