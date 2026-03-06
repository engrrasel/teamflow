from django.contrib import admin
from .models import Task, TaskAssignment, SalesOrder, Collection, EmployeeLocation


# -----------------------------
# TASK ADMIN
# -----------------------------
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "company",
        "task_type",
        "priority",
        "due_date",
        "created_by",
        "created_at",
    )

    list_filter = (
        "task_type",
        "priority",
        "company",
    )

    search_fields = (
        "title",
    )


# -----------------------------
# TASK ASSIGNMENT ADMIN
# -----------------------------
@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "task",
        "employee",
        "status",
        "submitted_at",
        "approved_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "task__title",
        "employee__username",
    )


# -----------------------------
# SALES ORDER
# -----------------------------
@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):

    list_display = (
        "assignment",
        "amount",
        "created_at",
    )


# -----------------------------
# COLLECTION
# -----------------------------
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):

    list_display = (
        "assignment",
        "amount",
        "created_at",
    )


# -----------------------------
# EMPLOYEE LOCATION (LIVE GPS)
# -----------------------------
@admin.register(EmployeeLocation)
class EmployeeLocationAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "latitude",
        "longitude",
        "updated_at",
    )

    search_fields = (
        "employee__username",
    )