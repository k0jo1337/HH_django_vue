from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    register_view,
    login_view,
    logout_view,
    me_view,
    profile_view,
    change_password_view,
    password_reset_request,
    password_reset_verify,
    password_reset_confirm
)

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("me/", me_view, name="me"),
    path("profile/", profile_view, name="profile"),
    path("change-password/", change_password_view, name="change_password"),
    path("password-reset/", password_reset_request, name="password_reset"),
    path("password-reset/verify/<uidb64>/<token>/", password_reset_verify, name="password_reset_verify"),
    path("password-reset/confirm/", password_reset_confirm, name="password_reset_confirm"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)