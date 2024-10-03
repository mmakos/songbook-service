from django.urls import path

from . import views

urlpatterns = [
    path('song/<str:song_slug>/', views.song, name='song'),
    path('songs/', views.songs, name='songs'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
]
