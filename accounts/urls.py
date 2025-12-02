"""
فایل تنظیمات URL برای اپلیکیشن accounts

این فایل تمام endpointهای API مربوط به احراز هویت،
مدیریت کاربران و سیستم Role-Based را تعریف می‌کند.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter


# ============================================================================
# بخش ۱: Import ViewSet‌ها
# ============================================================================

from .views import (
    # ViewSet‌های اصلی احراز هویت
    RegisterViewSet,      # ثبت‌نام کاربر جدید
    LoginViewSet,         # ورود به سیستم
    LogoutViewSet,        # خروج از سیستم
    ProfileViewSet,       # مدیریت پروفایل کاربر
    
    # ViewSet‌های مدیریت بر اساس نقش
    AdminViewSet,         # پنل مدیریت ادمین
    TeacherViewSet,       # پنل مدیریت معلم
    
    # ViewSet‌های امنیتی جدید
    ForgotPasswordViewSet,        # بازیابی رمز عبور
    VerifyOTPViewSet,             # تأیید کد OTP
    PhoneVerificationViewSet,     # تأیید شماره موبایل
    
    # ViewSet‌های مدیریتی جدید
    RoleManagementViewSet,        # مدیریت نقش‌ها
    SessionManagementViewSet,     # مدیریت نشست‌ها
    AdminDashboardViewSet,        # داشبورد ادمین
)


# ============================================================================
# بخش ۲: تنظیمات Router اصلی
# ============================================================================

# ایجاد Router پیش‌فرض Django REST Framework
router = DefaultRouter()

# ثبت ViewSet‌ها با Router

# ۲.۱ endpointهای اصلی احراز هویت
router.register(
    'register',               # مسیر: /api/accounts/register/
    RegisterViewSet,          # ViewSet مربوطه
    basename='register'       # نام پایه برای URLها
)

router.register(
    'login',                  # مسیر: /api/accounts/login/
    LoginViewSet,             
    basename='login'
)

router.register(
    'logout',                 # مسیر: /api/accounts/logout/
    LogoutViewSet,            
    basename='logout'
)

router.register(
    'profile',                # مسیر: /api/accounts/profile/
    ProfileViewSet,           
    basename='profile'
)

# ۲.۲ endpointهای مدیریت بر اساس نقش
router.register(
    'admin-panel',            # مسیر: /api/accounts/admin-panel/
    AdminViewSet,             
    basename='admin_panel'    # فقط برای کاربران با نقش admin
)

router.register(
    'teacher-panel',          # مسیر: /api/accounts/teacher-panel/
    TeacherViewSet,           
    basename='teacher_panel'  # فقط برای کاربران با نقش teacher
)

# ۲.۳ endpointهای امنیتی جدید
router.register(
    'forgot-password',        # مسیر: /api/accounts/forgot-password/
    ForgotPasswordViewSet,    # درخواست کد بازیابی رمز
    basename='forgot_password'
)

router.register(
    'verify-otp',             # مسیر: /api/accounts/verify-otp/
    VerifyOTPViewSet,         # تأیید کد OTP و تغییر رمز
    basename='verify_otp'
)

router.register(
    'verify-phone',           # مسیر: /api/accounts/verify-phone/
    PhoneVerificationViewSet, # تأیید شماره موبایل
    basename='verify_phone'
)

# ۲.۴ endpointهای مدیریتی جدید
router.register(
    'role-management',        # مسیر: /api/accounts/role-management/
    RoleManagementViewSet,    # مدیریت نقش کاربران
    basename='role_management'
)

router.register(
    'session-management',     # مسیر: /api/accounts/session-management/
    SessionManagementViewSet, # مدیریت نشست‌های کاربر
    basename='session_management'
)

router.register(
    'admin-dashboard',        # مسیر: /api/accounts/admin-dashboard/
    AdminDashboardViewSet,    # داشبورد آمار و گزارشات
    basename='admin_dashboard'
)


# ============================================================================
# بخش ۳: لیست نهایی URLها
# ============================================================================

urlpatterns = [
    # شامل کردن تمام URLهای ثبت شده در Router
    path('', include(router.urls)),
]


# ============================================================================
# بخش ۴: توابع کمکی (Utility Functions) - باید به فایل جداگانه منتقل شود
# ============================================================================

"""
توجه: توابع زیر باید به فایل utils.py یا services.py منتقل شوند
این‌ها فقط برای نمونه در اینجا قرار داده شده‌اند.
"""

import random
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def generate_otp(length=6):
    """
    تولید کد OTP تصادفی
    
    ورودی:
        length (int, اختیاری): طول کد OTP (پیش‌فرض: 6)
    
    خروجی:
        str: کد OTP تولید شده
    
    مثال:
        >>> generate_otp(6)
        '123456'
        >>> generate_otp(4)
        '7890'
    """
    # تولید رشته‌ای از اعداد تصادفی با طول مشخص
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def send_sms(phone_number, message):
    """
    ارسال پیامک به شماره موبایل (نسخه mock برای توسعه)
    
    در محیط تولید باید با سرویس پیامک واقعی جایگزین شود.
    
    ورودی:
        phone_number (str): شماره موبایل گیرنده
        message (str): متن پیامک
    
    خروجی:
        bool: True اگر ارسال موفق باشد
    
    مثال:
        >>> send_sms("09123456789", "کد تأیید شما: 123456")
        📱 SMS to 09123456789: کد تأیید شما: 123456
        True
    """
    try:
        # TODO: این بخش باید با سرویس پیامک واقعی جایگزین شود
        # مانند: کاوه نگار، فارابیت، پیامک رسان و...
        
        # برای محیط توسعه، پیام را در کنسول نمایش می‌دهیم
        print(f"📱 SMS to {phone_number}: {message}")
        
        # ثبت در لاگ سیستم
        logger.info(f"SMS sent to {phone_number}: {message}")
        
        # شبیه‌سازی موفقیت‌آمیز بودن ارسال
        return True
        
    except Exception as e:
        # ثبت خطا در صورت عدم موفقیت
        logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
        return False


# ============================================================================
# بخش ۵: مستندات endpointها
# ============================================================================

"""
📌 لیست کامل endpointهای API:

