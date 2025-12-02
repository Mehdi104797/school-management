"""
Serializerهای مربوط به سیستم احراز هویت و مدیریت کاربران

هر Serializer مسئولیت زیر را دارد:
1. اعتبارسنجی داده‌های ورودی
2. تبدیل داده‌ها به فرمت مناسب برای مدل
3. ارائه خروجی استاندارد برای API
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User, PasswordResetOTP


# ============================================================================
# 1. RegisterSerializer - ثبت‌نام کاربر جدید
# ============================================================================

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer برای ثبت‌نام کاربر جدید در سیستم
    
    ورودی‌های مورد نیاز:
        phone_number (str): شماره موبایل ۱۱ رقمی (شروع با 09)
        national_code (str): کد ملی ۱۰ رقمی
        password (str): رمز عبور (حداقل ۶ کاراکتر)
        first_name (str): نام
        last_name (str): نام خانوادگی
        father_name (str, اختیاری): نام پدر
        service_code (str, اختیاری): کد خدمات
        city (str, اختیاری): شهر
        role (str, اختیاری): نقش کاربر (پیش‌فرض: student)
    
    خروجی:
        dict: داده‌های کاربر ثبت‌نام شده
    
    مثال JSON ورودی:
        {
            "phone_number": "09123456789",
            "national_code": "1234567890",
            "password": "password123",
            "first_name": "علی",
            "last_name": "محمدی",
            "city": "تهران",
            "role": "student"
        }
    """
    
    password = serializers.CharField(
        write_only=True, 
        min_length=6,
        style={'input_type': 'password'},
        help_text="رمز عبور باید حداقل ۶ کاراکتر باشد"
    )

    class Meta:
        model = User
        fields = [
            'phone_number', 'national_code', 'password',
            'first_name', 'last_name', 'father_name',
            'service_code', 'city', 'role'
        ]
    
    def validate_phone_number(self, value):
        """
        اعتبارسنجی شماره موبایل
        
        ورودی:
            value (str): شماره موبایل وارد شده
        
        خروجی:
            str: شماره موبایل اعتبارسنجی شده
        
        خطاهای احتمالی:
            ValidationError: اگر شماره معتبر نباشد یا تکراری باشد
        """
        # بررسی فرمت شماره موبایل
        if not (value.isdigit() and len(value) == 11 and value.startswith('09')):
            raise serializers.ValidationError("شماره موبایل معتبر نیست.")
        
        # بررسی تکراری نبودن
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("این شماره موبایل قبلاً ثبت شده است.")
        
        return value

    def validate_national_code(self, value):
        """
        اعتبارسنجی کد ملی
        
        ورودی:
            value (str): کد ملی وارد شده
        
        خروجی:
            str: کد ملی اعتبارسنجی شده
        """
        # بررسی فرمت کد ملی
        if not (value.isdigit() and len(value) == 10):
            raise serializers.ValidationError("کد ملی باید 10 رقم عددی باشد.")
        
        # بررسی تکراری نبودن
        if User.objects.filter(national_code=value).exists():
            raise serializers.ValidationError("این کد ملی قبلاً ثبت شده است.")
        
        return value

    def create(self, validated_data):
        """
        ایجاد کاربر جدید در دیتابیس
        
        ورودی:
            validated_data (dict): داده‌های اعتبارسنجی شده
        
        خروجی:
            User object: شیء کاربر ایجاد شده
        """
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # هش کردن رمز عبور
        user.save()
        return user


# ============================================================================
# 2. LoginSerializer - ورود کاربر به سیستم
# ============================================================================

class LoginSerializer(serializers.Serializer):
    """
    Serializer برای احراز هویت و ورود کاربر
    
    ورودی‌های مورد نیاز:
        phone_number (str): شماره موبایل ثبت‌نام شده
        password (str): رمز عبور
    
    خروجی:
        dict: شامل user object در validated_data
    
    مثال JSON ورودی:
        {
            "phone_number": "09123456789",
            "password": "password123"
        }
    """
    
    phone_number = serializers.CharField(
        help_text="شماره موبایل ۱۱ رقمی"
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="رمز عبور حساب کاربری"
    )

    def validate(self, data):
        """
        اعتبارسنجی کلی برای احراز هویت
        
        ورودی:
            data (dict): داده‌های ورودی شامل phone_number و password
        
        خروجی:
            dict: داده‌های اعتبارسنجی شده با اضافه شدن user object
        
        خطاهای احتمالی:
            ValidationError: اگر احراز هویت ناموفق باشد
        """
        # احراز هویت کاربر
        user = authenticate(
            phone_number=data['phone_number'],
            password=data['password']
        )
        
        # بررسی موفقیت احراز هویت
        if not user:
            raise serializers.ValidationError("شماره موبایل یا رمز عبور اشتباه است.")
        
        # بررسی فعال بودن حساب کاربری
        if not user.is_active:
            raise serializers.ValidationError("حساب کاربری غیرفعال است.")
        
        # اضافه کردن user به داده‌های بازگشتی
        data['user'] = user
        return data


