from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=120)
    address = models.TextField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name