1. احراز هویت:
   POST   /api/accounts/register/      - ثبت‌نام کاربر جدید
   POST   /api/accounts/login/         - ورود به سیستم
   POST   /api/accounts/logout/        - خروج از سیستم

2. پروفایل:
   GET    /api/accounts/profile/       - مشاهده پروفایل
   PATCH  /api/accounts/profile/       - ویرایش پروفایل

3. امنیت:
   POST   /api/accounts/forgot-password/   - درخواست کد بازیابی
   POST   /api/accounts/verify-otp/        - تأیید کد و تغییر رمز
   POST   /api/accounts/verify-phone/      - تأیید شماره موبایل

4. مدیریت نشست:
   GET    /api/accounts/session-management/   - لیست نشست‌ها
   POST   /api/accounts/session-management/revoke_session/  - ابطال یک نشست
   POST   /api/accounts/session-management/revoke_all_sessions/ - ابطال همه نشست‌ها

5. مدیریت نقش (فقط ادمین):
   GET    /api/accounts/role-management/      - لیست کاربران بر اساس نقش
   POST   /api/accounts/role-management/change_role/  - تغییر نقش کاربر

6. داشبورد ادمین:
   GET    /api/accounts/admin-dashboard/dashboard_stats/  - آمار سیستم

7. پنل‌های اختصاصی:
   GET    /api/accounts/admin-panel/    - پنل ادمین (لیست کاربران)
   GET    /api/accounts/teacher-panel/  - پنل معلم
"""


# ============================================================================
# بخش ۶: مثال‌های استفاده از API با curl
# ============================================================================

"""
مثال‌های درخواست به API با استفاده از curl:

1. ثبت‌نام:
curl -X POST http://localhost:8000/api/accounts/register/ \
     -H "Content-Type: application/json" \
     -d '{
          "phone_number": "09123456789",
          "national_code": "1234567890",
          "password": "password123",
          "first_name": "علی",
          "last_name": "محمدی"
        }'

2. ورود:
curl -X POST http://localhost:8000/api/accounts/login/ \
     -H "Content-Type: application/json" \
     -d '{
          "phone_number": "09123456789",
          "password": "password123"
        }'

3. مشاهده پروفایل (با توکن):
curl -X GET http://localhost:8000/api/accounts/profile/ \
     -H "Authorization: Bearer <access_token>"

4. بازیابی رمز عبور:
curl -X POST http://localhost:8000/api/accounts/forgot-password/ \
     -H "Content-Type: application/json" \
     -d '{"phone_number": "09123456789"}'
"""


# ============================================================================
# بخش ۷: نکات مهم
# ============================================================================

"""
⚠️ نکات امنیتی و پیکربندی:

1. حفاظت در برابر Brute-force:
   - endpointهای login و forgot-password باید rate-limited باشند
   - از django-ratelimit استفاده کنید

2. SSL/TLS:
   - در محیط تولید حتماً از HTTPS استفاده کنید
   - تنظیمات در settings.py:
     SECURE_SSL_REDIRECT = True
     SESSION_COOKIE_SECURE = True
     CSRF_COOKIE_SECURE = True

3. CORS:
   - فقط دامنه‌های مورد اعتماد را در CORS_ALLOWED_ORIGINS قرار دهید
   - در settings.py تنظیم کنید

4. توکن JWT:
   - زمان انقضای مناسب برای access و refresh tokenها تنظیم کنید
   - از ROTATE_REFRESH_TOKENS استفاده کنید

5. لاگ‌گیری:
   - تمام درخواست‌های مهم را لاگ کنید
   - از Sentry یا Loggly برای مانیتورینگ استفاده کنید
"""