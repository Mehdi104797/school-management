from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)  # admin, teacher, student

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    national_code = models.CharField(max_length=10, unique=True)
    service_code = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    father_name = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    roles = models.ManyToManyField(Role, related_name="users", blank=True)

    # تعریف فیلدهایی که برای login یا نمایش مهم‌اند
    USERNAME_FIELD = 'username'  # بعداً می‌تونیم به 'phone_number' تغییر بدیم
    REQUIRED_FIELDS = ['email', 'national_code', 'phone_number']