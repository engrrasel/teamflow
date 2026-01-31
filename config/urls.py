from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from accounts.views import dashboard_view

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    path('company/', include('company.urls')),

    path('dashboard/', dashboard_view, name='dashboard'),

    # Accounts (Login, Signup, Logout)
    path('accounts/', include('accounts.urls')),

    # Password Reset (Forgot Password)
    path(
        'accounts/password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html'
        ),
        name='password_reset'
    ),
    path(
        'accounts/password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'accounts/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'accounts/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
