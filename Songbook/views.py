from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest

from Songbook.models import get_song, get_songs, fast_search, get_songs_by_category


def song(request, song_id: str):
    try:
        return HttpResponse(get_song(song_id), content_type='application/json')
    except Exception:
        return HttpResponseNotFound()


def songs(request):
    return HttpResponse(get_songs(), content_type='application/json')


def songs_by_category(request, category: str):
    return HttpResponse(get_songs_by_category(category), content_type='application/json')


def autocomplete(request):
    key = request.GET.get('q')
    if key is None:
        return HttpResponseBadRequest()
    return HttpResponse(fast_search(key), content_type='application/json')