# ============================================================================
# 3. UserSerializer - نمایش اطلاعات کامل کاربر
# ============================================================================

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer برای نمایش اطلاعات کامل کاربر (معمولاً برای ادمین)
    
    موارد استفاده:
        - نمایش لیست کاربران در پنل ادمین
        - نمایش جزئیات یک کاربر خاص
    
    خروجی شامل تمام فیلدهای مهم کاربر به جز رمز عبور
    
    مثال JSON خروجی:
        {
            "id": 1,
            "phone_number": "09123456789",
            "national_code": "1234567890",
            "first_name": "علی",
            "last_name": "محمدی",
            "role": "student",
            ...
        }
    """
    
    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'national_code', 'service_code',
            'first_name', 'last_name', 'father_name', 'city', 'role',
            'phone_verified', 'is_active'
        ]
        read_only_fields = ['id']  # شناسه کاربر قابل ویرایش نیست


# ============================================================================
# 4. ProfileSerializer - مدیریت پروفایل کاربر
# ============================================================================

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer برای نمایش و ویرایش پروفایل کاربر جاری
    
    تفاوت با UserSerializer:
        - فیلدهای read-only بیشتر (شماره موبایل، کد ملی، نقش)
        - فقط برای کاربر جاری استفاده می‌شود
    
    فیلدهای قابل ویرایش:
        first_name, last_name, father_name, city, service_code
    
    مثال JSON ورودی برای ویرایش:
        {
            "first_name": "علی",
            "last_name": "احمدی",
            "city": "مشهد"
        }
    """
    
    class Meta:
        model = User
        fields = [
            'phone_number', 'national_code', 'service_code',
            'first_name', 'last_name', 'father_name', 'city', 'role',
            'phone_verified', 'phone_verified_at'
        ]
        read_only_fields = [
            'phone_number', 'national_code', 'role',
            'phone_verified', 'phone_verified_at'
        ]


# ============================================================================
# 5. ForgotPasswordSerializer - درخواست بازیابی رمز عبور
# ============================================================================

