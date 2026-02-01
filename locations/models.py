from django.db import models

# Create your models here.
from django.db import models


class Division(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class District(models.Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Thana(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class PostOffice(models.Model):
    thana = models.ForeignKey(Thana, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    post_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} ({self.post_code})"
