from django.urls import path

from apps.preference.views import PreferenceAPIView

urlpatterns = [
    path("preference/", PreferenceAPIView.as_view(), name="preference_create"),
]
