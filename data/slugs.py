import json

from Songbook.str_convert import title_to_unique_name

with open('authors.json', encoding='utf-8') as file:
    authors: dict = json.load(file)

author_slugs = set()
for author in authors:
    slug: str
    nick = author.get("nickname")
    if nick and (' ' in nick or author.get("forceNickname")):
        slug = nick
    else:
        slug = author["name"]
        if author.get("forceSecondName"):
            secondName: str = author["secondName"]
            if " " in secondName:
                slug += ''.join(' ' + n[0] for n in secondName.split(' '))
            else:
                slug += ' ' + secondName
        slug += " " + author["lastName"]
    slug = title_to_unique_name(slug)
    if slug in author_slugs:
        raise Exception(str(author) + "\t" + slug)
    author_slugs.add(slug)
    author["slug"] = slug

with open('authors.json', 'w', encoding='utf-8') as file:
    json.dump(authors, file, ensure_ascii=False, indent=2)
