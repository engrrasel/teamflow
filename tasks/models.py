from django.db import models
from django.conf import settings
from django.utils import timezone


# =========================================
# TASK (MASTER TASK)
# =========================================
class Task(models.Model):

    TASK_TYPE = (
        ("visit", "Visit"),
        ("desk", "Desk Work"),
        ("call", "Call"),
        ("meeting", "Meeting"),
        ("collection", "Collection"),
    )

    PRIORITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    )

    REPEAT_CHOICES = (
        ("none", "One Time"),
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("15days", "Every 15 Days"),
        ("monthly", "Monthly"),
    )

    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField(max_length=200)

    task_type = models.CharField(max_length=20, choices=TASK_TYPE, default="desk")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")

    customer = models.ForeignKey("customers.Customer", on_delete=models.SET_NULL, null=True, blank=True)

    description = models.TextField(blank=True)

    # ❗ শুধু one-time task এর জন্য
    due_date = models.DateField(null=True, blank=True)

    # 🔥 NEW (MOST IMPORTANT)
    duration_days = models.IntegerField(default=1)

    repeat_type = models.CharField(max_length=20, choices=REPEAT_CHOICES, default="none")

    next_run = models.DateField(null=True, blank=True)

    assign_time = models.TimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# =========================================
# TASK ASSIGNMENT
# =========================================
from datetime import timedelta
from django.utils import timezone

class TaskAssignment(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("checked_in", "Checked In"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="task_assignments"
    )

    assignment_date = models.DateField(db_index=True)

    # 🔥 NEW (DYNAMIC DEADLINE)
    due_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True
    )

    submitted_at = models.DateTimeField(null=True, blank=True)

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_assignments"
    )

    approved_at = models.DateTimeField(null=True, blank=True)

    # ===============================
    # CHECK-IN TRACKING
    # ===============================

    checked_in_at = models.DateTimeField(null=True, blank=True)
    checkin_lat = models.FloatField(null=True, blank=True)
    checkin_lng = models.FloatField(null=True, blank=True)

    # ===============================
    # OVERRIDE FIELDS
    # ===============================

    title_override = models.CharField(max_length=200, null=True, blank=True)
    description_override = models.TextField(null=True, blank=True)

    task_type_override = models.CharField(
        max_length=20,
        choices=Task.TASK_TYPE,
        null=True,
        blank=True
    )

    priority_override = models.CharField(
        max_length=10,
        choices=Task.PRIORITY_CHOICES,
        null=True,
        blank=True
    )

    due_date_override = models.DateField(null=True, blank=True)

    # ===============================
    # POINTS
    # ===============================

    custom_points = models.FloatField(null=True, blank=True)

    # ===============================
    # NOTES
    # ===============================

    reject_note = models.TextField(blank=True, null=True)
    resubmit_note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # ===============================
    # CONSTRAINTS & INDEXES
    # ===============================

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["task", "employee", "assignment_date"],
                name="unique_task_employee_date"
            )
        ]

        indexes = [
            models.Index(fields=["employee", "assignment_date"]),
            models.Index(fields=["task", "assignment_date"]),
            models.Index(fields=["status", "assignment_date"]),
        ]

        ordering = ["-assignment_date", "-created_at"]

    # ===============================
    # 🔥 AUTO DEADLINE (MAIN FIX)
    # ===============================

    def save(self, *args, **kwargs):

        if self.assignment_date and self.task.duration_days:
            self.due_date = self.assignment_date + timedelta(days=self.task.duration_days - 1)

        super().save(*args, **kwargs)

    # ===============================
    # DISPLAY HELPERS
    # ===============================

    @property
    def title(self):
        return self.title_override or self.task.title

    @property
    def description(self):
        return self.description_override or self.task.description

    @property
    def task_type_value(self):
        return self.task_type_override or self.task.task_type

    @property
    def priority_value(self):
        return self.priority_override or self.task.priority

    @property
    def due_date_value(self):
        # 🔥 FINAL FIX (no static deadline)
        return self.due_date_override or self.due_date

    # ===============================
    # WORKFLOW
    # ===============================

    def submit(self):

        if self.status not in ["checked_in", "rejected"]:
            return False

        self.status = "submitted"
        self.submitted_at = timezone.now()
        self.approved_at = None
        self.approved_by = None

        self.save(update_fields=[
            "status",
            "submitted_at",
            "approved_at",
            "approved_by"
        ])
        return True

    def approve(self, admin_user):

        if self.status != "submitted":
            return False

        self.status = "approved"
        self.approved_by = admin_user
        self.approved_at = timezone.now()

        self.save(update_fields=[
            "status",
            "approved_by",
            "approved_at"
        ])
        return True

    def reject(self, admin_user, note=None):

        if self.status != "submitted":
            return False

        self.status = "rejected"
        self.reject_note = note
        self.approved_by = admin_user
        self.approved_at = timezone.now()

        self.save(update_fields=[
            "status",
            "reject_note",
            "approved_by",
            "approved_at"
        ])
        return True

    # ===============================
    # POINT SYSTEM
    # ===============================

    @property
    def calculate_points(self):

        if self.custom_points is not None:
            return self.custom_points

        task_type = self.task_type_value
        priority = self.priority_value
        due_date = self.due_date_value

        base_points = {
            "visit": 12,
            "desk": 6,
            "call": 5,
            "meeting": 10,
            "collection": 15,
        }.get(task_type, 5)

        priority_multiplier = {
            "low": 1,
            "medium": 1.3,
            "high": 1.6,
        }.get(priority, 1)

        points = base_points * priority_multiplier

        if due_date and self.approved_at:
            approved_date = self.approved_at.date()

            if approved_date <= due_date:
                points += 3
            else:
                points -= 2

        total_sales = sum(o.amount for o in self.orders.all())
        points += float(total_sales) * 0.005

        total_collection = sum(c.amount for c in self.collections.all())
        points += float(total_collection) * 0.01

        return round(points, 2)

# =========================================
# SALES ORDER
# =========================================

class SalesOrder(models.Model):

    assignment = models.ForeignKey(
        TaskAssignment,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.amount}"


# =========================================
# COLLECTION
# =========================================

class Collection(models.Model):

    assignment = models.ForeignKey(
        TaskAssignment,
        on_delete=models.CASCADE,
        related_name="collections"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Collection {self.amount}"


# =========================================
# LIVE EMPLOYEE LOCATION
# =========================================

class EmployeeLocation(models.Model):

    employee = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="live_location"
    )

    latitude = models.FloatField()
    longitude = models.FloatField()

    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return f"{self.employee} ({self.latitude},{self.longitude})"


# =========================================
# TASK ACTION NOTE
# =========================================

class TaskActionNote(models.Model):

    NOTE_TYPE = (
        ("reject", "Reject"),
        ("resubmit", "Resubmit"),
        ("comment", "Comment"),  
        
    )

    assignment = models.ForeignKey(
        TaskAssignment,
        on_delete=models.CASCADE,
        related_name="notes"
    )

    note_type = models.CharField(
        max_length=10,
        choices=NOTE_TYPE
    )

    note = models.TextField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.note_type} - {self.created_at}"