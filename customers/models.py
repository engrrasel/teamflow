from django.db import models
from locations.models import Division, District, Thana, PostOffice


class Customer(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)

    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    thana = models.ForeignKey(Thana, on_delete=models.SET_NULL, null=True)
    post_office = models.ForeignKey(PostOffice, on_delete=models.SET_NULL, null=True)

    business_categories = models.JSONField(default=list, blank=True)
    selling_products = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"


