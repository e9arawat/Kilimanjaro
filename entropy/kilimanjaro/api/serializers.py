"""
serializers for models
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Employee


class UserSerializer(serializers.ModelSerializer):
    """
    user serializer class
    """

    class Meta:
        """
        Meta class
        """

        model = get_user_model()
        fields = ["first_name", "last_name", "email"]


class EmployeeSerializer(serializers.ModelSerializer):
    """
    employee serializer class
    """

    class Meta:
        """
        Meta class
        """

        read_only_fields = ["slug"]
        model = Employee
        fields = ["slug", "start_date", "paid_leaves", "role", "manager"]


class AttendanceSerializer(serializers.Serializer):
    """
    attendance serializer class
    """

    employee = serializers.CharField(max_length=100)
    total_days = serializers.IntegerField()
    total_leaves = serializers.IntegerField()
    total_official_travel = serializers.IntegerField()
    total_absents = serializers.IntegerField()
    total_lates = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()
