from django.urls import path

from . import views

urlpatterns = [
    path('song/<str:song_slug>/', views.song, name='song'),
    path('songs/', views.songs, name='songs'),
    path('person/<str:person>/', views.songs_by_person, name='person'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
]
