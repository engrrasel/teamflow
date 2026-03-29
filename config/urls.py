from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from accounts.views import dashboard_view


urlpatterns = [
    # ================= ADMIN =================
    path('admin/', admin.site.urls),

    # ================= COMPANY =================
    path('company/', include('company.urls')),

    # ================= LOCATIONS (🔥 FIXED) =================
    # NOTE: আগে '' ছিল → এখন clean prefix
    path('locations/', include('locations.urls')),

    # ================= CUSTOMERS =================
    path('customers/', include('customers.urls')),

    # ================= TASKS =================
    path('tasks/', include('tasks.urls')),

    # ================= DASHBOARD =================
    path('dashboard/', dashboard_view, name='dashboard'),

    # ================= ACCOUNTS =================
    path('accounts/', include('accounts.urls')),

    # ================= PASSWORD RESET =================
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