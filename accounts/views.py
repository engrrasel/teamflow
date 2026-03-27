from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseForbidden

from accounts.services import can_manage_company
from .models import Membership, EmployeeWeekend
from .forms import (
    SignupForm,
    LoginForm,
    EmployeeInviteForm,
    ForcePasswordChangeForm,
    EmployeeFullEditForm,
    EmployeeEditForm
)

from company.models import CompanyWeekend

User = get_user_model()


# ------------------ Signup ------------------

def signup_view(request):
    form = SignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("/company/create/")

    return render(
        request,
        "accounts/signup.html",
        {"form": form},
    )


# ------------------ Login ------------------

def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]

        user = authenticate(
            request,
            email=email,
            password=password,
        )

        if user:
            login(request, user)

            # session company context
            membership = Membership.objects.filter(user=user).first()

            if membership:
                request.session["company_id"] = membership.company.id

            # default password check
            if user.check_password(settings.DEFAULT_INVITE_PASSWORD):
                return redirect("force_password_change")

            return redirect("dashboard")

        form.add_error(None, "Invalid email or password")

    return render(
        request,
        "accounts/login.html",
        {"form": form},
    )


# ------------------ Logout ------------------

def logout_view(request):
    logout(request)
    return redirect("login")


# ------------------ Dashboard ------------------

@login_required
def dashboard_view(request):

    membership = getattr(request, "membership", None)

    # ❌ No company → create company
    if not membership:
        return redirect("create_company")

    company = membership.company

    # ❌ Weekend setup নাই → company setup page
    if not company.weekends.exists():
        return redirect("company_edit")

    # ❌ Holiday নাই → holiday setup
    if not company.holidays.exists():
        return redirect("company_holiday")

    # ✅ সব ঠিক → dashboard
    return render(request, "accounts/dashboard.html")

# ------------------ Invite Employee ------------------

@login_required
def invite_employee_view(request):

    if not request.membership:
        return redirect("/company/create/")

    company = request.membership.company

    form = EmployeeInviteForm(
        request.POST or None,
        company=company
    )

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        designation = form.cleaned_data["designation"]

        user, created = User.objects.get_or_create(email=email)

        if created:
            user.set_password(settings.DEFAULT_INVITE_PASSWORD)
            user.save()

        membership, created = Membership.objects.get_or_create(
            user=user,
            company=company,
            defaults={
                "role": "employee",
                "designation": designation,
            },
        )

        if not created:
            membership.designation = designation
            membership.save()

        return render(
            request,
            "accounts/invite_success.html",
            {
                "email": email,
                "default_password": settings.DEFAULT_INVITE_PASSWORD,
            },
        )

    return render(
        request,
        "accounts/invite_employee.html",
        {"form": form},
    )


# ------------------ Employee List ------------------

@login_required
def employee_list_view(request):

    if not request.membership:
        return redirect('/company/create/')

    if not can_manage_company(request.membership):
        return HttpResponseForbidden(
            "You are not allowed to view employees."
        )

    company = request.membership.company

    memberships = (
        Membership.objects
        .filter(company=company)
        .select_related('user')
    )

    form = EmployeeInviteForm(company=company)

    # 👉 company default weekend
    company_weekends = CompanyWeekend.objects.filter(company=company)
    weekend_days = set(w.weekday for w in company_weekends)

    return render(
        request,
        "accounts/employee_list.html",
        {
            "memberships": memberships,
            "form": form,
            "weekend_days": weekend_days,   # ⭐ এইটা দরকার
        }
    )

# ------------------ Employee Create ------------------
@login_required
def employee_create_view(request):

    if not request.membership:
        return redirect("/company/create/")

    if not can_manage_company(request.membership):
        return HttpResponseForbidden("Not allowed")

    company = request.membership.company

    if request.method == "POST":
        form = EmployeeInviteForm(
            request.POST,
            company=company,
        )

        if form.is_valid():
            email = form.cleaned_data["email"]
            designation = form.cleaned_data["designation"]

            user, created = User.objects.get_or_create(email=email)

            if created:
                user.set_password(settings.DEFAULT_INVITE_PASSWORD)
                user.save()

            membership = Membership.objects.create(
                user=user,
                company=company,
                role="employee",
                designation=designation,
            )

            weekdays = request.POST.getlist("weekdays")

            if weekdays:
                for w in weekdays:
                    EmployeeWeekend.objects.create(
                        employee=user,
                        weekday=int(w),
                    )
            else:
                company_weekends = CompanyWeekend.objects.filter(
                    company=company
                )

                for w in company_weekends:
                    EmployeeWeekend.objects.create(
                        employee=user,
                        weekday=w.weekday,
                    )

            return redirect("employee_list")

    else:
        form = EmployeeInviteForm(company=company)

    # 👉 company default weekend বের করা
    company_weekends = CompanyWeekend.objects.filter(company=company)
    weekend_days = [w.weekday for w in company_weekends]

    return render(
        request,
        "accounts/employee_add.html",
        {
            "form": form,
            "weekend_days": weekend_days
        },
    )


# ------------------ Employee Edit ------------------

@login_required
def employee_edit_view(request, pk):

    if not request.membership:
        return redirect("/company/create/")

    company = request.membership.company

    membership = get_object_or_404(
        Membership,
        pk=pk,
        company=company,
    )

    form = EmployeeFullEditForm(
        request.POST or None,
        membership=membership,
        company=company,
    )

    user = membership.user

    if request.method == "POST" and form.is_valid():

        user.name = form.cleaned_data["name"]
        user.email = form.cleaned_data["email"]
        user.save()

        membership.designation = form.cleaned_data["designation"]
        membership.save()

        weekdays = request.POST.getlist("weekdays")

        EmployeeWeekend.objects.filter(
            employee=user
        ).delete()

        for w in weekdays:
            EmployeeWeekend.objects.create(
                employee=user,
                weekday=int(w),
            )

        return redirect("employee_list")

    emp_weekends = EmployeeWeekend.objects.filter(employee=user)

    if emp_weekends.exists():
        weekend_days = [w.weekday for w in emp_weekends]

    else:
        company_weekends = CompanyWeekend.objects.filter(
            company=company
        )
        weekend_days = [w.weekday for w in company_weekends]

    return render(
        request,
        "accounts/employee_edit.html",
        {
            "form": form,
            "weekend_days": weekend_days,
        },
    )


# ------------------ Employee Delete ------------------

@login_required
def employee_delete_view(request, pk):

    if not request.membership:
        return redirect("/company/create/")

    company = request.membership.company

    membership = get_object_or_404(
        Membership,
        pk=pk,
        company=company,
    )

    membership.delete()

    return redirect("employee_list")


# ------------------ Employee Weekend ------------------

@login_required
def employee_weekend_view(request, user_id):

    if request.method == "POST":
        weekdays = request.POST.getlist("weekdays")

        EmployeeWeekend.objects.filter(
            employee_id=user_id
        ).delete()

        for w in weekdays:
            EmployeeWeekend.objects.create(
                employee_id=user_id,
                weekday=int(w),
            )

        return redirect("employee_list")

    weekends = EmployeeWeekend.objects.filter(
        employee_id=user_id
    )

    return render(
        request,
        "accounts/employee_weekend.html",
        {"weekends": weekends},
    )


from django.contrib.auth import login

@login_required
def force_password_change_view(request):

    form = ForcePasswordChangeForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        new_password = form.cleaned_data["new_password"]

        request.user.set_password(new_password)
        request.user.is_invited = False
        request.user.save()

        login(request, request.user)

        return redirect("dashboard")

    return render(
        request,
        "accounts/force_password_change.html",
        {"form": form},
    )