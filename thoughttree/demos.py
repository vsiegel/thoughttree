system = "system"
prompt = "prompt"
start = "start"
demos = {
    "Next Paragraph": {prompt: "Give me a foo!"},

    "Inline completion": {system: "Be overly polite.",
                          prompt: """What is funny about mice? The way they can startle people.
What is funny about eels? 
What is funny about bears? Their seemingly clumsy yet surprisingly agile movements.
""", start: "2.26"}
}
