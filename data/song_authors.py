import json
import os
from typing import Optional

song = {}
authors: list[dict[str, str]]

with open('data/authors.json', encoding='utf-8') as file:
    authors = json.load(file)


wrong = 0


def get_authors(song, a: Optional[list]) -> Optional[list]:
    if a is None:
        return None
    result = []
    for auth in a:
        au = get_author(auth, song)
        if au is not None:
            result.append(au)

    return result if len(result) > 0 else None


def get_author(author: dict[str, str], song: str) -> int:
    global wrong
    name = author.get("name")
    lastName = author.get("lastName")
    if name is not None and lastName is not None:
        for a in authors:
            if a["name"].startswith(name) and a["lastName"] == lastName:
                return a["id"]
            if a["name"].startswith(name) and lastName and lastName[1:3] == ". " and lastName[3:] == a["lastName"]:
                return a["id"]
    if name is not None:
        for a in authors:
            if a.get("nickname") == name:
                return a["id"]

    print(f"Author not found: {author} for song: {song}")
    wrong += 1
    return 999999


def reassign_author(song, key: str):
    au = song.get(key)
    a = get_authors(song["title"], au)
    if a is not None:
        song[key] = a


for filename in os.listdir('songs_manual'):
    if filename.endswith(".json"):
        f = os.path.join('songs_manual', filename)
        with open(f, encoding='utf-8') as file:
            song = json.load(file)
            reassign_author(song, "composer")
            reassign_author(song, "lyrics")
            reassign_author(song, "translation")
            reassign_author(song, "performers")


print()
print(f"Wrong authors: {wrong}")
