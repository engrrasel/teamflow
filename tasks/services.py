from datetime import date
from customers.models import Customer
from accounts.models import Membership
from .models import Task


def auto_assign_tasks(company):

    today = date.today()

    customers = Customer.objects.filter(company=company)

    employees = Membership.objects.filter(
        company=company,
        role="employee"
    )

    for customer in customers:

        customer_tags = set(
            customer.tags.values_list("id", flat=True)
        )

        for emp in employees:

            emp_tags = set(
                emp.tags.values_list("id", flat=True)
            )

            if customer_tags & emp_tags:

                Task.objects.get_or_create(
                    company=company,
                    employee=emp.user,
                    customer=customer,
                    due_date=today,
                    defaults={
                        "title": f"Visit {customer.name}"
                    }
                )