from django.urls import path

from apps.preference.views import PreferenceAPIView, GenreListAPIView, TagListAPIView

urlpatterns = [
    path("", PreferenceAPIView.as_view(), name="preference_create"),
    path("genres", GenreListAPIView.as_view(), name="genre_list"),
    path("tags", TagListAPIView.as_view(), name="tag_list"),
]
