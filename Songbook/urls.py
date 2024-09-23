from django.urls import path

from . import views

urlpatterns = [
    path('song/<str:song_id>/', views.song, name='song'),
    path('songs/', views.songs, name='songs'),
    path('songs/<str:category>', views.songs_by_category, name='songs_by_category'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
]
