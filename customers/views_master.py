from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django import forms

from accounts.services import can_manage_company
from .models import BusinessCategory, SellingProduct


class NameForm(forms.Form):
    name = forms.CharField(max_length=120)


# ---------- Business Category ----------

@login_required
def business_category_list(request):
    if not can_manage_company(request.membership):
        return HttpResponseForbidden("No permission")

    company = request.membership.company
    items = BusinessCategory.objects.filter(company=company)
    form = NameForm()

    if request.method == "POST":
        form = NameForm(request.POST)
        if form.is_valid():
            BusinessCategory.objects.create(
                company=company,
                name=form.cleaned_data['name']
            )
            return redirect('business_category_list')

    return render(request, "customers/master_list.html", {
        "title": "Business Categories",
        "items": items,
        "form": form,
        "delete_url": "business_category_delete"
    })


@login_required
def business_category_delete(request, pk):
    if not can_manage_company(request.membership):
        return HttpResponseForbidden("No permission")

    obj = get_object_or_404(BusinessCategory, pk=pk)
    obj.delete()
    return redirect('business_category_list')


# ---------- Selling Product ----------

@login_required
def selling_product_list(request):
    if not can_manage_company(request.membership):
        return HttpResponseForbidden("No permission")

    company = request.membership.company
    items = SellingProduct.objects.filter(company=company)
    form = NameForm()

    if request.method == "POST":
        form = NameForm(request.POST)
        if form.is_valid():
            SellingProduct.objects.create(
                company=company,
                name=form.cleaned_data['name']
            )
            return redirect('selling_product_list')

    return render(request, "customers/master_list.html", {
        "title": "Selling Products",
        "items": items,
        "form": form,
        "delete_url": "selling_product_delete"
    })


@login_required
def selling_product_delete(request, pk):
    if not can_manage_company(request.membership):
        return HttpResponseForbidden("No permission")

    obj = get_object_or_404(SellingProduct, pk=pk)
    obj.delete()
    return redirect('selling_product_list')
