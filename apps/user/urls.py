from django.urls import path
from apps.user.views.LoginView import LoginView

app_name = "user"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
]
