from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date

from .models import Task, TaskAssignment, VisitReport, SalesOrder, Collection
from customers.models import Customer
from accounts.models import Membership

from django.contrib.auth import get_user_model
User = get_user_model()


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
        {
            "assignments": assignments
        }
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

    # status change
    assignment.status = "checked_in"
    assignment.save()

    # visit report create
    VisitReport.objects.get_or_create(
        assignment=assignment
    )

    return redirect("my_tasks")

# -----------------------------
# ADD ORDER
# -----------------------------
@login_required
def add_order_view(request, assignment_id):

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
# TASK LIST (ADMIN)
# -----------------------------
@login_required
def task_list_view(request):

    company = request.membership.company

    start_date = request.GET.get("start")
    end_date = request.GET.get("end")

    tasks = Task.objects.filter(
        company=company
    ).select_related(
        "customer", "created_by"
    ).prefetch_related(
        "assignments", "assignments__employee"
    )

    if not start_date and not end_date:
        today = date.today()
        tasks = tasks.filter(assign_date=today)

    elif start_date and not end_date:
        tasks = tasks.filter(assign_date=start_date)

    elif start_date and end_date:
        tasks = tasks.filter(assign_date__range=[start_date, end_date])


    employees = Membership.objects.filter(
        company=company,
        role="employee"
    ).select_related("user")

    customers = Customer.objects.filter(company=company)


    # Assignment based counts
    assignments = TaskAssignment.objects.filter(
        task__company=company
    )

    total_count = assignments.count()

    pending_count = assignments.filter(
        status="pending"
    ).count()

    submitted_count = assignments.filter(
        status="submitted"
    ).count()

    approved_count = assignments.filter(
        status="approved"
    ).count()


    context = {
        "tasks": tasks,
        "employees": employees,
        "customers": customers,

        "total_count": total_count,
        "pending_count": pending_count,
        "submitted_count": submitted_count,
        "approved_count": approved_count,
    }

    return render(request, "tasks/task_list.html", context)
# -----------------------------
# ADD TASK (MULTI EMPLOYEE)
# -----------------------------@login_required
def task_add_view(request):

    company = request.membership.company

    if request.method == "POST":

        title = request.POST.get("title")
        task_type = request.POST.get("task_type")
        due_date = request.POST.get("due_date")

        customer_id = request.POST.get("customer")
        employees = request.POST.getlist("employees")

        # ⭐ custom points
        custom_points = request.POST.get("custom_points")

        try:
            custom_points = float(custom_points)
        except:
            custom_points = None


        customer = None
        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id)


        task = Task.objects.create(
            company=company,
            title=title,
            task_type=task_type,
            due_date=due_date or None,
            customer=customer,
            created_by=request.user
        )


        # multi employee assignment
        for emp_id in employees:

            employee = get_object_or_404(User, id=emp_id)

            TaskAssignment.objects.create(
                task=task,
                employee=employee,
                custom_points=custom_points   # ⭐ এখানে save হবে
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
def submit_task(request, assignment_id):

    assignment = get_object_or_404(
        TaskAssignment,
        id=assignment_id,
        employee=request.user
    )

    if assignment.status != "checked_in":
        return redirect("my_tasks")

    assignment.status = "submitted"
    assignment.submitted_at = timezone.now()
    assignment.save()

    return redirect("my_tasks")
# -----------------------------
# APPROVE TASK
# -----------------------------
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


# -----------------------------
# LEADERBOARD
# -----------------------------
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

        points = sum([a.calculate_points() for a in assignments])

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
        {
            "leaderboard": leaderboard
        }
    )

def calculate_points(self):

    # admin override
    if self.custom_points is not None:
        return self.custom_points

    if not self.submitted_at:
        return 0

    priority_points = {
        "low": 1,
        "medium": 1.5,
        "high": 2
    }

    base_point = priority_points.get(self.task.priority, 1)

    if not self.task.due_date:
        return base_point

    submit_date = self.submitted_at.date()

    if submit_date <= self.task.due_date:
        return base_point

    delay_days = (submit_date - self.task.due_date).days

    if delay_days == 1:
        return base_point * 0.5

    if delay_days == 2:
        return 0

    return -(delay_days - 2)