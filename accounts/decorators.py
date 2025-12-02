"""
دکوراتورهای کمکی برای سیستم احراز هویت
"""

from functools import wraps
from .models import SecurityLog


def log_security_action(action, details_func=None):
    """
    دکوراتور برای ثبت خودکار لاگ امنیتی پس از اجرای view
    
    این دکوراتور به صورت خودکار پس از اجرای هر view،
    یک لاگ امنیتی در دیتابیس ثبت می‌کند.
    
    پارامترهای ورودی:
        action (str): 
            نوع عملیات انجام شده (مطابق با ACTION_CHOICES در SecurityLog)
            مثال: 'LOGIN_SUCCESS', 'USER_CREATED', 'ROLE_CHANGED'
        
        details_func (callable, اختیاری):
            تابعی که جزئیات لاگ را تولید می‌کند.
            این تابع دو پارامتر می‌گیرد: request و response
            و باید یک دیکشنری برگرداند.
    
    خروجی:
        دکوراتور پوشاننده view function
    
    مثال استفاده:
    
    1. استفاده ساده:
        @log_security_action('LOGIN_SUCCESS')
        def login_view(request):
            # منطق ورود
            return Response(...)
    
    2. استفاده با تابع جزئیات:
        def get_login_details(request, response):
            return {
                'user_id': request.user.id,
                'login_time': timezone.now().isoformat(),
                'status_code': response.status_code
            }
        
        @log_security_action('LOGIN_SUCCESS', get_login_details)
        def login_view(request):
            # منطق ورود
            return Response(...)
    """
    
    def decorator(view_func):
        """
        دکوراتور داخلی که view function را می‌پوشاند
        
        ورودی:
            view_func (callable): تابع view اصلی Django/DRF
        
        خروجی:
            wrapped_view (callable): تابع view پوشانده شده
        """
        
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            """
            تابع پوشاننده که قبل و بعد از view اجرا می‌شود
            
            مراحل اجرا:
                1. اجرای view اصلی و گرفتن response
                2. ثبت لاگ امنیتی
                3. بازگرداندن response به کاربر
            
            ورودی:
                request (HttpRequest): شیء درخواست Django
                *args: آرگومان‌های اضافی
                **kwargs: آرگومان‌های کلیدواژه
            
            خروجی:
                HttpResponse: پاسخ view اصلی
            """
            
            # 1. اجرای view اصلی
            response = view_func(request, *args, **kwargs)
            
            # 2. آماده‌سازی جزئیات لاگ
            details = {}
            if details_func:
                # اگر تابع جزئیات ارسال شده، آن را اجرا کن
                try:
                    details = details_func(request, response)
                except Exception as e:
                    # در صورت خطا، جزئیات خطا را ثبت کن
                    details = {
                        'error': str(e),
                        'details_func_error': True
                    }
            
            # 3. ثبت لاگ امنیتی در دیتابیس
            try:
                SecurityLog.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    action=action,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    details=details
                )
            except Exception as e:
                # اگر ثبت لاگ با خطا مواجه شد، view همچنان اجرا شود
                # (لاگ‌گیری نباید روی عملکرد اصلی اثر بگذارد)
                print(f"⚠️ خطا در ثبت لاگ امنیتی: {e}")
                # می‌توانید اینجا به سیستم لاگ‌گیری حرفه‌ای مثل Sentry هم گزارش دهید
            
            # 4. بازگرداندن response اصلی
            return response
        
        return wrapped_view
    
    return decorator


# ----------------------------------------------------------------------
# دکوراتورهای کمکی اضافی
# ----------------------------------------------------------------------

def require_phone_verified(view_func):
    """
    دکوراتور برای اجبار به تأیید موبایل قبل از دسترسی
    
    این دکوراتور بررسی می‌کند که کاربر موبایل خود را تأیید کرده باشد.
    در غیر این صورت دسترسی رد می‌شود.
    
    ورودی:
        view_func (callable): تابع view اصلی
    
    خروجی:
        wrapped_view (callable): تابع view پوشانده شده
    
    مثال استفاده:
        @require_phone_verified
        def sensitive_action(request):
            # فقط اگر موبایل تأیید شده باشد اجرا می‌شود
            return Response(...)
    """
    
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # بررسی احراز هویت
        if not request.user.is_authenticated:
            from rest_framework.response import Response
            from rest_framework import status
            return Response(
                {"error": "نیاز به ورود به سیستم دارید"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # بررسی تأیید موبایل
        if not request.user.phone_verified:
            from rest_framework.response import Response
            from rest_framework import status
            return Response(
                {
                    "error": "لطفاً ابتدا شماره موبایل خود را تأیید کنید",
                    "requires_verification": True,
                    "verification_endpoint": "/api/accounts/verify-phone/"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # اجرای view اصلی
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def rate_limit(max_requests, time_window):
    """
    دکوراتور برای محدود کردن تعداد درخواست‌ها
    
    این دکوراتور از حملات Brute-force جلوگیری می‌کند
    با محدود کردن تعداد درخواست‌ها در بازه زمانی مشخص.
    
    پارامترهای ورودی:
        max_requests (int): حداکثر تعداد درخواست مجاز
        time_window (int): بازه زمانی به ثانیه
    
    خروجی:
        دکوراتور پوشاننده view function
    
    مثال استفاده:
        @rate_limit(max_requests=5, time_window=60)  # 5 درخواست در دقیقه
        def login_view(request):
            return Response(...)
    """
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            from django.core.cache import cache
            from rest_framework.response import Response
            from rest_framework import status
            
            # ایجاد کلید منحصر به فرد برای کاربر
            user_ip = request.META.get('REMOTE_ADDR', '')
            view_name = view_func.__name__
            cache_key = f"rate_limit:{view_name}:{user_ip}"
            
            # دریافت تعداد درخواست‌های قبلی
            request_count = cache.get(cache_key, 0)
            
            # بررسی محدودیت
            if request_count >= max_requests:
                return Response(
                    {
                        "error": "تعداد درخواست‌های شما بیش از حد مجاز است",
                        "retry_after": time_window,
                        "max_requests": max_requests,
                        "time_window_seconds": time_window
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                    headers={'Retry-After': str(time_window)}
                )
            
            # افزایش شمارنده
            cache.set(cache_key, request_count + 1, timeout=time_window)
            
            # اجرای view اصلی
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    
    return decorator


def track_user_activity(activity_type):
    """
    دکوراتور برای ردیابی فعالیت‌های کاربر
    
    این دکوراتور علاوه بر ثبت لاگ امنیتی،
    اطلاعات فعالیت کاربر را برای آنالیز رفتاری ذخیره می‌کند.
    
    پارامتر ورودی:
        activity_type (str): نوع فعالیت کاربر
    
    خروجی:
        دکوراتور پوشاننده view function
    """
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            from django.utils import timezone
            from .models import UserActivity  # فرض می‌کنیم این مدل وجود دارد
            
            # اجرای view اصلی
            response = view_func(request, *args, **kwargs)
            
            # ثبت فعالیت کاربر (اگر لاگین کرده باشد)
            if request.user.is_authenticated:
                try:
                    UserActivity.objects.create(
                        user=request.user,
                        activity_type=activity_type,
                        endpoint=request.path,
                        method=request.method,
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:200],
                        timestamp=timezone.now()
                    )
                except Exception as e:
                    # ثبت خطا بدون تأثیر روی پاسخ اصلی
                    print(f"⚠️ خطا در ثبت فعالیت کاربر: {e}")
            
            return response
        
        return wrapped_view
    
    return decorator