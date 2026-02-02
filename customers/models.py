from django.db import models
from locations.models import Division, District, Thana, PostOffice
from company.models import Company


class BusinessCategory(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class SellingProduct(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class Customer(models.Model):
    # 🔴 MUST for SaaS isolation
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)

    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    thana = models.ForeignKey(Thana, on_delete=models.SET_NULL, null=True)
    post_office = models.ForeignKey(PostOffice, on_delete=models.SET_NULL, null=True)

    business_categories = models.ManyToManyField(BusinessCategory, blank=True)
    selling_products = models.ManyToManyField(SellingProduct, blank=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"
