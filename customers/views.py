from django.shortcuts import render, redirect
from .forms import CustomerForm
from .models import Customer


def customer_list_view(request):
    customers = Customer.objects.all()
    form = CustomerForm()
    return render(request, "customers/customer_list.html", {
        "customers": customers,
        "form": form
    })


def customer_add_view(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customer_list")

    return redirect("customer_list")
