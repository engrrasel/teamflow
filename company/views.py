from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CompanyCreateForm
from accounts.models import Membership


@login_required
def create_company_view(request):

    # 🔥 যদি user আগে থেকেই কোনো company এর member হয়
    existing = Membership.objects.filter(user=request.user).first()
    if existing:
        request.session['company_id'] = existing.company.id
        return redirect('/dashboard/')

    if request.method == 'POST':
        form = CompanyCreateForm(request.POST)
        if form.is_valid():
            company = form.save()

            # membership তৈরি (company_admin)
            Membership.objects.create(
                user=request.user,
                company=company,
                role='company_admin'
            )

            request.session['company_id'] = company.id
            return redirect('/dashboard/')
    else:
        form = CompanyCreateForm()

    return render(request, 'company/create_company.html', {'form': form})
