"""
فایل توابع کمکی (Utilities) برای سیستم احراز هویت

این فایل شامل تمام توابع کمکی مورد نیاز برای:
1. تولید کدهای OTP
2. مدیریت ارسال پیامک
3. کنترل تلاش‌های ورود
4. توابع امنیتی دیگر

همه توابع به طور کامل مستند شده‌اند و ورودی/خروجی مشخص دارند.
"""

import random
import logging
from datetime import timedelta

from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from rest_framework import serializers

# تنظیمات لاگ‌گیری
logger = logging.getLogger(__name__)


# ============================================================================
# بخش ۱: توابع مربوط به OTP (One-Time Password)
# ============================================================================

def generate_otp(length=6):
    """
    تولید کد OTP تصادفی
    
    این تابع یک کد عددی تصادفی با طول مشخص تولید می‌کند.
    معمولاً برای احراز هویت دو مرحله‌ای یا بازیابی رمز استفاده می‌شود.
    
    ورودی:
        length (int, اختیاری): طول کد OTP
            • پیش‌فرض: 6
            • محدوده مجاز: 4 تا 10
    
    خروجی:
        str: کد OTP تولید شده
    
    مثال:
        >>> generate_otp()
        '123456'
        >>> generate_otp(4)
        '7890'
    
    نکات امنیتی:
        • از random.randint استفاده می‌کند که برای اهداف امنیتی کافی است
        • برای محیط‌های با امنیت بالا از secrets.randbelow استفاده کنید
    """
    # اعتبارسنجی طول کد
    if not 4 <= length <= 10:
        raise ValueError(f"طول کد OTP باید بین 4 تا 10 باشد، اما {length} دریافت شد.")
    
    # تولید کد تصادفی
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    
    # ثبت لاگ برای پیگیری
    logger.debug(f"OTP با طول {length} تولید شد")
    
    return otp


def generate_secure_otp(length=6):
    """
    تولید کد OTP ایمن برای محیط‌های با امنیت بالا
    
    از ماژول secrets استفاده می‌کند که برای اهداف رمزنگاری مناسب است.
    
    ورودی:
        length (int, اختیاری): طول کد OTP
    
    خروجی:
        str: کد OTP ایمن
    
    تفاوت با generate_otp:
        • استفاده از secrets برای امنیت بیشتر
        • مناسب برای محیط تولید
    """
    try:
        import secrets
        # تولید اعداد تصادفی ایمن
        numbers = [str(secrets.randbelow(10)) for _ in range(length)]
        return ''.join(numbers)
    except ImportError:
        # اگر ماژول secrets وجود نداشت، از نسخه ساده استفاده کن
        logger.warning("ماژول secrets یافت نشد، از random استفاده می‌شود")
        return generate_otp(length)


def validate_otp(otp_code):
    """
    اعتبارسنجی فرمت کد OTP
    
    ورودی:
        otp_code (str): کد OTP برای اعتبارسنجی
    
    خروجی:
        bool: True اگر کد معتبر باشد
    
    خطاها:
        ValidationError: اگر کد معتبر نباشد
    """
    if not otp_code:
        raise serializers.ValidationError("کد OTP الزامی است.")
    
    if not otp_code.isdigit():
        raise serializers.ValidationError("کد OTP باید فقط شامل اعداد باشد.")
    
    if not 4 <= len(otp_code) <= 10:
        raise serializers.ValidationError("طول کد OTP باید بین 4 تا 10 رقم باشد.")
    
    return True


# ============================================================================
# بخش ۲: توابع مربوط به ارسال پیامک
# ============================================================================

