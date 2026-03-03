from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Customer
from .forms import CustomerForm


@login_required
def customer_list_view(request):

    company = request.membership.company

    # Only this company's customers
    customers = Customer.objects.filter(company=company)

    form = CustomerForm(company=company)

    return render(request, "customers/customer_list.html", {
        "customers": customers,
        "form": form
    })


@login_required
def customer_add_view(request):

    company = request.membership.company

    customers = Customer.objects.filter(company=company)

    if request.method == "POST":

        form = CustomerForm(request.POST, company=company)

        if form.is_valid():

            obj = form.save(commit=False)
            obj.company = company
            obj.save()
            form.save_m2m()

            return redirect("customer_list")

        # form invalid হলে popup open থাকবে
        return render(request, "customers/customer_list.html", {
            "customers": customers,
            "form": form,
            "open_modal": True
        })

    return redirect("customer_list")


# -----------------------------
# CUSTOMER EDIT
# -----------------------------

@login_required
def customer_edit_view(request, pk):

    company = request.membership.company

    customer = get_object_or_404(
        Customer,
        pk=pk,
        company=company
    )

    customers = Customer.objects.filter(company=company)

    if request.method == "POST":

        form = CustomerForm(
            request.POST,
            instance=customer,
            company=company
        )

        if form.is_valid():
            form.save()
            return redirect("customer_list")

        return render(request, "customers/customer_list.html", {
            "customers": customers,
            "form": form,
            "open_modal": True
        })

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

    company = request.membership.company

    customer = get_object_or_404(
        Customer,
        pk=pk,
        company=company
    )

    customer.delete()

    return redirect("customer_list")