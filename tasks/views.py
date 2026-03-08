from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Task, TaskAssignment, SalesOrder, Collection, EmployeeLocation
from customers.models import Customer
from accounts.models import Membership, EmployeeWeekend
from company.models import CompanyWeekend, CompanyHoliday

User = get_user_model()


# =====================================
# EMPLOYEE TASK DASHBOARD
# =====================================

@login_required
def my_tasks_view(request):

    assignments = TaskAssignment.objects.filter(
        employee=request.user
    ).select_related(
        "task",
        "task__customer"
    )

    return render(
        request,
        "tasks/my_tasks.html",
        {"assignments": assignments}
    )


# =====================================
# CHECK IN
# =====================================

@login_required
def check_in_view(request, assignment_id):

    assignment = get_object_or_404(
        TaskAssignment,
        id=assignment_id,
        employee=request.user
    )

    assignment.status = "checked_in"
    assignment.save()

    return redirect("my_tasks")


# =====================================
# ADD ORDER
# =====================================

@login_required
def add_order_view(request, assignment_id):

    if request.method != "POST":
        return redirect("my_tasks")

    assignment = get_object_or_404(
        TaskAssignment,
        id=assignment_id,
        employee=request.user
    )

    amount = request.POST.get("amount")

    if amount:
        SalesOrder.objects.create(
            assignment=assignment,
            amount=amount
        )

    return redirect("my_tasks")


# =====================================
# ADD COLLECTION
# =====================================

@login_required
def add_collection_view(request, assignment_id):

    if request.method != "POST":
        return redirect("my_tasks")

    assignment = get_object_or_404(
        TaskAssignment,
        id=assignment_id,
        employee=request.user
    )

    amount = request.POST.get("amount")

    if amount:
        Collection.objects.create(
            assignment=assignment,
            amount=amount
        )

    return redirect("my_tasks")


# =====================================
# LIVE EMPLOYEE MAP
# =====================================

@login_required
def live_employee_map(request):

    membership = getattr(request, "membership", None)

    if not membership:
        return redirect("dashboard")

    company = membership.company

    locations = EmployeeLocation.objects.filter(
        employee__membership__company=company
    ).select_related("employee")

    return render(
        request,
        "tasks/live_map.html",
        {"locations": locations}
    )


# =====================================
# UPDATE EMPLOYEE LOCATION
# =====================================

@login_required
def update_employee_location(request):

    lat = request.GET.get("lat")
    lng = request.GET.get("lng")

    if not lat or not lng:
        return JsonResponse({"status": "error"})

    try:
        lat = float(lat)
        lng = float(lng)
    except ValueError:
        return JsonResponse({"status": "invalid"})

    EmployeeLocation.objects.update_or_create(
        employee=request.user,
        defaults={
            "latitude": lat,
            "longitude": lng
        }
    )

    return JsonResponse({"status": "ok"})


# =====================================
# ADD TASK
# =====================================

@login_required
def task_add_view(request):

    membership = getattr(request, "membership", None)

    if not membership:
        return redirect("dashboard")

    company = membership.company

    if request.method == "POST":

        title = request.POST.get("title")
        task_type = request.POST.get("task_type")
        due_date = request.POST.get("due_date")
        repeat_type = request.POST.get("repeat_type", "none")

        customer_id = request.POST.get("customer")
        employees = request.POST.getlist("employees")

        # custom points
        custom_points = request.POST.get("custom_points")

        try:
            custom_points = float(custom_points)
        except (TypeError, ValueError):
            custom_points = None

        customer = None

        if customer_id:
            customer = get_object_or_404(
                Customer,
                id=customer_id,
                company=company
            )

        today = timezone.localdate()

        task = Task.objects.create(
            company=company,
            title=title,
            task_type=task_type,
            due_date=due_date or None,
            customer=customer,
            created_by=request.user,
            repeat_type=repeat_type,
            next_run=today if repeat_type != "none" else None
        )

        for emp_id in employees:

            employee = get_object_or_404(User, id=emp_id)

            TaskAssignment.objects.create(
                task=task,
                employee=employee,
                custom_points=custom_points,
                assignment_date=today
            )

    return redirect("task_list")


# =====================================
# TASK LIST
# =====================================

@login_required
def task_list_view(request):

    company = request.membership.company

    generate_recurring_tasks(company)

    tasks = Task.objects.filter(
        company=company
    ).select_related(
        "customer",
        "created_by"
    ).prefetch_related(
        "assignments",
        "assignments__employee"
    )

    start = request.GET.get("start")
    end = request.GET.get("end")

    if start and end:

        start_date = parse_date(start)
        end_date = parse_date(end)

        if start_date and end_date:
            tasks = tasks.filter(
                created_at__date__range=(start_date, end_date)
            )

    employees = Membership.objects.filter(
        company=company,
        role="employee"
    ).select_related("user")

    customers = Customer.objects.filter(company=company)

    assignments = TaskAssignment.objects.filter(
        task__company=company
    )

    context = {
        "tasks": tasks,
        "employees": employees,
        "customers": customers,
        "total_count": assignments.count(),
        "pending_count": assignments.filter(status="pending").count(),
        "submitted_count": assignments.filter(status="submitted").count(),
        "approved_count": assignments.filter(status="approved").count(),
    }

    return render(
        request,
        "tasks/task_list.html",
        context
    )


