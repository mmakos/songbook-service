import json
import os
from datetime import datetime

from django.db import migrations

from Songbook.models import Song


def map_song(s: dict) -> Song:
    song: Song = Song()
    song.id = s["id"]
    song.slug = s["slug"]
    song.title = s["title"]
    song.category_id = s["category"]

    song.create_time = datetime.fromtimestamp(s["created"]["time"])
    song.create_verified = False
    song.creator_id = 2

    song.band_id = s.get("band")
    song.source.add(*s.get("source", []))
    song.lyrics.add(*s.get("lyrics", []))
    song.composer.add(*s.get("composer", []))
    song.translation.add(*s.get("translation", []))
    song.performer.add(*s.get("performer", []))

    song.video = s.get("ytVideo")
    song.key = s.get("key")

    song.verses = s["verses"]

    return song


def migrate_songs(a, b):
    for song_filename in os.listdir('songs_manual'):
        with open(f'songs_manual/{song_filename}', encoding='utf-8') as file:
            song = json.load(file)
        map_song(song).save()


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.RunPython(migrate_songs)
    ]
