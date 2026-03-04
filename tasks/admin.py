from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "employee",
        "customer",
        "task_type",
        "due_date",
        "status"
    )