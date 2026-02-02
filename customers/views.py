from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Customer
from .forms import CustomerForm


@login_required
def customer_list_view(request):
    company = request.membership.company

    # ✅ Only this company's customers
    customers = Customer.objects.filter(company=company)

    form = CustomerForm(company=company)

    return render(request, "customers/customer_list.html", {
        "customers": customers,
        "form": form
    })


@login_required
def customer_add_view(request):
    company = request.membership.company

    if request.method == "POST":
        form = CustomerForm(request.POST, company=company)
        if form.is_valid():
            obj = form.save(commit=False)

            # 🔴 MUST for SaaS isolation
            obj.company = company

            obj.save()
            form.save_m2m()

    return redirect("customer_list")
