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
