"""
Models
"""

from datetime import date, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


class Employee(models.Model):
    """
    Employee models
    """

    role_choices = [
        ("Trainee", "Trainee"),
        ("Employee", "Employee"),
        ("Manager", "Manager"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="employee_related"
    )
    start_date = models.DateField()
    paid_leaves = models.IntegerField()
    role = models.CharField(max_length=100, choices=role_choices, null=True, blank=True)
    manager = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="employee_related",
    )

    objects = models.Manager

    def __str__(self):
        """to return the display string"""
        return f"{self.role}-{self.user}"

    @classmethod
    def generate_dummy_data(cls):
        """
        function to generate dummy-data
        """
        usernames = []
        firstnames = []
        lastnames = []
        emails = []

        for i in range(1, 10001):
            usernames.append("user" + str(i))
            firstnames.append("first" + str(i))
            lastnames.append("last" + str(i))
            emails.append("user" + str(i) + "@enine.school")

        profiles = []
        for username, firstname, lastname, email in zip(
            usernames, firstnames, lastnames, emails
        ):
            profile = User(
                username=username,
                first_name=firstname,
                last_name=lastname,
                email=email,
                password=username + "pass",
            )
            profiles.append(profile)

        User.objects.bulk_create(profiles)

        users = User.objects.filter(is_staff=False)
        start_date = date.today() - timedelta(days=21)
        paid_leaves = 24

        employees = []
        for user in users:
            employee = Employee(
                user=user, start_date=start_date, paid_leaves=paid_leaves
            )
            employees.append(employee)

        Employee.objects.bulk_create(employees)

    def employee_record(self):
        """to return the record of one employee"""
        total_days = (date.today() - self.start_date).days + 1
        total_leaves = self.attendance_related.filter(status="Leave").count()
        total_official_travel = self.attendance_related.filter(
            status="Official Travel"
        ).count()
        total_lates = self.attendance_related.filter(status="Late").count()
        total_absents = (
            self.attendance_related.filter(status="Absent").count() + total_lates // 3
        )
        total_lates = total_lates % 3
        attendance_percentage = (
            round(((total_days - total_absents) / total_days) * 100, 2)
            if total_days > 0
            else 0
        )

        attendance_dict = {
            "total_days": total_days,
            "total_leaves": total_leaves,
            "total_official_travel": total_official_travel,
            "total_absents": total_absents,
            "total_lates": total_lates,
            "attendance_percentage": attendance_percentage,
        }
        return attendance_dict

    @classmethod
    def attendance_record(cls, employees):
        """to return the record of all the employees"""
        # ids = [x for x in range((i-1)*10,i*10+3)]
        # print(f"page= {i}, ids={ids}")
        # employees = cls.objects.filter(pk__in=ids)
        # employees = cls.objects.all()
        # print(employees[1].id)
        attendance_dict = [
            {employee.user: employee.employee_record()} for employee in employees
        ]
        return attendance_dict

    def employee_info(self):
        """to return the company related information of each employee"""
        return {
            "user": self.user,
            "start_date": self.start_date,
            "paid_leaves": self.paid_leaves,
            "role": self.role,
            "manager": self.manager,
        }

    @classmethod
    def find_start_date(cls):
        """function to find the minimum date"""
        all_dates_object = cls.objects.all().values("start_date")
        if not all_dates_object:
            return []
        all_dates = [x["start_date"] for x in all_dates_object]
        return min(all_dates)

    @classmethod
    def date_record(cls, date_param, employees):
        """to find the attendance record of all the employees on a particular date"""
        # employees = cls.objects.all()
        date_data = {"date": date_param, "username_status": []}

        for employee in employees:
            status = "N/A"
            try:
                status = employee.attendance_related.get(date=date_param).status
            except ObjectDoesNotExist:
                if date_param >= employee.start_date:
                    status = "Present"

            date_data["username_status"].append(
                {
                    "username": employee.user.username,
                    "status": status,
                }
            )
        return date_data

    @classmethod
    def all_dates_record(cls):
        """return the record of all the dates"""
        current_date = cls.find_start_date()
        dates_record = []
        delta = timedelta(days=1)
        if not cls.objects.all():
            return []
        try:
            obj = cls.objects.all().first()
        except ObjectDoesNotExist:
            return dates_record
        while current_date <= date.today():
            dates_record.append(obj.date_record(current_date))
            current_date += delta
        return dates_record


class Attendance(models.Model):
    """Attendance Model"""

    status_choices = [
        ("Present", "Present"),
        ("Late", "Late"),
        ("Absent", "Absent"),
        ("Sick", "Sick"),
        ("Vacation", "Vacation"),
        ("Travel", "Travel"),
    ]

    date = models.DateField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="attendance_related"
    )
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="attendance_related"
    )

    status = models.CharField(max_length=20, choices=status_choices)

    def __str__(self):
        """to return display name"""
        return f"{self.user} - {self.date} - {self.status}"

    objects = models.Manager
