from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    register_view,
    login_view,
    logout_view,
    me_view,
    profile_view
)

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("me/", me_view, name="me"),
    path("profile/", profile_view, name="profile"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)