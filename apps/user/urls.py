from django.urls import path
from apps.user.views.LoginView import LoginView
from apps.user.views.registerview import RegisterView
from apps.user.views.profileview import MeView, WithdrawView

app_name = "user"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("signup/", RegisterView.as_view(), name="signup"),
    path("me/", MeView.as_view(), name="profile"),
    path("me/delete/", WithdrawView.as_view(), name="profile_delete"),
]
