"""Views"""

from datetime import date
from datetime import datetime
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from .forms import (
    AttendanceForm,
    AddEmployeeForm,
    EmployeeUpdateForm,
    AttendanceUpdateForm,
)
from .models import Attendance, Employee


# Create your views here.
class Home(TemplateView):
    """renders home page"""

    template_name = "kilimanjaro/home.html"


class UserLogin(LoginView):
    """render login page"""

    redirect_authenticated_user = True
    template_name = "kilimanjaro/user-login.html"

    def get_success_url(self):
        return reverse_lazy("dashboard")


class Dashboard(ListView):
    """renders user dashboard"""

    template_name = "kilimanjaro/dashboard.html"
    model = Employee
    context_object_name = "attendance_record"
    paginate_by = 10

    def get_queryset(self):
        return self.model.attendance_record()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if not user.is_staff:
            employee = user.employee_related
            context["employee_attendance_record"] = employee.employee_record()
            context["company_record"] = employee.employee_info()
        return context


@login_required
def sign_out(request):
    """logout view"""
    logout(request)
    return redirect("home")


class AddEmployee(FormView):
    """renders sign-up page"""

    template_name = "kilimanjaro/add_employee.html"
    form_class = AddEmployeeForm
    success_url = "user-login"

    def form_valid(self, form):

        new_user = form.save()
        Employee.objects.create(
            user=new_user,
            start_date=date.today(),
            paid_leaves=24,
            role=None,
            manager=None,
        )
        return redirect(self.success_url)


class EmployeeAttendance(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    """renders attendance form"""

    template_name = "kilimanjaro/attendance_form.html"
    success_url = "dashboard"
    form_class = AttendanceForm
    login_url = "user-login"
    error_message = ""

    permission_required = "is_staff"

    def form_valid(self, form):
        selected_date = form.cleaned_data["date"]
        employee_data = User.objects.filter(is_staff=False)
        if Attendance.objects.filter(date=selected_date).exists():
            self.error_message = (
                "Attendance Record already exists for the selected date"
            )
            return self.render_to_response(self.get_context_data(form=form))

        for user in employee_data:
            field_name = f"attendance_status_{user.id}"
            attendance_status = self.request.POST[field_name]
            employee = user.employee_related
            if attendance_status != "Present":
                Attendance.objects.create(
                    date=selected_date,
                    user=user,
                    status=attendance_status,
                    employee=employee,
                )
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["employee_data"] = User.objects.filter(is_staff=False)
        context["error_message"] = getattr(self, "error_message", None)
        return context


class AttendanceRecordView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """renders record view"""

    template_name = "kilimanjaro/attendance_record.html"
    model = Employee
    context_object_name = "attendance_record"
    paginate_by = 10
    permission_required = "is_staff"
    login_url = "user-login"

    def get_queryset(self):
        return self.model.attendance_record()


class AttendanceSheetView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """renders date-wise attendance view"""

    template_name = "kilimanjaro/attendance_sheet.html"
    model = Employee
    paginate_by = 6
    context_object_name = "attendance_data"
    login_url = "user-login"
    permission_required = "is_staff"

    def get_queryset(self):
        return self.model.all_dates_record()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee_data = User.objects.filter(is_staff=False)
        context["employee_data"] = employee_data
        return context


class DateRecordView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """renders view for single attendance"""

    login_url = "user-login"
    permission_required = "is_staff"
    template_name = "kilimanjaro/date-record.html"
    context_object_name = "date_record"
    model = Employee

    def get_queryset(self):
        searched_date = self.request.POST.get("searched_date")
        if not searched_date:
            return {"error_message": "No Date Selected"}
        if searched_date > str(date.today()):
            return {"error_message": "Invalid Date"}

        searched_date = datetime.strptime(searched_date, "%Y-%m-%d").date()

        return self.model.date_record(searched_date)

    def post(self, request, *args, **kwargs):
        """function to search attendance record of any date"""
        return self.get(request, *args, **kwargs)


class UpdateAttendanceView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    """renders form for updating attendance"""

    login_url = "user-login"
    permission_required = "is_staff"
    template_name = "kilimanjaro/update_attendance.html"
    form_class = AttendanceUpdateForm
    success_url = reverse_lazy("attendance_record")

    def get_success_url(self):
        return reverse_lazy("attendance_record")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_date = self.kwargs.get("selected_date")
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
        attendance_data = Employee.date_record(selected_date)
        context["date"] = attendance_data["date"]
        context["attendances"] = attendance_data["username_status"]
        return context

    def post(self, request, *args, **kwargs):
        selected_date = self.kwargs.get("selected_date")

        for field_name, new_status in self.request.POST.items():
            if field_name.startswith("attendance_status_"):
                username = field_name.split("_")[-1]
                user = User.objects.get(username=username)
                employee = user.employee_related
                if (
                    new_status in ("Present", "N/A")
                    or employee.start_date
                    > datetime.strptime(selected_date, "%Y-%m-%d").date()
                ):
                    try:
                        Attendance.objects.get(date=selected_date, user=user).delete()
                    except ObjectDoesNotExist:
                        continue
                else:

                    attendance_record = Attendance.objects.get_or_create(
                        date=selected_date,
                        user=user,
                        employee=employee,
                    )[0]
                    attendance_record.status = new_status
                    attendance_record.save()

        return redirect(reverse("attendance_sheet"))


class SearchEmployee(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """renders deatails of an employee"""

    template_name = "kilimanjaro/search_employee.html"
    login_url = "user-login"
    permission_required = "is_staff"

    def post(self, *args, **kwargs):
        """function to get the searched username"""
        context = super().get_context_data(**kwargs)
        searched = self.request.POST.get("searched")

        if not searched:
            context["error_message"] = "No user Searched"
            return self.render_to_response(context)

        try:
            user = User.objects.get(username=searched)
        except ObjectDoesNotExist:
            context["error_message"] = "User Not Found"
            return self.render_to_response(context)

        if not user.is_staff:
            employee = user.employee_related
            context["attendance_record"] = employee.employee_record()
            context["company_record"] = employee.employee_info()
            context["employee"] = employee

        return self.render_to_response(context)


class EmployeeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """renders form for updating details of an employee"""

    model = Employee
    form_class = EmployeeUpdateForm
    template_name = "kilimanjaro/update_employee.html"
    success_url = reverse_lazy("dashboard")
    login_url = "user-login"
    permission_required = "is_staff"
