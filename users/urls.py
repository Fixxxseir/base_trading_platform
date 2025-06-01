from django.contrib.auth.views import LogoutView
from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from users.apps import UsersConfig
from users.views import (
    CustomPasswordChange,
    UserMe,
    UserRegisterAPIView,
    EmailVerificationView,
    UserLoginView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("register/", UserRegisterAPIView.as_view(), name="user-register"),
    path(
        "email-confirm/<str:token>/",
        EmailVerificationView.as_view(permission_classes=(AllowAny,)),
        name="email_confirm",
    ),
    path("login/", UserLoginView.as_view(), name="login"),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=(AllowAny,)),
        name="user-token_refresh",
    ),
    path(
        "settings/password/change",
        CustomPasswordChange.as_view(),
        name="users-password-change",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", UserMe.as_view(), name="user-profile"),
]
