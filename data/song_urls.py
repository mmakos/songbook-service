import json
import os
from typing import Optional

from googleapiclient.discovery import build

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

with open('bands.json', encoding='utf-8') as file:
    bands = {band["id"]: band["name"] for band in json.load(file)}
with open('authors.json', encoding='utf-8') as file:
    authors = {author["id"]: author["lastName"] for author in json.load(file)}


def get_song_yt_id(song: dict) -> Optional[str]:
    title = song["title"]
    band = song.get('band')
    if band is not None:
        band = bands[band]
    lyrics = song.get('lyrics')
    composer = song.get('composer')
    if lyrics is not None and len(lyrics) > 0:
        lyrics = authors[lyrics[0]]
    if composer is not None and len(composer) > 0:
        composer = authors[composer[0]]
        if composer == lyrics:
            composer = None

    query = title
    if band:
        query += f" {band}"
    else:
        if lyrics:
            query += f" {lyrics}"
        if composer:
            query += f" {composer}"

    search_response = youtube.search().list(
        q=query,
        part='snippet',
        maxResults=5,
        type='video'
    ).execute()

    for item in search_response.get("items", []):
        channel_title = item['snippet']['channelTitle'].lower()
        video_id = item['id']['videoId']

        if 'topic' in channel_title or 'vevo' in channel_title or 'official' in channel_title:
            return video_id

    if 'items' in search_response and len(search_response['items']) > 0:
        return search_response['items'][0]['id']['videoId']

    return None


with open(f'song_urls.json', encoding='utf-8') as file:
    songs = json.load(file)


for filename in os.listdir('../songs_manual'):
    with open(f'../songs_manual/{filename}', encoding='utf-8') as file:
        song = json.load(file)
        if song['slug'] in songs:
            continue
        try:
            yt_id = get_song_yt_id(song)
        except:
            break
        if yt_id:
            songs[song["slug"]] = f"https://www.youtube.com/watch?v={yt_id}"
        else:
            title: str = song['title']
            songs[song["slug"]] = f"https://www.youtube.com/results?search_query={title.replace(' ', '+')}"
        print(f"{song['slug']}: {songs[song['slug']]}")


with open('song_urls.json', 'w', encoding='utf-8') as file:
    json.dump(songs, file, indent=2, ensure_ascii=False)
