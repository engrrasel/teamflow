from datetime import timedelta

from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib import messages


from django.views.decorators.http import require_POST
from .models import TaskActionNote
from .models import Task, TaskAssignment, SalesOrder, Collection, EmployeeLocation
from customers.models import Customer
from accounts.models import Membership, EmployeeWeekend
from company.models import CompanyWeekend, CompanyHoliday

User = get_user_model()


# =====================================
# ADMIN PERMISSION HELPER
# =====================================

def admin_required(request):

    membership = getattr(request, "membership", None)

    if not membership:
        return HttpResponseForbidden("No membership")

    role = str(membership.role).lower()

    if role not in ["company_admin"]:
        return HttpResponseForbidden("Admin only")

    return None

# =====================================
# EMPLOYEE TASK DASHBOARD
# =====================================

@login_required
def my_tasks_view(request):

    today = timezone.localdate()

    # 🔥 Base queryset (optimized + latest first)
    base_qs = TaskAssignment.objects.select_related(
        "task",
        "task__customer"
    ).filter(
        employee=request.user
    ).order_by("-id")   # ✅ সব জায়গায় latest first

    # ✅ Today Tasks (latest first)
    today_tasks = base_qs.filter(
        assignment_date=today
    )

    # ✅ Ongoing Tasks
    ongoing_tasks = base_qs.filter(
        status__in=["pending", "checked_in", "submitted"]
    ).exclude(
        assignment_date=today
    )

    # ✅ History Tasks
    history_tasks = base_qs.filter(
        status__in=["approved", "rejected"]
    )

    return render(
        request,
        "tasks/my_tasks.html",
        {
            "today_tasks": today_tasks,
            "ongoing_tasks": ongoing_tasks,
            "history_tasks": history_tasks,
        }
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
    check = admin_required(request)
    if check:
        return check

    membership = getattr(request, "membership", None)

    if not membership:
        return redirect("dashboard")

    company = membership.company

    if request.method == "POST":

        title = request.POST.get("title")
        description = request.POST.get("description")
        task_type = request.POST.get("task_type")

        due_date_str = request.POST.get("due_date")
        due_date = parse_date(due_date_str) if due_date_str else None

        repeat_type = request.POST.get("repeat_type", "none")

        customer_id = request.POST.get("customer")
        employee_ids = request.POST.getlist("employees")

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

        with transaction.atomic():

            task = Task.objects.create(
                company=company,
                title=title,
                description=description,
                task_type=task_type,
                due_date=due_date,
                customer=customer,
                created_by=request.user,
                repeat_type=repeat_type,
                next_run=today if repeat_type != "none" else None
            )

            assignments = []

            for emp_id in employee_ids:

                employee = get_object_or_404(
                    User,
                    id=emp_id,
                    membership__company=company
                )

                assignments.append(
                    TaskAssignment(
                        task=task,
                        employee=employee,
                        custom_points=custom_points,
                        assignment_date=today
                    )
                )

            TaskAssignment.objects.bulk_create(assignments)

        return redirect("task_list")

    employees = Membership.objects.filter(
        company=company,
        role="employee"
    ).select_related("user")

    customers = Customer.objects.filter(
        company=company
    )

    return render(
        request,
        "tasks/task_add.html",
        {
            "employees": employees,
            "customers": customers
        }
    )

# =====================================
# TASK LIST
# =====================================
@login_required
def task_list_view(request):

    membership = request.membership

    # employee হলে My Tasks এ পাঠাও
    if membership.role == "employee":
        return redirect("my_tasks")

    # admin হলে normal task list
    company = membership.company

    generate_recurring_tasks(company)

    tasks = Task.objects.filter(
        company=company
    ).select_related(
        "customer",
        "created_by"
    ).prefetch_related(
        "assignments",
        "assignments__employee"
    ).order_by('-id') 

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

    check = admin_required(request)
    if check:
        return check

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
    check = admin_required(request)
    if check:
        return check

    task = get_object_or_404(
        Task,
        id=task_id,
        company=request.membership.company
    )

    if request.method == "POST":

        title = request.POST.get("title")
        task_type = request.POST.get("task_type")
        priority = request.POST.get("priority")
        description = request.POST.get("description")

        due_date_str = request.POST.get("due_date")
        due_date = parse_date(due_date_str) if due_date_str else None

        task.title = title
        task.task_type = task_type
        task.priority = priority
        task.description = description
        task.due_date = due_date

        task.save(update_fields=[
            "title",
            "task_type",
            "priority",
            "description",
            "due_date"
        ])

        custom_points = request.POST.get("custom_points")

        try:
            custom_points = float(custom_points)
        except (TypeError, ValueError):
            custom_points = None

        for assignment in task.assignments.all():
            assignment.custom_points = custom_points
            assignment.save(update_fields=["custom_points"])

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

    check = admin_required(request)
    if check:
        return check

    task = get_object_or_404(
        Task,
        id=task_id,
        company=request.membership.company
    )

    # 🔥 FULL DELETE (correct way)
    task.delete()

    return redirect("scheduled_tasks")


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

        # IMPORTANT FIX
        employee_points[emp_id] += a.calculate_points

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

    # same data for now (daily/weekly/monthly later filter করা যাবে)
    context = {
        "daily": leaderboard,
        "weekly": leaderboard,
        "monthly": leaderboard,
        "quarterly": leaderboard,
        "yearly": leaderboard,
    }

    return render(
        request,
        "tasks/leaderboard.html",
        context
    )
# =====================================
# REJECT TASK
# =====================================

@login_required
def reject_task(request, assignment_id):

    check = admin_required(request)
    if check:
        return check

    assignment = get_object_or_404(
        TaskAssignment,
        id=assignment_id,
        task__company=request.membership.company
    )

    if request.method == "POST":

        reason = request.POST.get("reject_note")

        success = assignment.reject(request.user, reason)

        if success:
            TaskActionNote.objects.create(
                assignment=assignment,
                note_type="reject",
                note=reason,
                created_by=request.user
            )
        else:
            print("❌ Reject failed. Status:", assignment.status)

    return redirect("task_detail", assignment.task.id)

    
# =====================================
# GENERATE RECURRING TASKS
# =====================================

def generate_recurring_tasks(company):

    today = timezone.localdate()

    # company weekends
    company_weekends = set(
        CompanyWeekend.objects.filter(company=company)
        .values_list("weekday", flat=True)
    )

    # employee weekend map
    employee_weekends = {}

    for ew in EmployeeWeekend.objects.filter(
        employee__membership__company=company
    ):
        employee_weekends.setdefault(
            ew.employee_id, set()
        ).add(ew.weekday)

    # holiday set
    holiday_dates = set()

    for h in CompanyHoliday.objects.filter(company=company):
        current = h.start_date
        while current <= h.end_date:
            holiday_dates.add(current)
            current += timedelta(days=1)

    # existing assignments (duplicate protection)
    existing_runs = set(
        TaskAssignment.objects.filter(
            task__company=company
        ).values_list("task_id", "employee_id", "assignment_date")
    )

    tasks = Task.objects.filter(
        company=company,
        repeat_type__in=["daily", "weekly", "15days", "monthly"],
        is_active=True
    ).prefetch_related("assignments", "assignments__employee")

    new_assignments = []

    for task in tasks:

        # 🔥 IMPORTANT: run_date start
        run_date = task.next_run or today

        assignments_template = list(task.assignments.all())

        # 🔁 loop until today (missed recovery)
        while run_date <= today:

            # ❌ skip holiday globally
            if run_date in holiday_dates:
                run_date += timedelta(days=1)
                continue

            for a in assignments_template:

                employee = a.employee

                # employee-specific weekend
                weekend_days = employee_weekends.get(
                    employee.id,
                    company_weekends
                )

                # ❌ skip only this employee
                if run_date.weekday() in weekend_days:
                    continue

                # ❌ duplicate protection
                if (task.id, employee.id, run_date) in existing_runs:
                    continue

                new_assignments.append(
                    TaskAssignment(
                        task=task,
                        employee=employee,
                        custom_points=a.custom_points,
                        assignment_date=run_date
                    )
                )

            # 🔁 next run increment (only logic, no bug)
            if task.repeat_type == "daily":
                run_date += timedelta(days=1)

            elif task.repeat_type == "weekly":
                run_date += timedelta(days=7)

            elif task.repeat_type == "15days":
                run_date += timedelta(days=15)

            elif task.repeat_type == "monthly":
                run_date += timedelta(days=30)

        # ✅ FIX: next_run set correctly (NO GLOBAL BUG)
        task.next_run = run_date

    # bulk update
    Task.objects.bulk_update(tasks, ["next_run"])

    # bulk create
    TaskAssignment.objects.bulk_create(
        new_assignments,
        ignore_conflicts=True
    )
    
# =====================================
# scheduled tasks view
# =====================================
@login_required
def scheduled_tasks_view(request):
    check = admin_required(request)
    if check:
        return check

    company = request.membership.company

    tasks = Task.objects.filter(
        company=company,
        repeat_type__in=["daily", "weekly", "15days", "monthly"],
    ).select_related("customer", "created_by")

    return render(
        request,
        "tasks/scheduled_tasks.html",
        {"tasks": tasks}
    )


@login_required
def task_detail_view(request, task_id):

    company = request.membership.company

    task = get_object_or_404(
        Task.objects.select_related("customer", "created_by"),
        id=task_id,
        company=company
    )

    # 🔥 employee filter param (admin use করবে)
    employee_id = request.GET.get("employee")

    # 🔥 base queryset
    assignments = TaskAssignment.objects.filter(
        task=task
    ).select_related("employee")

    # 🔥 employee role হলে নিজেরটা দেখবে
    if request.membership.role == "employee":
        assignments = assignments.filter(employee=request.user)

    # 🔥 admin filter (optional)
    elif employee_id:
        assignments = assignments.filter(employee_id=employee_id)

    # 🔥 dropdown এর জন্য employees list
    employees = Membership.objects.filter(
        company=company,
        role="employee"
    ).select_related("user")

    return render(
        request,
        "tasks/task_detail.html",
        {
            "task": task,
            "assignments": assignments,
            "employees": employees
        }
    )

@login_required
def task_toggle(request, task_id):

    check = admin_required(request)
    if check:
        return check

    task = get_object_or_404(Task, id=task_id)

    task.is_active = not task.is_active
    task.save(update_fields=["is_active"])

    return redirect("scheduled_tasks")



@login_required
def scheduled_task_detail(request, task_id):

    check = admin_required(request)
    if check:
        return check

    task = get_object_or_404(Task, id=task_id)

    assignments = (
        task.assignments
        .select_related("employee")
        .order_by("-assignment_date")
    )

    run_dates = (
        task.assignments
        .values_list("created_at", flat=True)
        .order_by("-created_at")
    )

    # 🔥 ADD THIS
    skip_reasons = get_task_skip_reason(task)

    return render(
        request,
        "tasks/scheduled_task_detail.html",
        {
            "task": task,
            "assignments": assignments,
            "run_dates": run_dates,
            "skip_reasons": skip_reasons
        }
    )

@login_required
def assignment_delete_view(request, assignment_id):

    check = admin_required(request)
    if check:
        return check

    assignment = get_object_or_404(
        TaskAssignment,
        id=assignment_id,
        task__company=request.membership.company
    )

    assignment.delete()

    return redirect("task_list")


@login_required
def assignment_edit_view(request, assignment_id):

    check = admin_required(request)
    if check:
        return check

    assignment = get_object_or_404(
        TaskAssignment,
        id=assignment_id,
        task__company=request.membership.company
    )

    if request.method == "POST":

        assignment.title_override = request.POST.get("title") or None
        assignment.description_override = request.POST.get("description") or None
        assignment.task_type_override = request.POST.get("task_type") or None
        assignment.priority_override = request.POST.get("priority") or None

        due_date = request.POST.get("due_date")
        assignment.due_date_override = parse_date(due_date) if due_date else None

        custom_points = request.POST.get("custom_points")

        try:
            assignment.custom_points = float(custom_points)
        except:
            assignment.custom_points = None

        assignment.save()

        return redirect("task_list")

    return render(
        request,
        "tasks/task_edit.html",
        {
            "assignment": assignment,
            "task": assignment.task
        }
    )

@login_required
def assignment_detail_view(request, assignment_id):

    assignment = get_object_or_404(
        TaskAssignment.objects.select_related(
            "task",
            "employee",
            "task__customer",
            "task__created_by"
        ).prefetch_related(
            "notes",
            "notes__created_by"
        ),
        id=assignment_id,
        task__company=request.membership.company
    )

    user = request.user
    is_employee = user == assignment.employee
    is_admin = request.membership.role == "company_admin"

    # =========================
    # 🔒 CHECK-IN REQUIRED
    # =========================
    if is_employee and not assignment.checked_in_at:
        messages.warning(request, "Please check in first.")
        return redirect("my_tasks")

    # =========================
    # POST HANDLING
    # =========================
    if request.method == "POST":

        note = request.POST.get("note", "").strip()
        action = request.POST.get("action") or "message"

        # =========================
        # 👤 EMPLOYEE ACTION
        # =========================
        if is_employee:

            # 💬 message
            if note:
                TaskActionNote.objects.create(
                    assignment=assignment,
                    note=note,
                    created_by=user,
                    note_type="comment"
                )

            # 📤 submit
            if action == "submit":
                success = assignment.submit()

                if not success:
                    messages.warning(request, "Task cannot be submitted in current state.")

        # =========================
        # 🧑‍💼 ADMIN ACTION
        # =========================
        elif is_admin:

            # ✅ APPROVE
            if action == "approve":

                if note:
                    TaskActionNote.objects.create(
                        assignment=assignment,
                        note=note,
                        created_by=user,
                        note_type="comment"
                    )

                assignment.approve(user)

            # ❌ REJECT
            elif action == "reject":

                if not note:
                    messages.error(request, "Reject note is required.")
                    return redirect("assignment_detail", assignment.id)

                assignment.reject(user, note)

                TaskActionNote.objects.create(
                    assignment=assignment,
                    note=note,
                    created_by=user,
                    note_type="reject"
                )

            # 💬 NORMAL MESSAGE
            else:

                if note:
                    TaskActionNote.objects.create(
                        assignment=assignment,
                        note=note,
                        created_by=user,
                        note_type="comment"
                    )

        return redirect("assignment_detail", assignment.id)

    # =========================
    # RENDER
    # =========================
    return render(
        request,
        "tasks/assignment_detail.html",
        {
            "assignment": assignment
        }
    )



@login_required
def employee_locations_api(request):

    company = request.membership.company

    locations = EmployeeLocation.objects.filter(
        employee__membership__company=company
    ).select_related("employee")

    data = []

    for loc in locations:
        data.append({
            "name": loc.employee.username,
            "lat": loc.latitude,
            "lng": loc.longitude,
        })

    return JsonResponse(data, safe=False)


def get_task_skip_reason(task):

    today = timezone.localdate()
    reasons = []

    # 1️⃣ Next run check
    if task.next_run and task.next_run > today:
        reasons.append(f"Next run scheduled on {task.next_run}")

    # 2️⃣ Holiday check
    if CompanyHoliday.objects.filter(
        company=task.company,
        start_date__lte=today,
        end_date__gte=today
    ).exists():
        reasons.append("Today is holiday")

    # 3️⃣ Weekend check
    company_weekends = CompanyWeekend.objects.filter(
        company=task.company,
        weekday=today.weekday()
    )

    if company_weekends.exists():
        reasons.append("Today is company weekend")

    # 4️⃣ Already generated check
    if TaskAssignment.objects.filter(
        task=task,
        assignment_date=today
    ).exists():
        reasons.append("Task already generated today")

    # 5️⃣ IMPORTANT: missed run detect 🔥
    if task.next_run and task.next_run < today:
        reasons.append(f"Missed run (last should run on {task.next_run})")

    return reasons


@login_required
@require_POST
def check_in_assignment(request, assignment_id):
    assignment = get_object_or_404(
        TaskAssignment,
        id=assignment_id,
        employee=request.user  # 🔥 security: নিজের assignment ছাড়া কেউ check-in করতে পারবে না
    )

    # Already checked ইন?
    if assignment.checked_in_at:
        return JsonResponse({
            "status": "already",
            "time": assignment.checked_in_at.strftime("%I:%M %p")
        })

    lat = request.POST.get("lat")
    lng = request.POST.get("lng")

    # Optional: validation
    if not lat or not lng:
        return JsonResponse({"status": "error", "message": "Location required"})

    # Save
    assignment.checked_in_at = timezone.now()
    assignment.checkin_lat = float(lat)
    assignment.checkin_lng = float(lng)
    assignment.status = "checked_in"
    assignment.save(update_fields=[
        "checked_in_at",
        "checkin_lat",
        "checkin_lng",
        "status"
    ])

    return JsonResponse({
        "status": "success",
        "time": assignment.checked_in_at.strftime("%I:%M %p")
    })