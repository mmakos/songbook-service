import json

authors = []

with open('authors.txt', encoding='utf-8') as file:
    for i, line in enumerate(file.readlines()):
        line = line.strip()
        line = line.split(" ")
        author = {}

        if line[-1].startswith("(") and line[-1].endswith(")"):
            author["nickname"] = line[-1][1:-1]
            line.pop()

        if line[0] == "Siostra":
            author["title"] = "sister"
            line.pop(0)

        author["name"] = line[0]
        author["lastName"] = line[-1]

        if len(line) == 3:
            author["secondName"] = line[1]

        author["id"] = i + 100

        authors.append(author)

with open('authors.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(authors, indent=2, ensure_ascii=False))
