from django.urls import path
from .views import create_company_view

urlpatterns = [
    path('create/', create_company_view, name='create_company'),
]
