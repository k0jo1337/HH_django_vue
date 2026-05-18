from django.urls import path
from .views import (
    hello,
    create_appeal,
    list_appeals,
    list_all_appeals,
    update_appeal_status,
    appeal_detail,
)

urlpatterns = [
    path("hello/", hello),
    path("appeals/", create_appeal, name="create_appeal"),
    path("appeals/list/", list_appeals, name="list_appeals"),
    path("appeals/all/", list_all_appeals, name="list_all_appeals"),
    path("appeals/<int:pk>/status/", update_appeal_status, name="update_appeal_status"),
    path("appeals/<int:pk>/detail/", appeal_detail, name="appeal_detail"),
]