from django.urls import path

from apps.preference.views import PreferenceAPIView

urlpatterns = [
    path("", PreferenceAPIView.as_view(), name="preference_create"),
]
