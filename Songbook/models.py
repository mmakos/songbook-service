import json
import os

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from Songbook.str_convert import title_to_unique_name


class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    slug = models.SlugField(max_length=20, unique=True)


class Band(models.Model):
    id = models.IntegerField(primary_key=True)
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=50)
    url = models.URLField(null=True)


class SourceType(models.Model):
    id = models.IntegerField(primary_key=True)
    slug = models.SlugField(max_length=20, unique=True)

    class Meta:
        db_table = "songbook_source_type"


class Source(models.Model):
    id = models.IntegerField(primary_key=True)
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=50)
    src_type = models.ForeignKey(SourceType, on_delete=models.RESTRICT, name="type")
    url = models.URLField(null=True)
    year = models.IntegerField(null=True, validators=[MinValueValidator(1000), MaxValueValidator(2100)])


class Person(models.Model):
    id = models.IntegerField(primary_key=True)
    slug = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=50)
    second_name = models.CharField(null=True, max_length=30)
    nickname = models.CharField(null=True, max_length=100)
    url = models.URLField(null=True)

    force_second_name = models.BooleanField(default=False)
    force_nickname = models.BooleanField(default=False)


class Song(models.Model):
    id = models.IntegerField(primary_key=True)
    slug = models.SlugField(max_length=50, unique=True)
    title = models.CharField(max_length=50, db_index=True, unique=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.RESTRICT)

    creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="songbook_song_creator")
    create_time = models.DateTimeField()
    create_verified = models.BooleanField(default=False)

    editor = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="songbook_song_editor")
    edit_time = models.DateTimeField(null=True)
    edit_verified = models.BooleanField(default=False)

    band = models.ForeignKey(Band, null=True, on_delete=models.SET_NULL)
    source = models.ManyToManyField(Source, blank=True)
    lyrics = models.ManyToManyField(Person, blank=True, related_name="songbook_song_lyrics")
    composer = models.ManyToManyField(Person, blank=True, related_name="songbook_song_composer")
    translation = models.ManyToManyField(Person, blank=True, related_name="songbook_song_translation")
    performer = models.ManyToManyField(Person, blank=True, related_name="songbook_song_performer")

    video = models.JSONField(null=True)
    key = models.JSONField(null=True)

    verses = models.JSONField()


songs = {}

with open('data/users.json', encoding='utf-8') as file:
    users: dict = {user["id"]: user for user in json.load(file)}
with open('data/categories.json', encoding='utf-8') as file:
    categories: dict = {category["id"]: category for category in json.load(file)}
with open('data/bands.json', encoding='utf-8') as file:
    bands: dict = {band["id"]: band for band in json.load(file)}
with open('data/authors.json', encoding='utf-8') as file:
    authors: dict = {author["id"]: author for author in json.load(file)}
with open('data/sources.json', encoding='utf-8') as file:
    sources: dict = {source["id"]: source for source in json.load(file)}


def extend_song_with_author(song_out: dict, song: dict, author: str):
    author_ids = song.get(author)
    if author_ids is not None:
        current = song_out.get('authors', [])
        current.extend(authors[author_id]['slug'] for author_id in author_ids)
        song_out['authors'] = current


def extend_song_with_source(song_out: dict, song: dict):
    source_ids = song.get('source')
    if source_ids is not None:
        current = song_out.get('source', [])
        current.extend(sources[source_id]['slug'] for source_id in source_ids)
        song_out['source'] = current


for file in os.listdir('songs_manual'):
    with open(f'songs_manual/{file}', encoding='utf-8') as song_file:
        song: dict = json.load(song_file)
    song_out = {'category': song["category"], 'title': song["title"]}
    extend_song_with_author(song_out, song, 'performer')
    extend_song_with_author(song_out, song, 'lyrics')
    extend_song_with_author(song_out, song, 'translation')
    extend_song_with_author(song_out, song, 'composer')
    extend_song_with_source(song_out, song)
    band = song.get("band")
    if band:
        song_out["band"] = bands[band]['slug']
    songs[song["slug"]] = song_out


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
    song['category'] = categories[category]['slug']


def replace_authors(song: dict, author: str):
    auth = song.get(author)
    if not auth:
        return
    song[author] = [authors[a] for a in auth]


def replace_source(song: dict):
    src = song.get('source')
    if not src:
        return
    song['source'] = [sources[s] for s in src]


def replace(song: dict):
    replace_authors(song, "composer")
    replace_authors(song, "lyrics")
    replace_authors(song, "translation")
    replace_authors(song, "performer")
    replace_band(song)
    replace_category(song)
    replace_creator(song)
    replace_source(song)


def map_source(source: Source):
    return {
        'slug': source.slug,
        'name': source.name,
        'type': source.src_type.slug
    }


def map_person(person: Person):
    p = {'slug': person.slug, 'name': person.name, 'lastName': person.last_name}
    if person.second_name:
        p['secondName'] = person.second_name
    if person.nickname:
        p['nickname'] = person.nickname
    # if person.url:    // TODO niepotrzebne do piosenki
    #     p['url'] = person.url
    if person.force_nickname:
        p['forceNickname'] = person.force_nickname
    if person.force_second_name:
        p['forceSecondName'] = person.force_second_name

    return p


def get_song(song_slug: str):
    song = Song.objects.get(slug=song_slug)
    s = {
        'slug': song.slug,
        'title': song.title,
        'category': song.category.slug,
        'created': {
            'name': 'TODO',
            'type': 'bot',
            'verified': song.create_verified,
            'time': int(song.create_time.timestamp())
        },
        'verses': song.verses
    }
    if song.band:
        s['band'] = {
            'slug': song.band.slug,
            'name': song.band.name,
        }
    lyrics = [map_person(person) for person in song.lyrics.all()]
    if lyrics:
        s['lyrics'] = lyrics
    performer = [map_person(person) for person in song.performer.all()]
    if performer:
        s['performer'] = performer
    translation = [map_person(person) for person in song.translation.all()]
    if translation:
        s['translation'] = translation
    composer = [map_person(person) for person in song.composer.all()]
    if composer:
        s['composer'] = composer
    if song.video:
        s['ytVideo'] = song.video
    if song.key:
        s['key'] = song.key

    return s


def get_songs():
    return [{'slug': slug, 'title': song["title"], 'category': categories[song['category']]["slug"]} for slug, song in
            songs.items()]


def get_songs_by_person(author):
    person_songs = [{'slug': slug, 'title': song["title"], 'category': categories[song['category']]["slug"]} for
                    slug, song in songs.items() if author in song.get('authors', ())]
    return {
        "person": next(a for a in authors.values() if a['slug'] == author),
        "songs": person_songs,
    }


def get_songs_by_band(band):
    band_songs = [{'slug': slug, 'title': song["title"], 'category': categories[song['category']]["slug"]} for
                  slug, song in songs.items() if band in song.get('band', ())]
    return {
        "band": next(b for b in bands.values() if b['slug'] == band),
        "songs": band_songs,
    }


def get_songs_by_source(source):
    source_songs = [{'slug': slug, 'title': song["title"], 'category': categories[song['category']]["slug"]} for
                    slug, song in songs.items() if source in song.get('source', ())]
    return {
        "source": next(s for s in sources.values() if s['slug'] == source),
        "songs": source_songs,
    }


def fast_search(key: str):
    key = title_to_unique_name(key)
    return [{'slug': slug, 'title': song['title'], 'category': categories[song['category']]["slug"]} for slug, song in
            songs.items() if key in slug]