# =====================================
# SUBMIT TASK
# =====================================

@login_required
def submit_task(request, assignment_id):

    assignment = get_object_or_404(
        TaskAssignment,
        id=assignment_id,
        employee=request.user
    )

    assignment.submit()

    return redirect("my_tasks")


# =====================================
# APPROVE TASK
# =====================================

@login_required
def approve_task(request, assignment_id):

    company = request.membership.company

    assignment = get_object_or_404(
        TaskAssignment,
        id=assignment_id,
        task__company=company
    )

    assignment.approve(request.user)

    return redirect("task_list")


# =====================================
# EDIT TASK
# =====================================

@login_required
def task_edit_view(request, task_id):

    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":

        task.title = request.POST.get("title")
        task.task_type = request.POST.get("task_type")
        task.priority = request.POST.get("priority")
        task.due_date = request.POST.get("due_date")
        task.description = request.POST.get("description")

        task.save()

        custom_points = request.POST.get("custom_points")

        try:
            custom_points = float(custom_points)
        except (TypeError, ValueError):
            custom_points = None

        for assignment in task.assignments.all():
            assignment.custom_points = custom_points
            assignment.save()

        return redirect("task_list")

    assignment = task.assignments.first()

    return render(
        request,
        "tasks/task_edit.html",
        {
            "task": task,
            "assignment": assignment
        }
    )


# =====================================
# DELETE TASK
# =====================================

@login_required
def task_delete_view(request, task_id):

    task = get_object_or_404(Task, id=task_id)
    task.delete()

    return redirect("task_list")


# =====================================
# LEADERBOARD
# =====================================

@login_required
def leaderboard_view(request):

    company = request.membership.company

    employees = Membership.objects.filter(
        company=company,
        role="employee"
    ).select_related("user")

    assignments = TaskAssignment.objects.filter(
        task__company=company,
        status="approved"
    ).select_related("employee")

    employee_points = {}

    for a in assignments:

        emp_id = a.employee_id

        if emp_id not in employee_points:
            employee_points[emp_id] = 0

        employee_points[emp_id] += a.calculate_points()

    leaderboard = []

    for e in employees:

        leaderboard.append({
            "user": e.user,
            "points": employee_points.get(e.user.id, 0)
        })

    leaderboard.sort(
        key=lambda x: x["points"],
        reverse=True
    )

    return render(
        request,
        "tasks/leaderboard.html",
        {"leaderboard": leaderboard}
    )

# =====================================
# REJECT TASK
# =====================================

@login_required
def reject_task(request, assignment_id):

    assignment = get_object_or_404(
        TaskAssignment,
        id=assignment_id
    )

    if request.method == "POST":

        reason = request.POST.get("reject_note")

        assignment.status = "rejected"
        assignment.reject_note = reason
        assignment.save()

    return redirect("task_list")


# =====================================
# RESUBMIT TASK
# =====================================

@login_required
def resubmit_task(request, assignment_id):

    assignment = get_object_or_404(
        TaskAssignment,
        id=assignment_id
    )

    if request.method == "POST":

        note = request.POST.get("resubmit_note")
        assignment.resubmit(note)

    return redirect("task_list")


# =====================================
# GENERATE RECURRING TASKS
# =====================================

def generate_recurring_tasks(company):

    today = timezone.localdate()

    if CompanyHoliday.objects.filter(company=company, date=today).exists():
        return

    company_weekends = set(
        CompanyWeekend.objects.filter(company=company)
        .values_list("weekday", flat=True)
    )

    tasks = Task.objects.filter(
        company=company,
        repeat_type__in=["daily","weekly","15days","monthly"],
        next_run=today,
        is_active=True
    ).prefetch_related("assignments","assignments__employee")

    new_assignments = []

    for task in tasks:

        for a in task.assignments.all():

            employee = a.employee

            emp_weekends = set(
                EmployeeWeekend.objects.filter(employee=employee)
                .values_list("weekday", flat=True)
            )

            weekend_days = emp_weekends or company_weekends

            if today.weekday() in weekend_days:
                continue

            new_assignments.append(
                TaskAssignment(
                    task=task,
                    employee=employee,
                    custom_points=a.custom_points,
                    assignment_date=today
                )
            )

        if task.repeat_type == "daily":
            task.next_run = today + timedelta(days=1)

        elif task.repeat_type == "weekly":
            task.next_run = today + timedelta(days=7)

        elif task.repeat_type == "15days":
            task.next_run = today + timedelta(days=15)

        elif task.repeat_type == "monthly":
            task.next_run = today + timedelta(days=30)

        task.save(update_fields=["next_run"])

    TaskAssignment.objects.bulk_create(
        new_assignments,
        ignore_conflicts=True
    )