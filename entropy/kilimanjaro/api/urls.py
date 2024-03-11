"""
API urls
"""

from django.urls import path
from kilimanjaro.api import views

urlpatterns = [
    path("user-list/", views.UserList.as_view(), name="user-list"),
    path("user-detail/<slug:slug>/", views.UserDetail.as_view(), name="user-detail"),
    path("employee-list/", views.EmployeeList.as_view(), name="employee-list"),
    path(
        "employee-detail/<slug:slug>/",
        views.EmployeeDetail.as_view(),
        name="employee-detail",
    ),
    path("attendance-list/", views.AttendanceList.as_view(), name="attendance-list"),
    path(
        "attendance-detail/<slug:slug>/",
        views.AttendanceDetail.as_view(),
        name="attendance-detail",
    ),
]
