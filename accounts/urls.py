from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    path("employees/", views.employee_list_view, name="employee_list"),
    path("employees/add/", views.employee_create_view, name="employee_add"),
    path('force-password-change/', views.force_password_change_view, name='force_password_change'),
    path('invite/', views.invite_employee_view, name='invite_employee'),
]
