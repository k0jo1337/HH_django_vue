from django.urls import path
from .views import (
    hello,
    create_appeal,
    list_appeals,
    list_all_appeals,
    update_appeal_status,
    appeal_detail,
    assign_executor,
    get_executors,
    create_executor,
    update_executor,
    delete_executor,
    report_by_executor,
    export_appeals_csv,
)

urlpatterns = [
    path("hello/", hello),
    path("appeals/", create_appeal, name="create_appeal"),
    path("appeals/list/", list_appeals, name="list_appeals"),
    path("appeals/all/", list_all_appeals, name="list_all_appeals"),
    path("appeals/<int:pk>/status/", update_appeal_status, name="update_appeal_status"),
    path("appeals/<int:pk>/detail/", appeal_detail, name="appeal_detail"),
    path("appeals/<int:pk>/assign/", assign_executor, name="assign_executor"),
    path("executors/", get_executors, name="get_executors"),
    path("executors/create/", create_executor, name="create_executor"),
    path("executors/<int:pk>/", update_executor, name="update_executor"),
    path("executors/<int:pk>/delete/", delete_executor, name="delete_executor"),
    path("report/by-executor/", report_by_executor, name="report_by_executor"),
    path("export/csv/", export_appeals_csv, name="export_appeals_csv"),
]