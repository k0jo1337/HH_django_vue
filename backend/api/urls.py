from django.urls import path
from .views import create_appeal, hello, list_appeals

urlpatterns = [
    path("appeals/", list_appeals),
    path("appeals/create/", create_appeal),
    path("hello/", hello),
]