class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer برای درخواست کد OTP بازیابی رمز عبور
    
    ورودی مورد نیاز:
        phone_number (str): شماره موبایل کاربر
    
    خروجی:
        dict: پیام تأیید ارسال کد
    
    کارکرد:
        1. اعتبارسنجی شماره موبایل
        2. بررسی وجود کاربر
        3. ایجاد و ارسال کد OTP
    
    مثال JSON ورودی:
        {
            "phone_number": "09123456789"
        }
    """
    
    phone_number = serializers.CharField(
        max_length=11,
        help_text="شماره موبایل ۱۱ رقمی برای دریافت کد بازیابی"
    )
    
    def validate_phone_number(self, value):
        """
        اعتبارسنجی شماره موبایل برای بازیابی رمز
        
        ورودی:
            value (str): شماره موبایل وارد شده
        
        خروجی:
            str: شماره موبایل اعتبارسنجی شده
        
        خطاهای احتمالی:
            ValidationError: اگر شماره معتبر نباشد یا کاربر وجود نداشته باشد
        """
        # بررسی فرمت شماره موبایل
        if not (value.isdigit() and len(value) == 11 and value.startswith('09')):
            raise serializers.ValidationError("شماره موبایل معتبر نیست.")
        
        # بررسی وجود کاربر
        if not User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("کاربری با این شماره موبایل یافت نشد.")
        
        return value


# ============================================================================
# 6. VerifyOTPSerializer - تأیید کد OTP و تغییر رمز
# ============================================================================

class VerifyOTPSerializer(serializers.Serializer):
    """
    Serializer برای تأیید کد OTP و تنظیم رمز عبور جدید
    
    ورودی‌های مورد نیاز:
        phone_number (str): شماره موبایل
        otp_code (str): کد ۶ رقمی دریافتی
        new_password (str): رمز عبور جدید (حداقل ۶ کاراکتر)
    
    خروجی:
        dict: پیام تأیید تغییر رمز
    
    مثال JSON ورودی:
        {
            "phone_number": "09123456789",
            "otp_code": "123456",
            "new_password": "newpassword123"
        }
    """
    
    phone_number = serializers.CharField(
        max_length=11,
        help_text="شماره موبایل کاربر"
    )
    otp_code = serializers.CharField(
        max_length=6,
        help_text="کد ۶ رقمی ارسال شده به موبایل"
    )
    new_password = serializers.CharField(
        min_length=6, 
        write_only=True,
        style={'input_type': 'password'},
        help_text="رمز عبور جدید (حداقل ۶ کاراکتر)"
    )
    
    def validate(self, data):
        """
        اعتبارسنجی کد OTP و وضعیت آن
        
        ورودی:
            data (dict): داده‌های ورودی
        
        خروجی:
            dict: داده‌ها با اضافه شدن otp_record
        
        خطاهای احتمالی:
            ValidationError: اگر کد OTP معتبر نباشد
        """
        now = timezone.now()
        
        try:
            # جستجوی کد OTP معتبر و استفاده نشده
            otp_record = PasswordResetOTP.objects.get(
                phone_number=data['phone_number'],
                otp_code=data['otp_code'],
                is_used=False,  # استفاده نشده باشد
                expires_at__gt=now  # منقضی نشده باشد
            )
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError("کد OTP نامعتبر یا منقضی شده است.")
        
        # اضافه کردن رکورد OTP به داده‌های بازگشتی
        data['otp_record'] = otp_record
        return data


# ============================================================================
# 7. PhoneVerificationSerializer - تأیید شماره موبایل
# ============================================================================

class PhoneVerificationSerializer(serializers.Serializer):
    """
    Serializer برای تأیید شماره موبایل با کد ارسالی
    
    ورودی‌های مورد نیاز:
        phone_number (str): شماره موبایل
        verification_code (str): کد تأیید ۶ رقمی
    
    مثال JSON ورودی:
        {
            "phone_number": "09123456789",
            "verification_code": "654321"
        }
    """
    
    phone_number = serializers.CharField(
        max_length=11,
        help_text="شماره موبایل برای تأیید"
    )
    verification_code = serializers.CharField(
        max_length=6,
        help_text="کد تأیید ارسال شده به موبایل"
    )


# ============================================================================
# 8. ResendVerificationSerializer - درخواست مجدد کد تأیید
# ============================================================================

class ResendVerificationSerializer(serializers.Serializer):
    """
    Serializer برای درخواست ارسال مجدد کد تأیید موبایل
    
    ورودی مورد نیاز:
        phone_number (str): شماره موبایل
    
    مثال JSON ورودی:
        {
            "phone_number": "09123456789"
        }
    """
    
    phone_number = serializers.CharField(
        max_length=11,
        help_text="شماره موبایل برای ارسال مجدد کد تأیید"
    )


# ============================================================================
# 9. RoleSerializer - تغییر نقش کاربر
# ============================================================================

class RoleSerializer(serializers.Serializer):
    """
    Serializer ساده برای تغییر نقش کاربر
    
    ورودی:
        role (str): نقش جدید (admin/teacher/student)
    
    مثال JSON ورودی:
        {
            "role": "teacher"
        }
    """
    
    role = serializers.ChoiceField(
        choices=['admin', 'teacher', 'student'],
        help_text="نقش جدید کاربر"
    )


# ============================================================================
# 10. RoleChangeSerializer - تغییر نقش کاربر (نسخه کامل)
# ============================================================================

class RoleChangeSerializer(serializers.Serializer):
    """
    Serializer کامل برای تغییر نقش کاربر توسط ادمین
    
    ورودی‌های مورد نیاز:
        user_id (int): شناسه کاربر مورد نظر
        new_role (str): نقش جدید
        reason (str, اختیاری): دلیل تغییر نقش
    
    مثال JSON ورودی:
        {
            "user_id": 5,
            "new_role": "teacher",
            "reason": "ارتقا به مربی"
        }
    """
    
    user_id = serializers.IntegerField(
        help_text="شناسه کاربری که نقشش تغییر می‌کند"
    )
    new_role = serializers.ChoiceField(
        choices=['admin', 'teacher', 'student'],
        help_text="نقش جدید کاربر"
    )
    reason = serializers.CharField(
        max_length=255, 
        required=False,
        allow_blank=True,
        help_text="دلیل تغییر نقش (اختیاری)"
    )