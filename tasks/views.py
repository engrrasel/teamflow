from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Task, TaskAssignment, SalesOrder, Collection, EmployeeLocation
from customers.models import Customer
from accounts.models import Membership

from django.contrib.auth import get_user_model
User = get_user_model()

from django.utils import timezone

# -----------------------------
# MY TASKS (EMPLOYEE DASHBOARD)
# -----------------------------
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


# -----------------------------
# CHECK-IN
# -----------------------------
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


# -----------------------------
# ADD ORDER
# -----------------------------
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


# -----------------------------
# ADD COLLECTION
# -----------------------------
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


# -----------------------------
# LIVE EMPLOYEE MAP
# -----------------------------
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


# -----------------------------
# UPDATE EMPLOYEE LOCATION
# -----------------------------
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

        customer_id = request.POST.get("customer")
        employees = request.POST.getlist("employees")

        # -------- CUSTOM POINTS --------
        custom_points = request.POST.get("custom_points")

        try:
            custom_points = float(custom_points)
        except (TypeError, ValueError):
            custom_points = None
        # --------------------------------

        customer = None

        if customer_id:
            customer = get_object_or_404(
                Customer,
                id=customer_id,
                company=company
            )

        # -------- CREATE TASK --------
        task = Task.objects.create(
            company=company,
            title=title,
            task_type=task_type,
            due_date=due_date or None,
            customer=customer,
            created_by=request.user
        )

        # -------- ASSIGN EMPLOYEES --------
        for emp_id in employees:

            employee = get_object_or_404(User, id=emp_id)

            TaskAssignment.objects.create(
                task=task,
                employee=employee,
                custom_points=custom_points
            )

    return redirect("task_list")


@login_required
def task_list_view(request):

    company = request.membership.company

    tasks = Task.objects.filter(
        company=company
    ).select_related(
        "customer",
        "created_by"
    ).prefetch_related(
        "assignments",
        "assignments__employee"
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

    return render(request, "tasks/task_list.html", context)


@login_required
def submit_task(request, assignment_id):

    assignment = get_object_or_404(
        TaskAssignment,
        id=assignment_id,
        employee=request.user
    )

    assignment.submit()

    return redirect("my_tasks")

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

from django.utils import timezone

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

        # -------- CUSTOM POINTS UPDATE --------
        custom_points = request.POST.get("custom_points")

        try:
            custom_points = float(custom_points)
        except (TypeError, ValueError):
            custom_points = None

        for assignment in task.assignments.all():
            assignment.custom_points = custom_points
            assignment.save()
        # --------------------------------------

        return redirect("task_list")

    # প্রথম assignment থেকে point দেখানোর জন্য
    assignment = task.assignments.first()

    return render(
        request,
        "tasks/task_edit.html",
        {
            "task": task,
            "assignment": assignment
        }
    )
@login_required
def task_delete_view(request, task_id):

    task = get_object_or_404(Task, id=task_id)

    task.delete()

    return redirect("task_list")


@login_required
def leaderboard_view(request):

    company = request.membership.company

    employees = Membership.objects.filter(
        company=company,
        role="employee"
    ).select_related("user")

    leaderboard = []

    for e in employees:

        assignments = TaskAssignment.objects.filter(
            task__company=company,
            employee=e.user,
            status="approved"
        )

        points = sum(a.calculate_points() for a in assignments)

        leaderboard.append({
            "user": e.user,
            "points": points
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



@login_required
def reject_task(request, assignment_id):

    assignment = get_object_or_404(
        TaskAssignment,
        id=assignment_id
    )

    note = request.POST.get("reject_note")

    assignment.reject(request.user, note)

    return redirect("task_list")


from django.utils import timezone

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