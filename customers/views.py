from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Customer
from .forms import CustomerForm


# -----------------------------
# HELPER
# -----------------------------
def get_company_or_redirect(request):
    membership = getattr(request, "membership", None)
    if not membership:
        return None, redirect("dashboard")
    return membership.company, None


# -----------------------------
# CUSTOMER LIST
# -----------------------------
@login_required
def customer_list_view(request):

    company, redirect_resp = get_company_or_redirect(request)
    if redirect_resp:
        return redirect_resp

    customers = Customer.objects.filter(company=company)
    form = CustomerForm(company=company)

    return render(request, "customers/customer_list.html", {
        "customers": customers,
        "form": form
    })


# -----------------------------
# CUSTOMER ADD
# -----------------------------
@login_required
def customer_add_view(request):

    company, redirect_resp = get_company_or_redirect(request)
    if redirect_resp:
        return redirect_resp

    if request.method != "POST":
        return redirect("customer_list")

    customers = Customer.objects.filter(company=company)
    form = CustomerForm(request.POST, company=company)

    if form.is_valid():

        obj = form.save(commit=False)
        obj.company = company

        # 📍 location save
        obj.latitude = request.POST.get("latitude") or None
        obj.longitude = request.POST.get("longitude") or None

        obj.save()
        form.save_m2m()

        return redirect("customer_list")

    return render(request, "customers/customer_list.html", {
        "customers": customers,
        "form": form,
        "open_modal": True
    })


# -----------------------------
# CUSTOMER EDIT
# -----------------------------
@login_required
def customer_edit_view(request, pk):

    company, redirect_resp = get_company_or_redirect(request)
    if redirect_resp:
        return redirect_resp

    customer = get_object_or_404(Customer, pk=pk, company=company)
    customers = Customer.objects.filter(company=company)

    if request.method == "POST":

        form = CustomerForm(
            request.POST,
            instance=customer,
            company=company
        )

        if form.is_valid():

            obj = form.save(commit=False)

            # 📍 location update
            obj.latitude = request.POST.get("latitude") or None
            obj.longitude = request.POST.get("longitude") or None

            obj.save()
            form.save_m2m()

            return redirect("customer_list")

    else:
        form = CustomerForm(instance=customer, company=company)

    return render(request, "customers/customer_list.html", {
        "customers": customers,
        "form": form,
        "open_modal": True
    })


# -----------------------------
# CUSTOMER DELETE
# -----------------------------
@login_required
def customer_delete_view(request, pk):

    company, redirect_resp = get_company_or_redirect(request)
    if redirect_resp:
        return redirect_resp

    customer = get_object_or_404(Customer, pk=pk, company=company)
    customer.delete()

    return redirect("customer_list")


# -----------------------------
# CUSTOMER MAP
# -----------------------------
@login_required
def customer_map_view(request):

    company, redirect_resp = get_company_or_redirect(request)
    if redirect_resp:
        return redirect_resp

    customers = Customer.objects.filter(
        company=company,
        latitude__isnull=False,
        longitude__isnull=False
    )

    return render(request, "customers/customer_map.html", {
        "customers": customers
    })