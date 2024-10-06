from django.urls import path

from . import views

urlpatterns = [
    path('song/<str:song_slug>/', views.song, name='song'),
    path('songs/', views.songs, name='songs'),
    path('person/<str:person>/', views.songs_by_person, name='person'),
    path('band/<str:band>/', views.songs_by_band, name='band'),
    path('source/<str:source>/', views.songs_by_source, name='source'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
]
