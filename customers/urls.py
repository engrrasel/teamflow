from django.urls import path
from .views import customer_list_view, customer_add_view
from .views_master import (
    business_category_list,
    business_category_delete,
    selling_product_list,
    selling_product_delete,
)

urlpatterns = [
    # ---------- Customers ----------
    path("", customer_list_view, name="customer_list"),
    path("add/", customer_add_view, name="customer_add"),

    # ---------- Business Categories ----------
    path(
        "business-categories/",
        business_category_list,
        name="business_category_list",
    ),
    path(
        "business-categories/delete/<int:pk>/",
        business_category_delete,
        name="business_category_delete",
    ),

    # ---------- Selling Products ----------
    path(
        "selling-products/",
        selling_product_list,
        name="selling_product_list",
    ),
    path(
        "selling-products/delete/<int:pk>/",
        selling_product_delete,
        name="selling_product_delete",
    ),
]
