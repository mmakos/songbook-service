import json
import os

with open('data/bands.json', 'r', encoding='utf-8') as file:
    bands: list = json.load(file)


def get_band_id(band) -> int:
    for b in bands:
        if b["name"] == band["name"]:
            return b["id"]
    raise Exception(band)


for filename in os.listdir('songs_manual'):
    if filename.endswith(".json"):
        f = os.path.join('songs_manual', filename)
        with open(f, 'r', encoding='utf-8') as file:
            song = json.load(file)
        band = song.get("band")
        if band is not None:
            song["band"] = get_band_id(band)
            with open(f, 'w', encoding='utf-8') as file:
                json.dump(song, file, ensure_ascii=False, indent=2)

