from django.urls import path
from apps.user.views.LoginView import LoginView
from apps.user.views.profile_img_view import ProfileImageView
from apps.user.views.registerview import RegisterView
from apps.user.views.profileview import MeView, WithdrawView
from apps.user.views.account_recovery import (
    FindAccountView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    CodeVerifyView,
    CodeSendView,
)
from apps.user.views.logout import LogoutView
from apps.user.views.social_login_view import GoogleLoginView, DiscordLoginView
from apps.user.views.token_refresh import TokenRefreshWithBlacklistView
from apps.user.views.availability import EmailAvailabilityView, NicknameAvailabilityView

app_name = "user"

urlpatterns = [
    path("login", LoginView.as_view(), name="login"),
    path("signup", RegisterView.as_view(), name="signup"),
    path("me", MeView.as_view(), name="profile"),
    path("me/delete", WithdrawView.as_view(), name="profile_delete"),
    path("code/send", CodeSendView.as_view(), name="code_send"),
    path("code/verify", CodeVerifyView.as_view(), name="code_verify"),
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
    path("logout", LogoutView.as_view(), name="logout"),
    path(
        "token/refresh", TokenRefreshWithBlacklistView.as_view(), name="token_refresh"
    ),
    path("me/image", ProfileImageView.as_view(), name="profile_image"),
    path("check-email", EmailAvailabilityView.as_view(), name="check-email"),
    path("check-nickname", NicknameAvailabilityView.as_view(), name="check-nickname"),

    # social
    path("google/login", GoogleLoginView.as_view(), name="google_login"),
    path("discord/login", DiscordLoginView.as_view(), name="discord_login"),
]
