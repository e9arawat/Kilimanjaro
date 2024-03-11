"""
API views
"""

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveAPIView,
    ListAPIView,
)
from django.contrib.auth import get_user_model
from ..models import Employee
from .serializers import UserSerializer, EmployeeSerializer, AttendanceSerializer


class MyOffsetPagination(LimitOffsetPagination):
    """
    pagination class
    """

    default_limit = 10
    max_limit = 1000


class UserList(ListCreateAPIView):
    """
    display the list of users
    """

    pagination_class = MyOffsetPagination
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class UserDetail(RetrieveUpdateDestroyAPIView):
    """
    display the details of a user
    """

    def get_object(self):
        """
        return a single object
        """
        slug = self.kwargs["slug"]
        employee = Employee.objects.get(slug=slug)
        return get_user_model().objects.get(username=employee.user)

    serializer_class = UserSerializer


class EmployeeList(ListCreateAPIView):
    """
    display the list of all the employees
    """

    pagination_class = MyOffsetPagination
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeDetail(RetrieveUpdateDestroyAPIView):
    """
    display the details of each employee
    """

    lookup_field = "slug"
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class AttendanceList(ListAPIView):
    """
    display the attendance record
    """

    pagination_class = MyOffsetPagination
    data = []
    for employee in Employee.objects.all():
        temp = employee.employee_record()
        temp["employee"] = employee.user
        data.append(temp)
    queryset = data
    serializer_class = AttendanceSerializer


class AttendanceDetail(RetrieveAPIView):
    """
    display attendance record of each employee
    """

    def get_object(self):
        """
        return a single object
        """
        slug = self.kwargs["slug"]
        employee = Employee.objects.get(slug=slug)
        data = employee.employee_record()
        data["employee"] = employee.user
        return data

    serializer_class = AttendanceSerializer
