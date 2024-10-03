import json
import os
import time

with open('categories.json', encoding='utf-8') as file:
    categories: dict = {category["slug"]: category["id"] for category in json.load(file)}

for file in os.listdir('../songs_manual'):
    with open(f'../songs_manual/{file}', encoding='utf-8') as song_file:
        song: dict = json.load(song_file)
    song["created"] = song.pop("editorInfo")
    with open(f'../songs_manual/{file}', 'w', encoding='utf-8') as song_file:
        json.dump(song, song_file, ensure_ascii=False, indent=2)
