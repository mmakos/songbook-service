import json

authors = []

with open('authors.txt', encoding='utf-8') as file:
    for i, line in enumerate(file.readlines()):
        line = line.strip()
        author = {}
        if line.endswith(")"):
            nick_idx = line.index("(")
            author["nickname"] = line[nick_idx + 1:-1]
            line = line[:nick_idx]

        line = line.strip().split(" ")

        if line[0] == "Siostra":
            author["title"] = "siostra"
            line.pop(0)
        elif line[0] == "x.":
            author["title"] = "ksiądz"
            line.pop(0)
        elif line[0] == "ppłk.":
            author["title"] = "podpułkownik"
            line.pop(0)
        elif line[0] == "kpt.":
            author["title"] = "kapitan"
            line.pop(0)
        elif line[0] == "św.":
            author["title"] = "święty"
            line.pop(0)

        author["name"] = line[0]
        author["lastName"] = line[-1]

        if len(line) == 3:
            author["secondName"] = line[1]

        author["id"] = i + 100

        authors.append(author)

with open('authors.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(authors, indent=2, ensure_ascii=False))
