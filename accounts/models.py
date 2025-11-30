from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    """
    سفارشی‌سازی مدیریت کاربران برای مدل User
    """

    def create_user(self, phone_number, national_code, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("شماره موبایل الزامی است.")
        if not national_code:
            raise ValueError("کد ملی الزامی است.")

        user = self.model(
            phone_number=phone_number,
            national_code=national_code,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, national_code, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("ادمین باید is_staff=True داشته باشد.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("ادمین باید is_superuser=True داشته باشد.")

        return self.create_user(phone_number, national_code, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    مدل کاربر سفارشی با احراز هویت بر اساس شماره موبایل
    """
    national_code = models.CharField(max_length=10, unique=True, verbose_name="کد ملی")
    service_code = models.CharField(max_length=10, blank=True, null=True, verbose_name="کد خدمات")
    phone_number = models.CharField(max_length=11, unique=True, verbose_name="شماره موبایل")

    first_name = models.CharField(max_length=50, verbose_name="نام")
    last_name = models.CharField(max_length=50, verbose_name="نام خانوادگی")
    father_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="نام پدر")

    city = models.CharField(max_length=50, blank=True, null=True, verbose_name="شهر")

    ROLE_CHOICES = (
        ('admin', 'ادمین'),
        ('teacher', 'معلم'),
        ('student', 'دانش‌آموز'),
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name="نقش"
    )

    is_active = models.BooleanField(default=True, verbose_name="فعال")
    is_staff = models.BooleanField(default=False, verbose_name="کارمند")

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['national_code']

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        return f"{self.phone_number} - {self.first_name} {self.last_name}"


class UserSession(models.Model):
    """
    مدیریت sessionهای کاربری (برای logout و ردیابی دستگاه/آی‌پی)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions', verbose_name="کاربر")
    refresh_token = models.TextField(verbose_name="توکن بازیابی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="آی‌پی")
    device = models.CharField(max_length=200, null=True, blank=True, verbose_name="دستگاه")

    class Meta:
        verbose_name = "نشست کاربر"
        verbose_name_plural = "نشست‌های کاربران"

    def __str__(self):
        return f"نشست {self.user.phone_number} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"