from django.urls import path
from apps.user.views.LoginView import LoginView
from apps.user.views.preference.preference_api import PreferenceAPIView
from apps.user.views.registerview import RegisterView

app_name = "user"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("signup/", RegisterView.as_view(), name="signup"),
    path("preference/", PreferenceAPIView.as_view(), name="preference_create"),
]
