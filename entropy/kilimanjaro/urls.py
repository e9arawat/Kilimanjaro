"""URLS"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.Home.as_view(), name="home"),
    path("add_employee/", views.AddEmployee.as_view(), name="add_employee"),
    path("sign_out/", views.sign_out, name="sign_out"),
    path(
        "attendance_form/", views.EmployeeAttendance.as_view(), name="attendance_form"
    ),
    # path(
    #     "attendance_record/",
    #     views.AttendanceRecordView.as_view(),
    #     name="attendance_record",
    # ),
    # path(
    #     "attendance_sheet/",
    #     views.AttendanceSheetView.as_view(),
    #     name="attendance_sheet",
    # ),
    path(
        "update_attendance/<str:selected_date>/",
        views.UpdateAttendanceView.as_view(),
        name="update_attendance",
    ),
    path("date-record/", views.DateRecordView.as_view(), name="date-record"),
    path("search_employee/", views.SearchEmployee.as_view(), name="search_employee"),
    path(
        "update_employee/<int:pk>/",
        views.EmployeeUpdateView.as_view(),
        name="update_employee",
    ),
    path("dashboard/", views.Dashboard.as_view(), name="dashboard"),
    path("user-login/", views.UserLogin.as_view(), name="user-login"),
]
