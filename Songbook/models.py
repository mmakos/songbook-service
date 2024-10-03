import json
import os

from Songbook.str_convert import title_to_unique_name

songs = {}

for file in os.listdir('songs_manual'):
    with open(f'songs_manual/{file}', encoding='utf-8') as song_file:
        song: dict = json.load(song_file)
    songs[song["slug"]] = {'category': song["category"], 'title': song["title"]}

with open('data/users.json', encoding='utf-8') as file:
    users: dict = {user["id"]: user for user in json.load(file)}
with open('data/categories.json', encoding='utf-8') as file:
    categories: dict = {category["id"]: category for category in json.load(file)}
with open('data/bands.json', encoding='utf-8') as file:
    bands: dict = {band["id"]: band for band in json.load(file)}
with open('data/authors.json', encoding='utf-8') as file:
    authors: dict = {author["id"]: author for author in json.load(file)}


def replace_band(song: dict):
    band = song.get('band')
    if not band:
        return
    song['band'] = bands[band]


def replace_creator(song: dict):
    created = song['created']
    creator_id = created.pop('id')
    user = users[creator_id]
    created['name'] = user['name']
    created['type'] = user['type']


def replace_category(song: dict):
    category = song.get('category')
    if not category:
        return
    song['category'] = categories[category]


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
    replace_category(song)
    replace_creator(song)


def get_song(song_slug: str):
    with open(f'songs_manual/{song_slug}.json', encoding='utf-8') as file:
        song = json.load(file)
        replace(song)
        return song


def get_songs():
    return [{'slug': slug, 'title': song["title"]} for slug, song in songs.items()]


def get_songs_by_category(category: str):
    return [{'slug': slug, 'title': song["title"]} for slug, song in songs.items() if song['category'] == category]


def fast_search(key: str):
    key = title_to_unique_name(key)
    return [{'slug': slug, 'title': song['title'], 'category': categories[song['category']]["slug"]} for slug, song in
            songs.items() if key in slug]
