"""Forms"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Employee, Attendance


class AddEmployeeForm(UserCreationForm):
    """form for adding employee"""

    class Meta:
        """overriding"""

        model = User
        fields = ["username", "first_name", "last_name", "email"]


class AttendanceForm(forms.ModelForm):
    """form for adding attendance"""

    attendance_status_choices = [
        ("Present", "Present"),
        ("Late", "Late"),
        ("Absent", "Absent"),
        ("Sick", "Sick"),
        ("Vacation", "Vacation"),
        ("Travel", "Travel"),
    ]

    class Meta:
        """
        Meta class
        """

        model = Attendance
        fields = ["date"]

        widgets = {
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        employee_data = User.objects.filter(is_staff=False)

        for employee in employee_data:
            field_name = f"attendance_status_{employee.id}"
            label = f"{employee.get_full_name()}"
            widget = forms.Select(
                attrs={"class": "form-control"}, choices=self.attendance_status_choices
            )
            self.fields[field_name] = forms.ChoiceField(
                label=label,
                required=True,
                widget=widget,
                choices=self.attendance_status_choices,
            )


class AttendanceUpdateForm(forms.Form):
    """form for updating attendance"""

    status = forms.ChoiceField(
        choices=[
            ("Present", "Present"),
            ("Late", "Late"),
            ("Absent", "Absent"),
            ("Sick", "Sick"),
            ("Vacation", "Vacation"),
            ("Travel", "Travel"),
        ]
    )


class EmployeeUpdateForm(forms.ModelForm):
    """form for updating employee info"""

    class Meta:
        """overriding"""

        model = Employee
        fields = ["start_date", "role", "manager", "paid_leaves"]