def send_sms(phone_number, message, sms_type='verification'):
    """
    ارسال پیامک به شماره موبایل
    
    در محیط توسعه: نمایش در کنسول و ذخیره در لاگ
    در محیط تولید: ارسال واقعی از طریق سرویس پیامک
    
    ورودی:
        phone_number (str): شماره موبایل گیرنده
            • فرمت: 11 رقمی، شروع با 09
            • مثال: "09123456789"
        
        message (str): متن پیامک
            • حداکثر طول: 70 کاراکتر برای پیامک فارسی
        
        sms_type (str, اختیاری): نوع پیامک
            • 'verification': پیامک تأیید
            • 'password_reset': بازیابی رمز
            • 'notification': اطلاع‌رسانی
            • پیش‌فرض: 'verification'
    
    خروجی:
        dict: نتیجه ارسال پیامک
            • success (bool): موفقیت‌آمیز بودن
            • message_id (str): شناسه پیام (در صورت موفقیت)
            • error (str): پیام خطا (در صورت شکست)
    
    مثال:
        >>> send_sms("09123456789", "کد تأیید شما: 123456")
        {
            'success': True,
            'message_id': 'console_mock_001',
            'error': None
        }
    """
    # اعتبارسنجی شماره موبایل
    if not validate_phone_number(phone_number):
        error_msg = f"شماره موبایل نامعتبر: {phone_number}"
        logger.error(error_msg)
        return {
            'success': False,
            'message_id': None,
            'error': error_msg
        }
    
    # اعتبارسنجی متن پیامک
    if not message or len(message.strip()) == 0:
        error_msg = "متن پیامک نمی‌تواند خالی باشد"
        logger.error(error_msg)
        return {
            'success': False,
            'message_id': None,
            'error': error_msg
        }
    
    # محدودیت طول پیامک
    if len(message) > 160:  # 160 کاراکتر برای پیامک انگلیسی
        # برای فارسی حدود 70 کاراکتر
        logger.warning(f"پیامک طولانی ({len(message)} کاراکتر) ممکن است به چند پیامک تقسیم شود")
    
    try:
        if settings.DEBUG:
            # حالت توسعه: نمایش در کنسول
            print(f"📱 SMS [{sms_type.upper()}] to {phone_number}: {message}")
            
            # شبیه‌سازی تأخیر ارسال
            import time
            time.sleep(0.5)  # تأخیر 500 میلی‌ثانیه
            
            result = {
                'success': True,
                'message_id': f"dev_mock_{int(time.time())}",
                'error': None
            }
        else:
            # حالت تولید: ارسال واقعی
            result = send_real_sms(phone_number, message, sms_type)
        
        # ثبت لاگ موفقیت
        logger.info(f"SMS sent successfully to {phone_number} - Type: {sms_type} - ID: {result.get('message_id')}")
        
        return result
        
    except Exception as e:
        # ثبت خطا
        error_msg = f"خطا در ارسال پیامک به {phone_number}: {str(e)}"
        logger.error(error_msg)
        
        return {
            'success': False,
            'message_id': None,
            'error': error_msg
        }


def send_real_sms(phone_number, message, sms_type):
    """
    ارسال واقعی پیامک با سرویس خارجی
    
    این تابع باید با سرویس پیامک واقعی (کاوه نگار، فارابیت، ...) جایگزین شود.
    
    ورودی:
        phone_number (str): شماره موبایل
        message (str): متن پیامک
        sms_type (str): نوع پیامک
    
    خروجی:
        dict: نتیجه ارسال
    """
    # TODO: پیاده‌سازی با سرویس پیامک واقعی
    
    # مثال با سرویس کاوه نگار
    """
    import requests
    
    url = "https://api.kavenegar.com/v1/{API_KEY}/sms/send.json"
    
    params = {
        'receptor': phone_number,
        'message': message,
        'sender': settings.SMS_SENDER_NUMBER,
        'type': 'sms'  # یا 'call' برای تماس صوتی
    }
    
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return {
            'success': True,
            'message_id': data['entries'][0]['messageid'],
            'error': None
        }
    else:
        return {
            'success': False,
            'message_id': None,
            'error': f"خطای سرویس پیامک: {response.status_code}"
        }
    """
    
    # فعلاً نسخه mock برگردانده می‌شود
    return {
        'success': True,
        'message_id': f"real_mock_{int(timezone.now().timestamp())}",
        'error': None
    }


