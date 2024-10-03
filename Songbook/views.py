import json

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest

from Songbook.models import get_song, get_songs, fast_search


def __dump(obj):
    return json.dumps(obj, ensure_ascii=False)


def song(request, song_slug: str):
    try:
        return HttpResponse(__dump(get_song(song_slug)), content_type='application/json')
    except Exception:
        return HttpResponseNotFound()


def songs(request):
    return HttpResponse(__dump(get_songs()), content_type='application/json')


def autocomplete(request):
    key = request.GET.get('q')
    if key is None:
        return HttpResponseBadRequest()
    return HttpResponse(__dump(fast_search(key)), content_type='application/json')
