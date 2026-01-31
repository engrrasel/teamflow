from django.urls import path
from . import views

urlpatterns = [
    # Company
    path('create/', views.create_company_view, name='create_company'),

    # Designation CRUD
    path('designations/', views.designation_list_view, name='designation_list'),
    path('designations/add/', views.designation_create_view, name='designation_add'),
    path('designations/<int:pk>/edit/', views.designation_edit_view, name='designation_edit'),
    path('designations/<int:pk>/delete/', views.designation_delete_view, name='designation_delete'),

    # AJAX designation create
    path('ajax/designation/create/', views.create_designation_ajax, name='designation_ajax_create'),


    path('groups/<int:pk>/edit/', views.group_edit_view, name='group_edit'),
    path('groups/<int:pk>/delete/', views.group_delete_view, name='group_delete'),

    # Groups
    path('groups/', views.group_list_view, name='group_list'),
    path('groups/add/', views.group_create_view, name='group_add'),
]
