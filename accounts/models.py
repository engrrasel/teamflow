from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


# ------------------ User Manager ------------------

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # 🔥 invited user এর জন্য

        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# ------------------ User Model ------------------

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)

    # SaaS invite flow এর জন্য
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_invited = models.BooleanField(default=False)  # 🔥 গুরুত্বপূর্ণ

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


# ------------------ Membership (SaaS core) ------------------

from django.conf import settings
from company.models import Company


class Membership(models.Model):
    ROLE_CHOICES = (
        ('platform_admin', 'Platform Admin'),
        ('company_admin', 'Company Admin'),
        ('employee', 'Employee'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'company')

    def __str__(self):
        return f"{self.user.email} → {self.company.name} ({self.role})"
