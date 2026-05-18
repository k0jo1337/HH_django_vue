from django.contrib import admin
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


def logout_redirect(request):
    logout(request)
    return redirect(settings.FRONTEND_URL)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("logout", logout_redirect, name="logout_redirect_no_slash"),
    path("logout/", logout_redirect, name="logout_redirect"),
    path("api/", include("api.urls")),
    path("api/account/", include("account.urls")),
    path("api/news/", include("news.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
