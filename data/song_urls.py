import json
import os


def extract_yt_id(url: str):
    if not url.startswith('https://www.youtube.com/watch?v='):
        raise Exception(url)
    yt_id = url[32:]
    if len(yt_id) != 11:
        raise Exception(yt_id)
    return yt_id


with open(f'song_urls.json', encoding='utf-8') as file:
    songs = json.load(file)


for filename in os.listdir('../songs_manual'):
    with open(f'../songs_manual/{filename}', encoding='utf-8') as file:
        song = json.load(file)
        links = songs.get(song['slug'])
        if not links:
            continue
        if not isinstance(links, list):
            links = [links]

        song['ytVideo'] = [extract_yt_id(url) for url in links]

    with open(f'../songs_manual/{filename}', 'w', encoding='utf-8') as file:
        json.dump(song, file, indent=2, ensure_ascii=False)
