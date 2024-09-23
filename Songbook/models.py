import json

from Songbook.songs import songs, categories
from Songbook.str_convert import normalize_for_search, title_to_unique_name


def get_song(song_id: str):
    with open(f'songs/{song_id}.json', encoding='utf-8') as file:
        return file.read()


def get_songs():
    return json.dumps(
        [{'id': title_to_unique_name(song), 'title': song} for category in songs.values() for song in category])


def get_songs_by_category(category: str):
    return json.dumps([{'id': title_to_unique_name(song), 'title': song} for song in songs[category]])


def fast_search(key: str):
    key = normalize_for_search(key.casefold().replace(" ", ""))
    return json.dumps(
        [{'id': title_to_unique_name(song), 'title': song, 'category': {'id': category, 'name': categories[category]}}
         for category, cat_songs in
         songs.items()
         for song in cat_songs if key in normalize_for_search(song.casefold().replace(" ", ""))])
