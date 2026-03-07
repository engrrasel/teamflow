from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .forms import (
    CompanyCreateForm,
    DesignationForm,
    DesignationGroupForm,
)
from .models import Designation, DesignationGroup
from accounts.models import Membership

from .models import CompanyWeekend

# ---------- Helper ----------
def get_membership(request):
    return getattr(request, "membership", None)


# ---------- Company ----------
from django.contrib import messages

from django.contrib import messages
from .models import CompanyWeekend
from django.contrib import messages
from .models import CompanyWeekend

@login_required
def create_company_view(request):

    membership = get_membership(request)

    # যদি already company থাকে → dashboard
    if membership:
        return redirect("dashboard")

    form = CompanyCreateForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            company = form.save()

            # company admin create
            Membership.objects.create(
                user=request.user,
                company=company,
                role="company_admin"
            )

            # 🔽 weekend save
            weekdays = request.POST.getlist("weekdays")

            for w in weekdays:
                CompanyWeekend.objects.create(
                    company=company,
                    weekday=int(w)
                )

            # session এ company সেট
            request.session["company_id"] = company.id

            # success message
            messages.success(request, "Company created successfully!")

            return redirect("dashboard")

    return render(
        request,
        "company/create_company.html",
        {
            "form": form,
            "weekend_days": []   # ✔ template এর সাথে match
        }
    )
# ---------- Designation ----------
@login_required
def designation_list_view(request):
    membership = get_membership(request)
    if not membership:
        return redirect('create_company')

    company = membership.company

    # 🔽 NEW
    form = DesignationForm(request.POST or None, company=company)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("designation_list")

    designations = (
        Designation.objects
        .filter(group__company=company)
        .select_related('group')
    )

    return render(request, "company/designation_list.html", {
        "designations": designations,
        "form": form,   # 🔽 পাঠালাম
    })


@login_required
def designation_create_view(request):
    membership = get_membership(request)
    if not membership:
        return redirect('create_company')

    form = DesignationForm(
        request.POST or None,
        company=membership.company
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("designation_list")

    return render(request, "company/designation_add.html", {"form": form})


@login_required
def designation_edit_view(request, pk):
    membership = get_membership(request)
    if not membership:
        return redirect('create_company')

    designation = get_object_or_404(
        Designation,
        pk=pk,
        group__company=membership.company
    )

    form = DesignationForm(
        request.POST or None,
        instance=designation,
        company=membership.company
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('designation_list')

    return render(request, "company/designation_edit.html", {"form": form})


@login_required
def designation_delete_view(request, pk):
    membership = get_membership(request)
    if not membership:
        return redirect('create_company')

    designation = get_object_or_404(
        Designation,
        pk=pk,
        group__company=membership.company
    )

    designation.delete()
    return redirect('designation_list')


# ---------- Designation AJAX ----------
@login_required
def create_designation_ajax(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    membership = get_membership(request)
    if not membership:
        return JsonResponse({"error": "No company"}, status=400)

    group_name = request.POST.get("group", "").strip()
    designation_name = request.POST.get("designation", "").strip()
    company = membership.company

    group = DesignationGroup.objects.filter(
        company=company,
        name__iexact=group_name
    ).first()

    if not group:
        group = DesignationGroup.objects.create(
            name=group_name,
            company=company
        )

    designation = Designation.objects.filter(
        group=group,
        name__iexact=designation_name
    ).first()

    if not designation:
        designation = Designation.objects.create(
            name=designation_name,
            group=group
        )

    return JsonResponse({
        "id": designation.id,
        "name": designation.name,
        "group": group.name
    })


# ---------- Groups ----------
@login_required
def group_list_view(request):
    membership = get_membership(request)
    if not membership:
        return redirect('create_company')

    company = membership.company

    form = DesignationGroupForm(
        request.POST or None,
        company=company
    )

    if request.method == "POST" and form.is_valid():
        group = form.save(commit=False)
        group.company = company
        group.save()
        return redirect('group_list')

    groups = DesignationGroup.objects.filter(company=company)

    return render(request, "company/group_list.html", {
        "groups": groups,
        "form": form,   # 🔽 পাঠালাম
    })



@login_required
def group_create_view(request):
    membership = get_membership(request)
    if not membership:
        return redirect('create_company')

    form = DesignationGroupForm(
        request.POST or None,
        company=membership.company
    )

    if request.method == "POST" and form.is_valid():
        group = form.save(commit=False)
        group.company = membership.company   # ✅ MUST
        group.save()
        return redirect("group_list")

    return render(request, "company/group_add.html", {"form": form})


@login_required
def group_edit_view(request, pk):
    membership = get_membership(request)
    if not membership:
        return redirect('create_company')

    group = get_object_or_404(
        DesignationGroup,
        pk=pk,
        company=membership.company
    )

    form = DesignationGroupForm(
        request.POST or None,
        instance=group,
        company=membership.company
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('group_list')

    return render(request, "company/group_edit.html", {"form": form})


@login_required
def group_delete_view(request, pk):
    membership = get_membership(request)
    if not membership:
        return redirect('create_company')

    group = get_object_or_404(
        DesignationGroup,
        pk=pk,
        company=membership.company
    )

    group.delete()
    return redirect('group_list')



@login_required
def company_weekend_view(request):

    company = request.membership.company

    if request.method == "POST":

        weekdays = request.POST.getlist("weekdays")

        CompanyWeekend.objects.filter(company=company).delete()

        for w in weekdays:
            CompanyWeekend.objects.create(
                company=company,
                weekday=int(w)
            )

        return redirect("company_weekend")

    weekends = CompanyWeekend.objects.filter(company=company)

    return render(
        request,
        "company/weekend_setup.html",
        {"weekends": weekends}
    )

from .models import CompanyHoliday

@login_required
def company_holiday_view(request):

    company = request.membership.company

    if request.method == "POST":

        name = request.POST.get("name")
        date = request.POST.get("date")

        CompanyHoliday.objects.create(
            company=company,
            name=name,
            date=date
        )

        return redirect("company_holiday")

    holidays = CompanyHoliday.objects.filter(company=company)

    return render(
        request,
        "company/holiday_setup.html",
        {"holidays":holidays}
    )

from .models import CompanyWeekend

@login_required
def company_edit_view(request):

    membership = get_membership(request)

    if not membership:
        return redirect("create_company")

    company = membership.company

    form = CompanyCreateForm(
        request.POST or None,
        instance=company
    )

    if request.method == "POST" and form.is_valid():

        form.save()

        # weekend update
        weekdays = request.POST.getlist("weekdays")

        CompanyWeekend.objects.filter(company=company).delete()

        for w in weekdays:
            CompanyWeekend.objects.create(
                company=company,
                weekday=int(w)
            )

        return redirect("dashboard")

    # 🔥 template এর জন্য শুধু weekday list পাঠাচ্ছি
    weekends = CompanyWeekend.objects.filter(company=company)
    weekend_days = [w.weekday for w in weekends]

    return render(
        request,
        "company/company_edit.html",
        {
            "form": form,
            "weekend_days": weekend_days
        }
    )