from django.db import models
from django.conf import settings
from company.models import Company
from customers.models import Customer


# -----------------------------
# TASK
# -----------------------------
from django.db import models
from django.utils import timezone

class Task(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
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

    # যাকে task দেওয়া হয়েছে
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_tasks"
    )

    # কে task assign করেছে
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks"
    )

    title = models.CharField(
        max_length=200
    )

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

    points = models.FloatField(
        default=0
    )

    assign_date = models.DateField(
        auto_now_add=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']

    def calculate_points(self):

        if not self.submitted_at or not self.due_date:
            return 0

        if self.submitted_at.date() <= self.due_date:
            return 1
        else:
            return 0.5

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