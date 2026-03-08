from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=120)
    address = models.TextField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class DesignationGroup(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('company', 'name')  # 🔥 duplicate group আটকাবে

    def __str__(self):
        return f"{self.name} - {self.company.name}"


class Designation(models.Model):
    group = models.ForeignKey(DesignationGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('group', 'name')  # 🔥 duplicate designation আটকাবে

    def __str__(self):
        return f"{self.name} ({self.group.name})"



class CompanyWeekend(models.Model):

    WEEKDAYS = (
        (0,"Monday"),
        (1,"Tuesday"),
        (2,"Wednesday"),
        (3,"Thursday"),
        (4,"Friday"),
        (5,"Saturday"),
        (6,"Sunday"),
    )

    company = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="weekends"
    )

    weekday = models.IntegerField(choices=WEEKDAYS)

    def __str__(self):
        return f"{self.company} - {self.get_weekday_display()}"
    

class CompanyHoliday(models.Model):

    company = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="holidays"
    )

    name = models.CharField(max_length=100)

    date = models.DateField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "date"],
                name="unique_company_holiday"
            )
        ]

    def __str__(self):
        return f"{self.name} - {self.date}"