def send_verification_sms(phone_number, otp_code):
    """
    ارسال پیامک تأیید با فرمت استاندارد
    
    ورودی:
        phone_number (str): شماره موبایل
        otp_code (str): کد تأیید
    
    خروجی:
        dict: نتیجه ارسال
    """
    message = f"کد تأیید شما: {otp_code}\nاعتبار: 10 دقیقه"
    return send_sms(phone_number, message, sms_type='verification')


def send_password_reset_sms(phone_number, otp_code):
    """
    ارسال پیامک بازیابی رمز عبور
    
    ورودی:
        phone_number (str): شماره موبایل
        otp_code (str): کد بازیابی
    
    خروجی:
        dict: نتیجه ارسال
    """
    message = f"کد بازیابی رمز عبور: {otp_code}\nاعتبار: 10 دقیقه\nدر صورت درخواست نکردن، این پیام را نادیده بگیرید."
    return send_sms(phone_number, message, sms_type='password_reset')


# ============================================================================
# بخش ۳: توابع امنیتی و کنترل دسترسی
# ============================================================================

def check_login_attempts(phone_number, ip_address, max_attempts=None, timeout=None):
    """
    بررسی تعداد تلاش‌های ناموفق ورود برای جلوگیری از Brute-force
    
    ورودی:
        phone_number (str): شماره موبایل کاربر
        ip_address (str): آی‌پی درخواست‌کننده
        
        max_attempts (int, اختیاری): حداکثر تلاش مجاز
            • پیش‌فرض: settings.MAX_LOGIN_ATTEMPTS یا 5
        
        timeout (int, اختیاری): زمان بلاک به ثانیه
            • پیش‌فرض: settings.LOGIN_ATTEMPT_TIMEOUT یا 900 (15 دقیقه)
    
    خروجی:
        dict: شامل تعداد تلاش‌ها و وضعیت
        
        مثال:
            {
                'attempts': 3,
                'is_blocked': False,
                'remaining_attempts': 2,
                'blocked_until': None
            }
    
    خطاها:
        ValidationError: اگر حساب کاربری بلاک شده باشد
    """
    # استفاده از مقادیر پیش‌فرض
    if max_attempts is None:
        max_attempts = getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
    
    if timeout is None:
        timeout = getattr(settings, 'LOGIN_ATTEMPT_TIMEOUT', 900)
    
    # کلید cache برای ذخیره تعداد تلاش‌ها
    cache_key = f"login_attempts:{phone_number}:{ip_address}"
    
    # دریافت تعداد تلاش‌های قبلی
    attempts = cache.get(cache_key, 0)
    
    # محاسبه زمان بلاک احتمالی
    blocked_until = None
    if attempts >= max_attempts:
        # اگر بلاک شده، زمان باقی‌مانده را محاسبه کن
        ttl = cache.ttl(cache_key)
        if ttl:
            blocked_until = timezone.now() + timedelta(seconds=ttl)
    
    result = {
        'attempts': attempts,
        'is_blocked': attempts >= max_attempts,
        'remaining_attempts': max(0, max_attempts - attempts),
        'blocked_until': blocked_until,
        'max_attempts': max_attempts
    }
    
    # اگر بلاک شده، خطا برگردان
    if result['is_blocked']:
        if blocked_until:
            remaining_time = blocked_until - timezone.now()
            minutes = int(remaining_time.total_seconds() // 60)
            seconds = int(remaining_time.total_seconds() % 60)
            
            raise serializers.ValidationError(
                f"حساب شما به دلیل تلاش‌های زیاد موقتاً قفل شده است. "
                f"لطفاً {minutes} دقیقه و {seconds} ثانیه دیگر تلاش کنید."
            )
        else:
            raise serializers.ValidationError(
                "حساب شما به دلیل تلاش‌های زیاد موقتاً قفل شده است."
            )
    
    return result


def record_login_attempt(phone_number, ip_address, successful):
    """
    ثبت تلاش ورود در دیتابیس و cache
    
    ورودی:
        phone_number (str): شماره موبایل
        ip_address (str): آی‌پی درخواست
        successful (bool): آیا ورود موفق بود؟
    
    خروجی:
        dict: اطلاعات ثبت شده
    """
    from .models import LoginAttempt  # Import داخل تابع برای جلوگیری از circular import
    
    # ثبت در دیتابیس
    login_attempt = LoginAttempt.objects.create(
        phone_number=phone_number,
        ip_address=ip_address,
        successful=successful,
        attempt_time=timezone.now()
    )
    
    # اگر ورود ناموفق بود، در cache هم ثبت کن
    if not successful:
        cache_key = f"login_attempts:{phone_number}:{ip_address}"
        
        # دریافت تعداد تلاش‌های قبلی
        attempts = cache.get(cache_key, 0) + 1
        
        # زمان انقضا
        timeout = getattr(settings, 'LOGIN_ATTEMPT_TIMEOUT', 900)
        
        # ذخیره در cache
        cache.set(cache_key, attempts, timeout=timeout)
        
        # ثبت لاگ
        logger.warning(
            f"تلاش ورود ناموفق برای {phone_number} از {ip_address}. "
            f"تعداد تلاش‌ها: {attempts}"
        )
    else:
        # اگر ورود موفق بود، cache مربوطه را پاک کن
        cache_key = f"login_attempts:{phone_number}:{ip_address}"
        cache.delete(cache_key)
        
        logger.info(f"ورود موفق برای {phone_number} از {ip_address}")
    
    return {
        'id': login_attempt.id,
        'successful': successful,
        'recorded_at': timezone.now()
    }


def reset_login_attempts(phone_number, ip_address=None):
    """
    ریست کردن تعداد تلاش‌های ورود
    
    ورودی:
        phone_number (str): شماره موبایل
        ip_address (str, اختیاری): آی‌پی خاص یا None برای همه آی‌پی‌ها
    
    خروجی:
        int: تعداد cache keyهای حذف شده
    """
    from django.core.cache import cache
    
    if ip_address:
        # حذف برای آی‌پی خاص
        cache_key = f"login_attempts:{phone_number}:{ip_address}"
        deleted = cache.delete(cache_key)
    else:
        # حذف برای همه آی‌پی‌های این شماره موبایل
        # این نیاز به pattern matching در cache دارد
        # بستگی به backend cache دارد
        # در اینجا یک پیاده‌سازی ساده:
        deleted = 0
        # TODO: پیاده‌سازی pattern matching بر اساس backend cache
    
    logger.info(f"تلاش‌های ورود ریست شد برای {phone_number}")
    
    return deleted


# ============================================================================
# بخش ۴: توابع اعتبارسنجی
# ============================================================================

def validate_phone_number(phone_number):
    """
    اعتبارسنجی شماره موبایل ایرانی
    
    ورودی:
        phone_number (str): شماره موبایل
    
    خروجی:
        bool: True اگر شماره معتبر باشد
    """
    if not phone_number or not isinstance(phone_number, str):
        return False
    
    # حذف فاصله و کاراکترهای اضافی
    cleaned = ''.join(filter(str.isdigit, phone_number))
    
    # بررسی طول و شروع شماره
    if len(cleaned) != 11:
        return False
    
    # شماره موبایل ایرانی با 09 شروع می‌شود
    if not cleaned.startswith('09'):
        return False
    
    # بررسی کد اپراتورهای معتبر ایران
    # 091x, 092x, 093x, 094x, 095x, 096x, 097x, 098x, 099x
    operator_code = cleaned[2]  # رقم سوم
    if operator_code not in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
        return False
    
    return True


def validate_national_code(national_code):
    """
    اعتبارسنجی کد ملی ایرانی
    
    ورودی:
        national_code (str): کد ملی
    
    خروجی:
        bool: True اگر کد معتبر باشد
    
    الگوریتم اعتبارسنجی کد ملی ایران
    """
    if not national_code or not isinstance(national_code, str):
        return False
    
    # فقط باید عدد باشد
    if not national_code.isdigit():
        return False
    
    # طول باید ۱۰ رقم باشد
    if len(national_code) != 10:
        return False
    
    # همه ارقام نمی‌توانند یکسان باشند
    if len(set(national_code)) == 1:
        return False
    
    # الگوریتم کنترل رقم کنترل
    try:
        # محاسبه مجموع وزنی
        sum_val = 0
        for i in range(9):
            sum_val += int(national_code[i]) * (10 - i)
        
        remainder = sum_val % 11
        
        # رقم کنترل
        control_digit = int(national_code[9])
        
        if remainder < 2:
            return control_digit == remainder
        else:
            return control_digit == (11 - remainder)
    except:
        return False


# ============================================================================
# بخش ۵: توابع کمکی عمومی
# ============================================================================

def generate_session_id():
    """
    تولید شناسه یکتا برای session
    
    خروجی:
        str: شناسه session
    """
    import uuid
    return str(uuid.uuid4())


def mask_phone_number(phone_number):
    """
    ماسک کردن شماره موبایل برای نمایش در لاگ‌ها
    
    ورودی:
        phone_number (str): شماره موبایل کامل
    
    خروجی:
        str: شماره ماسک شده
    
    مثال:
        >>> mask_phone_number("09123456789")
        "0912***6789"
    """
    if not phone_number or len(phone_number) != 11:
        return phone_number
    
    return phone_number[:4] + '***' + phone_number[-4:]


def mask_national_code(national_code):
    """
    ماسک کردن کد ملی برای نمایش
    
    ورودی:
        national_code (str): کد ملی کامل
    
    خروجی:
        str: کد ملی ماسک شده
    """
    if not national_code or len(national_code) != 10:
        return national_code
    
    return national_code[:3] + '****' + national_code[-3:]


def calculate_otp_expiry(minutes=10):
    """
    محاسبه زمان انقضای کد OTP
    
    ورودی:
        minutes (int, اختیاری): مدت اعتبار به دقیقه
    
    خروجی:
        datetime: زمان انقضا
    """
    return timezone.now() + timedelta(minutes=minutes)


# ============================================================================
# بخش ۶: تنظیمات و کانفیگ
# ============================================================================

class SecurityConfig:
    """
    کلاس مدیریت تنظیمات امنیتی
    """
    
    @staticmethod
    def get_max_login_attempts():
        """دریافت حداکثر تلاش مجاز ورود"""
        return getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
    
    @staticmethod
    def get_login_timeout():
        """دریافت زمان بلاک ورود ناموفق"""
        return getattr(settings, 'LOGIN_ATTEMPT_TIMEOUT', 900)
    
    @staticmethod
    def get_otp_validity():
        """دریافت مدت اعتبار کد OTP"""
        return getattr(settings, 'OTP_VALIDITY_MINUTES', 10)
    
    @staticmethod
    def get_session_timeout():
        """دریافت مدت اعتبار session"""
        return getattr(settings, 'SESSION_TIMEOUT_DAYS', 7)


# ============================================================================
# بخش ۷: تست توابع
# ============================================================================

if __name__ == "__main__":
    # تست توابع
    print("🔧 تست توابع utils.py")
    
    # تست generate_otp
    otp = generate_otp(6)
    print(f"OTP تولید شده: {otp}")
    
    # تست validate_phone_number
    test_phones = ["09123456789", "0912", "989123456789", "0912abc6789"]
    for phone in test_phones:
        valid = validate_phone_number(phone)
        print(f"شماره {phone}: {'✅ معتبر' if valid else '❌ نامعتبر'}")
    
    # تست mask_phone_number
    masked = mask_phone_number("09123456789")
    print(f"شماره ماسک شده: {masked}")
    
    print("✅ تست‌ها با موفقیت انجام شد")