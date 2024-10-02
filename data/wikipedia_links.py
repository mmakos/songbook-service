import json
import webbrowser

with open('data/authors.json', encoding="utf-8") as file:
    authors = json.load(file)

    for author in authors:
        if author.get('url') and "?search" in author.get('url'):
            webbrowser.open(f"https://www.google.com/search?&q={author['name']}+{author['lastName']}")
