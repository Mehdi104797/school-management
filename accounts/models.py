"""
مدل‌های مربوط به احراز هویت کاربران - سیستم Role-Based Authentication
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


# ----------------------------------------------------------------------
# UserManager - مدیریت عملیات کاربران
# ----------------------------------------------------------------------

class UserManager(BaseUserManager):
    """
    مدیریت سفارشی کاربران برای مدل User
    """
    
    def create_user(self, phone_number, national_code, password=None, **extra_fields):
        """
        ایجاد کاربر عادی
        
        ورودی:
            phone_number (str): شماره موبایل (11 رقمی)
            national_code (str): کد ملی (10 رقمی)
            password (str): رمز عبور (اختیاری)
            **extra_fields: فیلدهای اضافی کاربر
        
        خروجی:
            User object: شیء کاربر ایجاد شده
        
        خطاهای احتمالی:
            ValueError: اگر شماره موبایل یا کد ملی خالی باشد
        """
        # اعتبارسنجی فیلدهای اجباری
        if not phone_number:
            raise ValueError("شماره موبایل الزامی است.")
        if not national_code:
            raise ValueError("کد ملی الزامی است.")

        # ایجاد شیء کاربر جدید
        user = self.model(
            phone_number=phone_number,
            national_code=national_code,
            **extra_fields
        )
        
        # تنظیم رمز عبور (اگر ارسال شده)
        if password:
            user.set_password(password)
        
        # ذخیره کاربر در دیتابیس
        user.save(using=self._db)
        
        return user

    def create_superuser(self, phone_number, national_code, password=None, **extra_fields):
        """
        ایجاد کاربر ادمین (Superuser)
        
        ورودی:
            phone_number (str): شماره موبایل ادمین
            national_code (str): کد ملی ادمین
            password (str): رمز عبور ادمین
            **extra_fields: فیلدهای اضافی
        
        خروجی:
            User object: شیء ادمین ایجاد شده
        
        خطاهای احتمالی:
            ValueError: اگر is_staff یا is_superuser نادرست باشد
        """
        # تنظیم مقادیر پیش‌فرض برای ادمین
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # اعتبارسنجی مقادیر ادمین
        if extra_fields.get('is_staff') is not True:
            raise ValueError("ادمین باید is_staff=True داشته باشد.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("ادمین باید is_superuser=True داشته باشد.")

        # ایجاد ادمین با استفاده از متد create_user
        return self.create_user(phone_number, national_code, password, **extra_fields)


# ----------------------------------------------------------------------
# User - مدل اصلی کاربر
# ----------------------------------------------------------------------

class User(AbstractBaseUser, PermissionsMixin):
    """
    مدل کاربر سفارشی با احراز هویت بر اساس شماره موبایل
    
    فیلدهای کلیدی:
        phone_number: به عنوان USERNAME_FIELD استفاده می‌شود
        national_code: برای شناسایی ملی کاربر
        role: تعیین نقش کاربر در سیستم
    """
    
    # ======================== فیلدهای شناسایی ========================
    national_code = models.CharField(
        max_length=10, 
        unique=True, 
        verbose_name="کد ملی"
    )
    service_code = models.CharField(
        max_length=10, 
        blank=True, 
        null=True, 
        verbose_name="کد خدمات"
    )
    phone_number = models.CharField(
        max_length=11, 
        unique=True, 
        verbose_name="شماره موبایل"
    )
    
    # ======================== فیلدهای اطلاعات شخصی ========================
    first_name = models.CharField(max_length=50, verbose_name="نام")
    last_name = models.CharField(max_length=50, verbose_name="نام خانوادگی")
    father_name = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="نام پدر"
    )
    city = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="شهر"
    )
    
    # ======================== فیلدهای نقش و وضعیت ========================
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
    
    # ======================== فیلدهای تأیید موبایل ========================
    phone_verified = models.BooleanField(
        default=False, 
        verbose_name="موبایل تأیید شده"
    )
    phone_verified_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="تاریخ تأیید موبایل"
    )
    
    # ======================== فیلدهای فعال/غیرفعال ========================
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    is_staff = models.BooleanField(default=False, verbose_name="کارمند")
    
    # ======================== تنظیمات مدیریت کاربر ========================
    objects = UserManager()
    
    USERNAME_FIELD = 'phone_number'  # فیلد برای احراز هویت
    REQUIRED_FIELDS = ['national_code']  # فیلدهای اجباری
    
    class Meta:
        """تنظیمات متا برای مدل User"""
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"
    
    def __str__(self):
        """نمایش رشته‌ای کاربر"""
        return f"{self.phone_number} - {self.first_name} {self.last_name}"


# ----------------------------------------------------------------------
# UserSession - مدیریت نشست‌های کاربر
# ----------------------------------------------------------------------

class UserSession(models.Model):
    """
    مدیریت sessionهای کاربر برای کنترل چند دستگاه و ردیابی
    
    کاربردها:
        - کنترل چند دستگاه
        - ردیابی دستگاه‌های فعال
        - امکان logout انتخابی
        - امنیت با ذخیره IP و دستگاه
    """
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sessions', 
        verbose_name="کاربر"
    )
    refresh_token = models.TextField(verbose_name="توکن بازیابی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="آی‌پی")
    expires_at = models.DateTimeField(verbose_name="تاریخ انقضا")
    device = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name="دستگاه"
    )
    
    class Meta:
        """تنظیمات متا برای UserSession"""
        verbose_name = "نشست کاربر"
        verbose_name_plural = "نشست‌های کاربران"
    
    def __str__(self):
        """نمایش رشته‌ای session"""
        return f"نشست {self.user.phone_number} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # پیش‌فرض 7 روز بعد
            from django.utils import timezone
            from datetime import timedelta
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

# ----------------------------------------------------------------------
# PasswordResetOTP - مدیریت OTP بازیابی رمز عبور
# ----------------------------------------------------------------------

class PasswordResetOTP(models.Model):
    """
    ذخیره کدهای OTP برای بازیابی رمز عبور
    
    کاربردها:
        - تأیید هویت کاربر برای بازیابی رمز
        - محدودیت زمانی کدها
        - جلوگیری از استفاده مجدد
    """
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="کاربر"
    )
    phone_number = models.CharField(
        max_length=11, 
        verbose_name="شماره موبایل"
    )
    otp_code = models.CharField(
        max_length=6, 
        verbose_name="کد OTP"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="تاریخ ایجاد"
    )
    expires_at = models.DateTimeField(
        verbose_name="تاریخ انقضا"
    )
    is_used = models.BooleanField(
        default=False, 
        verbose_name="استفاده شده"
    )
    
    class Meta:
        """تنظیمات متا برای PasswordResetOTP"""
        verbose_name = "کد بازیابی رمز"
        verbose_name_plural = "کدهای بازیابی رمز"
        indexes = [
            # ایندکس برای جستجوی سریع با شماره موبایل و کد OTP
            models.Index(fields=['phone_number', 'otp_code']),
            # ایندکس برای حذف خودکار کدهای منقضی شده
            models.Index(fields=['expires_at']),
        ]


# ----------------------------------------------------------------------
# LoginAttempt - ردیابی تلاش‌های ورود
# ----------------------------------------------------------------------

class LoginAttempt(models.Model):
    """
    ثبت تمام تلاش‌های ورود برای امنیت و آنالیز
    
    کاربردها:
        - تشخیص حملات Brute-force
        - آنالیز رفتار کاربران
        - گزارش‌گیری امنیتی
        - محدودیت تلاش‌های ناموفق
    """
    
    phone_number = models.CharField(
        max_length=11, 
        verbose_name="شماره موبایل"
    )
    ip_address = models.GenericIPAddressField(
        verbose_name="آی‌پی"
    )
    attempt_time = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="زمان تلاش"
    )
    successful = models.BooleanField(
        default=False, 
        verbose_name="موفق"
    )
    
    class Meta:
        """تنظیمات متا برای LoginAttempt"""
        verbose_name = "تلاش ورود"
        verbose_name_plural = "تلاش‌های ورود"
        indexes = [
            # ایندکس برای آنالیز تلاش‌های کاربر
            models.Index(fields=['phone_number', 'attempt_time']),
            # ایندکس برای آنالیز تلاش‌های آی‌پی
            models.Index(fields=['ip_address', 'attempt_time']),
        ]


# ----------------------------------------------------------------------
# SecurityLog - ثبت لاگ‌های امنیتی
# ----------------------------------------------------------------------

class SecurityLog(models.Model):
    """
    ثبت تمام فعالیت‌های امنیتی سیستم
    
    کاربردها:
        - ممیزی امنیتی
        - ردیابی تغییرات
        - عیب‌یابی
        - گزارش‌گیری
    """
    
    # انواع فعالیت‌های قابل ثبت
    ACTION_CHOICES = (
        ('LOGIN_SUCCESS', 'ورود موفق'),
        ('LOGIN_FAILED', 'ورود ناموفق'),
        ('PASSWORD_CHANGED', 'تغییر رمز عبور'),
        ('PHONE_VERIFIED', 'تأیید موبایل'),
        ('ROLE_CHANGED', 'تغییر نقش'),
        ('SESSION_REVOKED', 'ابطال نشست'),
        ('USER_CREATED', 'ایجاد کاربر'),
        ('USER_UPDATED', 'ویرایش کاربر'),
        ('USER_DELETED', 'حذف کاربر'),
        ('ADMIN_ACTION', 'عملیات ادمین'),
    )
    
    # ======================== فیلدهای لاگ ========================
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="کاربر"
    )
    action = models.CharField(
        max_length=50, 
        choices=ACTION_CHOICES, 
        verbose_name="عملیات"
    )
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True, 
        verbose_name="آی‌پی"
    )
    user_agent = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="User Agent"
    )
    details = models.JSONField(
        default=dict, 
        verbose_name="جزئیات"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="زمان ایجاد"
    )
    
    class Meta:
        """تنظیمات متا برای SecurityLog"""
        verbose_name = "لاگ امنیتی"
        verbose_name_plural = "لاگ‌های امنیتی"
        ordering = ['-created_at']  # نمایش جدیدترین لاگ‌ها اول
        indexes = [
            # ایندکس برای جستجوی لاگ‌های کاربر
            models.Index(fields=['user', 'created_at']),
            # ایندکس برای جستجوی بر اساس نوع عملیات
            models.Index(fields=['action', 'created_at']),
        ]