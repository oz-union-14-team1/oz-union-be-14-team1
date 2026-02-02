from django.urls import path
from apps.user.views.LoginView import LoginView
from apps.user.views.registerview import RegisterView
from apps.user.views.profileview import MeView, WithdrawView
from apps.user.views.account_recovery import (
    FindAccountView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)
from apps.user.views.logout import LogoutView

app_name = "user"

urlpatterns = [
    path("login", LoginView.as_view(), name="login"),
    path("signup", RegisterView.as_view(), name="signup"),
    path("me", MeView.as_view(), name="profile"),
    path("me/delete", WithdrawView.as_view(), name="profile_delete"),
    path("find-account", FindAccountView.as_view(), name="find_account"),
    path(
        "password/reset/request",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password/reset/confirm",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
]
