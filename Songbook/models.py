import json

from Songbook.songs import songs, categories
from Songbook.str_convert import normalize_for_search, title_to_unique_name

with open('data/bands.json', encoding='utf-8') as file:
    bands = {band["id"]: band for band in json.load(file)}
with open('data/authors.json', encoding='utf-8') as file:
    authors = {author["id"]: author for author in json.load(file)}


def replace_band(song: dict):
    band = song.get('band')
    if not band:
        return
    song['band'] = bands[band]


def replace_authors(song: dict, author: str):
    auth = song.get(author)
    if not auth:
        return
    song[author] = [authors[a] for a in auth]


def replace(song: dict):
    replace_authors(song, "composer")
    replace_authors(song, "lyrics")
    replace_authors(song, "translation")
    replace_authors(song, "performer")
    replace_band(song)


def get_song(song_id: str):
    # time.sleep(2)
    with open(f'songs_manual/{song_id}.json', encoding='utf-8') as file:
        song = json.load(file)
        replace(song)
        return json.dumps(song, ensure_ascii=False)


def get_songs():
    return json.dumps(
        [{'id': title_to_unique_name(song), 'title': song} for category in songs.values() for song in category])


def get_songs_by_category(category: str):
    return json.dumps([{'id': title_to_unique_name(song), 'title': song} for song in songs[category]])


def fast_search(key: str):
    # time.sleep(1)
    key = normalize_for_search(key.casefold().replace(" ", ""))
    return json.dumps(
        [{'id': title_to_unique_name(song), 'title': song, 'category': {'id': category, 'name': categories[category]}}
         for category, cat_songs in
         songs.items()
         for song in cat_songs if key in normalize_for_search(song.casefold().replace(" ", ""))])
