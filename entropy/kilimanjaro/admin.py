"""Admin"""

from django.contrib import admin
from .models import Attendance, Employee

# Register your models here.


@admin.register(Attendance)
class AdminAttendance(admin.ModelAdmin):
    """registering Attendance model"""

    list_display = ("id", "date", "user", "status")


@admin.register(Employee)
class AdminEmployee(admin.ModelAdmin):
    """registering Attendance model"""

    list_display = ("id", "user", "start_date", "manager", "role")
