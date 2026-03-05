from django.db import models
from django.conf import settings
from django.utils import timezone


# -----------------------------
# TASK
# -----------------------------

class Task(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    TASK_TYPE = (
        ("visit", "Visit"),
        ("desk", "Desk Work"),
        ("call", "Call"),
        ("meeting", "Meeting"),
        ("collection", "Collection"),
    )

    company = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_tasks"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tasks"
    )

    title = models.CharField(max_length=200)

    task_type = models.CharField(
        max_length=20,
        choices=TASK_TYPE,
        default="desk"
    )

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks"
    )

    due_date = models.DateField(
        null=True,
        blank=True
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    # admin custom point
    custom_points = models.FloatField(
        default=1
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_tasks"
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    assign_date = models.DateField(
        auto_now_add=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["employee"]),
            models.Index(fields=["due_date"]),
        ]

    # -------------------------
    # TASK SUBMIT
    # -------------------------

    def submit(self):
        self.status = "submitted"
        self.submitted_at = timezone.now()
        self.save()

    # -------------------------
    # TASK APPROVE
    # -------------------------

    def approve(self, admin_user):

        if self.status != "submitted":
            return

        self.status = "approved"
        self.approved_by = admin_user
        self.approved_at = timezone.now()

        self.save()

    # -------------------------
    # POINT CALCULATION
    # -------------------------
    def calculate_points(self):

        # admin যদি extra point দেয়
        if self.custom_points > 1:
            return self.custom_points

        # task assign হয়েছে কিন্তু submit হয়নি
        if not self.submitted_at:
            return 1

        if not self.due_date:
            return 1

        submit_date = self.submitted_at.date()

        if submit_date <= self.due_date:
            return 1

        delay_days = (submit_date - self.due_date).days

        if delay_days == 1:
            return 0.5

        return 0

    # -------------------------
    # PENALTY CALCULATION
    # -------------------------

    def calculate_penalty(self):

        if not self.submitted_at or not self.due_date:
            return 0

        submit_date = self.submitted_at.date()

        delay_days = (submit_date - self.due_date).days

        if delay_days <= 1:
            return 0

        # ২ দিন লেট হলে -1 থেকে শুরু
        return delay_days - 1

    def __str__(self):
        return f"{self.employee} → {self.title}"


# -----------------------------
# VISIT REPORT
# -----------------------------

class VisitReport(models.Model):

    task = models.OneToOneField(
        Task,
        on_delete=models.CASCADE,
        related_name="visit_report"
    )

    check_in_time = models.DateTimeField(
        auto_now_add=True
    )

    note = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"Visit Report - {self.task}"


# -----------------------------
# SALES ORDER
# -----------------------------

class SalesOrder(models.Model):

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Order {self.amount} - {self.task}"


# -----------------------------
# COLLECTION
# -----------------------------

class Collection(models.Model):

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="collections"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Collection {self.amount} - {self.task}"