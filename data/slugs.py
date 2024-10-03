import json
import os

for file in os.listdir('../songs_manual'):
    with open(f'../songs_manual/{file}', encoding='utf-8') as song_file:
        song: dict = json.load(song_file)
    del song["created"]
    with open(f'../songs_manual/{file}', 'w', encoding='utf-8') as song_file:
        json.dump(song, song_file, ensure_ascii=False, indent=2)
