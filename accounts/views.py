from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import SignupForm, LoginForm

from django.contrib.auth.decorators import login_required


def signup_view(request):
    form = SignupForm(request.POST or None)

    if form.is_valid():
        user = form.save()
        login(request, user)

        return redirect('/company/create/')

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        user = authenticate(
            request,
            email=form.data.get('email'),
            password=form.data.get('password')
        )
        if user:
            login(request, user)
            return redirect('/dashboard/')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')
