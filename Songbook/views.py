import json

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest

from Songbook.models import get_song, get_songs, fast_search, get_songs_by_person, get_songs_by_band, \
    get_songs_by_source


def __dump(obj):
    return json.dumps(obj, ensure_ascii=False)


def song(request, song_slug: str):
    try:
        return HttpResponse(__dump(get_song(song_slug)), content_type='application/json')
    except Exception:
        return HttpResponseNotFound()


def songs(request):
    return HttpResponse(__dump(get_songs()), content_type='application/json')


def songs_by_person(request, person: str):
    return HttpResponse(__dump(get_songs_by_person(person)), content_type='application/json')


def songs_by_band(request, band: str):
    return HttpResponse(__dump(get_songs_by_band(band)), content_type='application/json')


def songs_by_source(request, source: str):
    return HttpResponse(__dump(get_songs_by_source(source)), content_type='application/json')


def autocomplete(request):
    key = request.GET.get('q')
    if key is None:
        return HttpResponseBadRequest()
    return HttpResponse(__dump(fast_search(key)), content_type='application/json')
