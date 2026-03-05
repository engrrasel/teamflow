from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date, timedelta

from .models import Task, VisitReport, SalesOrder, Collection
from customers.models import Customer
from accounts.models import Membership

from django.contrib.auth import get_user_model
User = get_user_model()


# -----------------------------
# MY TASKS
# -----------------------------
@login_required
def my_tasks_view(request):

    tasks = Task.objects.filter(
        employee=request.user
    ).select_related("customer")

    return render(
        request,
        "tasks/my_tasks.html",
        {"tasks": tasks}
    )


# -----------------------------
# CHECK-IN
# -----------------------------
@login_required
def check_in_view(request, task_id):

    task = get_object_or_404(
        Task,
        id=task_id,
        employee=request.user
    )

    # status change
    task.status = "checked_in"
    task.save()

    # visit report create
    VisitReport.objects.get_or_create(task=task)

    return redirect("my_tasks")

# -----------------------------
# ADD ORDER
# -----------------------------
@login_required
def add_order_view(request, task_id):

    task = get_object_or_404(
        Task,
        id=task_id,
        employee=request.user
    )

    amount = request.POST.get("amount")

    if amount:
        SalesOrder.objects.create(
            task=task,
            amount=amount
        )

    return redirect("my_tasks")


# -----------------------------
# ADD COLLECTION
# -----------------------------
@login_required
def add_collection_view(request, task_id):

    task = get_object_or_404(
        Task,
        id=task_id,
        employee=request.user
    )

    amount = request.POST.get("amount")

    if amount:
        Collection.objects.create(
            task=task,
            amount=amount
        )

    return redirect("my_tasks")


# -----------------------------
# TASK LIST (ADMIN)
# -----------------------------
@login_required
def task_list_view(request):

    company = request.membership.company

    tasks = Task.objects.filter(
        company=company
    ).select_related("employee", "customer")

    employees = Membership.objects.filter(
        company=company,
        role="employee"
    ).select_related("user")

    customers = Customer.objects.filter(company=company)

    return render(
        request,
        "tasks/task_list.html",
        {
            "tasks": tasks,
            "employees": employees,
            "customers": customers
        }
    )


# -----------------------------
# ADD TASK
# -----------------------------
@login_required
def task_add_view(request):

    company = request.membership.company

    if request.method == "POST":

        title = request.POST.get("title")
        task_type = request.POST.get("task_type")
        due_date = request.POST.get("due_date")
        employee_id = request.POST.get("employee")
        customer_id = request.POST.get("customer")
        custom_points = request.POST.get("custom_points") or 1

        # employee fallback
        if employee_id:
            employee = get_object_or_404(User, id=employee_id)
        else:
            employee = request.user

        # customer optional
        customer = None
        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id)

        Task.objects.create(
            company=company,
            employee=employee,
            customer=customer,
            title=title,
            task_type=task_type,
            due_date=due_date or None,
            custom_points=custom_points,
            created_by=request.user
        )

    return redirect("task_list")


# -----------------------------
# EDIT TASK
# -----------------------------
@login_required
def task_edit_view(request, task_id):

    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":

        task.title = request.POST.get("title")
        task.task_type = request.POST.get("task_type")
        task.due_date = request.POST.get("due_date")

        task.save()

        return redirect("task_list")

    return render(
        request,
        "tasks/task_edit.html",
        {"task": task}
    )


# -----------------------------
# DELETE TASK
# -----------------------------
@login_required
def task_delete_view(request, task_id):

    task = get_object_or_404(Task, id=task_id)

    task.delete()

    return redirect("task_list")


# -----------------------------
# SUBMIT TASK
# -----------------------------
@login_required
def submit_task(request, task_id):

    task = get_object_or_404(
        Task,
        id=task_id,
        employee=request.user
    )

    task.status = "submitted"
    task.submitted_at = timezone.now()

    task.save()

    return redirect("my_tasks")


# -----------------------------
# APPROVE TASK
# -----------------------------
@login_required
def approve_task(request, task_id):

    company = request.membership.company

    task = get_object_or_404(
        Task,
        id=task_id,
        company=company
    )

    task.status = "approved"
    task.save()

    return redirect("task_list")


# -----------------------------
# LEADERBOARD
# -----------------------------
@login_required
def leaderboard_view(request):

    company = request.membership.company
    today = timezone.now().date()

    employees = Membership.objects.filter(
        company=company,
        role="employee"
    ).select_related("user")

    daily = []
    weekly = []
    monthly = []
    yearly = []

    for e in employees:

        tasks = Task.objects.filter(
            company=company,
            employee=e.user,
            status="approved"
        )

        points = sum([t.calculate_points() for t in tasks])

        daily.append({"user": e.user, "points": points})

    daily.sort(key=lambda x: x["points"], reverse=True)

    return render(
        request,
        "tasks/leaderboard.html",
        {
            "daily": daily
        }
    )