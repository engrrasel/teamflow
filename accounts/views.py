from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .forms import EmployeeFullEditForm
from .forms import EmployeeEditForm
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    SignupForm,
    LoginForm,
    EmployeeInviteForm,
    ForcePasswordChangeForm,
)
from .models import Membership

User = get_user_model()


# ------------------ Signup ------------------

def signup_view(request):
    form = SignupForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('/company/create/')

    return render(request, 'accounts/signup.html', {'form': form})


# ------------------ Login ------------------

def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)

            # ✅ session এ company context সেট
            membership = Membership.objects.filter(user=user).first()
            if membership:
                request.session['company_id'] = membership.company.id

            # 🔥 Default password হলে force change
            if user.check_password(settings.DEFAULT_INVITE_PASSWORD):
                return redirect('force_password_change')

            return redirect('dashboard')

        form.add_error(None, "Invalid email or password")

    return render(request, 'accounts/login.html', {'form': form})


# ------------------ Logout ------------------

def logout_view(request):
    logout(request)
    return redirect('login')


# ------------------ Dashboard ------------------

@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')


# ------------------ Force Password Change ------------------

@login_required
def force_password_change_view(request):
    form = ForcePasswordChangeForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        new_password = form.cleaned_data['new_password']
        request.user.set_password(new_password)
        request.user.is_invited = False
        request.user.save()

        login(request, request.user)
        return redirect('dashboard')

    return render(request, 'accounts/force_password_change.html', {'form': form})


# ------------------ Invite Employee ------------------

@login_required
def invite_employee_view(request):
    if not request.membership:
        return redirect('/company/create/')

    company = request.membership.company
    form = EmployeeInviteForm(request.POST or None, company=company)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        designation = form.cleaned_data['designation']

        user, created = User.objects.get_or_create(email=email)

        if created:
            user.set_password(settings.DEFAULT_INVITE_PASSWORD)
            user.save()

        membership, created = Membership.objects.get_or_create(
            user=user,
            company=company,
            defaults={
                'role': 'employee',
                'designation': designation
            }
        )

        if not created:
            membership.designation = designation
            membership.save()

        return render(request, 'accounts/invite_success.html', {
            'email': email,
            'default_password': settings.DEFAULT_INVITE_PASSWORD
        })

    return render(request, 'accounts/invite_employee.html', {'form': form})


# ------------------ Employee List ------------------

@login_required
def employee_list_view(request):
    if not request.membership:
        return redirect('/company/create/')

    company = request.membership.company

    memberships = (
        Membership.objects
        .filter(company=company)
        .select_related('user')
    )

    # 🔥 এই লাইনটাই missing
    form = EmployeeInviteForm(company=company)

    return render(request, "accounts/employee_list.html", {
        "memberships": memberships,
        "form": form,   # ✅ পাঠাও
    })

# ------------------ Employee Create (Manual Add) ------------------

@login_required
def employee_create_view(request):
    if not request.membership:
        return redirect('/company/create/')

    company = request.membership.company

    if request.method == "POST":
        form = EmployeeInviteForm(request.POST, company=company)
        if form.is_valid():
            email = form.cleaned_data['email']
            designation = form.cleaned_data['designation']

            user, created = User.objects.get_or_create(email=email)

            if created:
                user.set_password(settings.DEFAULT_INVITE_PASSWORD)
                user.save()

            Membership.objects.create(
                user=user,
                company=company,
                role='employee',
                designation=designation
            )

            return redirect("employee_list")
    else:
        form = EmployeeInviteForm(company=company)

    return render(request, "accounts/employee_add.html", {
        "form": form
    })







from .forms import EmployeeFullEditForm

@login_required
def employee_edit_view(request, pk):
    if not request.membership:
        return redirect('/company/create/')

    company = request.membership.company

    membership = get_object_or_404(
        Membership,
        pk=pk,
        company=company
    )

    form = EmployeeFullEditForm(
        request.POST or None,
        membership=membership,
        company=company
    )

    if request.method == "POST" and form.is_valid():
        # 🔽 Update User
        user = membership.user
        user.name = form.cleaned_data['name']
        user.email = form.cleaned_data['email']
        user.save()

        # 🔽 Update Membership
        membership.designation = form.cleaned_data['designation']
        membership.save()

        return redirect('employee_list')

    return render(request, 'accounts/employee_edit.html', {
        'form': form
    })


@login_required
def employee_delete_view(request, pk):
    if not request.membership:
        return redirect('/company/create/')

    company = request.membership.company

    membership = get_object_or_404(
        Membership,
        pk=pk,
        company=company   # 🔐 SaaS safety
    )

    membership.delete()
    return redirect('employee_list')
