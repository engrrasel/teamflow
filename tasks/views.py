from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from django.utils import timezone

from django.db.models import Sum, Q, Value
from django.db.models.functions import Coalesce

from .models import Task, VisitReport, SalesOrder, Collection
from customers.models import Customer
from accounts.models import Membership

from django.db.models import Sum, Q, Value, FloatField
from django.db.models.functions import Coalesce

# -----------------------------
# MY TASKS
# -----------------------------
@login_required
def my_tasks_view(request):

    tasks = Task.objects.filter(
        employee=request.user,
        due_date=date.today()
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

    task.status = "checked_in"
    task.save()

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

    tasks = Task.objects.filter(company=company)

    employees = Membership.objects.filter(
        company=company,
        role="employee"
    )

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

        employee_id = request.POST.get("employee")
        customer_id = request.POST.get("customer")
        title = request.POST.get("title")
        task_type = request.POST.get("task_type")
        due_date = request.POST.get("due_date")

        if not employee_id:
            employee_id = request.user.id

        Task.objects.create(
            company=company,
            employee_id=employee_id,
            customer_id=customer_id or None,
            title=title,
            task_type=task_type,
            due_date=due_date,
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

    return render(request, "tasks/task_edit.html", {"task": task})


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

    task.points = task.calculate_points()
    task.status = "approved"

    task.save()

    return redirect("task_list")


# -----------------------------
# LEADERBOARD
#@login_required
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
    quarterly = []
    yearly = []

    for e in employees:

        tasks = Task.objects.filter(
            company=company,
            employee=e.user,
            status="approved"
        )

        # Daily
        daily_points = tasks.filter(
            submitted_at__date=today
        ).aggregate(Sum("points"))["points__sum"] or 0

        # Weekly
        weekly_points = tasks.filter(
            submitted_at__date__gte=today - timedelta(days=7)
        ).aggregate(Sum("points"))["points__sum"] or 0

        # Monthly
        monthly_points = tasks.filter(
            submitted_at__date__month=today.month
        ).aggregate(Sum("points"))["points__sum"] or 0

        # Quarterly
        quarter_start_month = ((today.month - 1) // 3) * 3 + 1
        quarterly_points = tasks.filter(
            submitted_at__date__month__gte=quarter_start_month
        ).aggregate(Sum("points"))["points__sum"] or 0

        # Yearly
        yearly_points = tasks.filter(
            submitted_at__date__year=today.year
        ).aggregate(Sum("points"))["points__sum"] or 0

        daily.append({"user": e.user, "points": daily_points})
        weekly.append({"user": e.user, "points": weekly_points})
        monthly.append({"user": e.user, "points": monthly_points})
        quarterly.append({"user": e.user, "points": quarterly_points})
        yearly.append({"user": e.user, "points": yearly_points})

    daily.sort(key=lambda x: x["points"], reverse=True)
    weekly.sort(key=lambda x: x["points"], reverse=True)
    monthly.sort(key=lambda x: x["points"], reverse=True)
    quarterly.sort(key=lambda x: x["points"], reverse=True)
    yearly.sort(key=lambda x: x["points"], reverse=True)

    return render(
        request,
        "tasks/leaderboard.html",
        {
            "daily": daily,
            "weekly": weekly,
            "monthly": monthly,
            "quarterly": quarterly,
            "yearly": yearly,
        }
    )