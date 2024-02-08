"""Forms"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Employee


class AddEmployeeForm(UserCreationForm):
    """form for adding employee"""

    class Meta:
        """overriding"""

        model = User
        fields = ["username", "first_name", "last_name", "email"]


class AttendanceForm(forms.Form):
    """form for adding attendance"""

    date = forms.DateField()
    attendance_status_choices = [
        ("Present", "Present"),
        ("Late", "Late"),
        ("Absent", "Absent"),
        ("Leave", "Leave"),
        ("Official Travel", "Official Travel"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        employee_data = User.objects.filter(is_staff=False)

        for employee in employee_data:
            field_name = f"attendance_status_{employee.id}"
            label = f"{employee.username} - {employee.get_full_name()}"
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
            ("Leave", "Leave"),
            ("Official Travel", "Official Travel"),
        ]
    )


class EmployeeUpdateForm(forms.ModelForm):
    """form for updating employee info"""

    class Meta:
        """overriding"""

        model = Employee
        fields = ["start_date", "role", "manager", "paid_leaves"]
