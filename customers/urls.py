from django.urls import path
from .views import customer_list_view, customer_add_view

urlpatterns = [
    path("", customer_list_view, name="customer_list"),
    path("add/", customer_add_view, name="customer_add"),
]
