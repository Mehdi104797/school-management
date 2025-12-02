"""
ViewSet‌های مربوط به سیستم احراز هویت و مدیریت کاربران

هر ViewSet مسئولیت زیر را دارد:
1. دریافت درخواست‌های HTTP
2. اعتبارسنجی داده‌ها (با Serializer)
3. اجرای منطق کسب‌وکار
4. بازگرداندن پاسخ مناسب
"""

import logging
from datetime import timedelta

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db import models

# Import داخلی‌های پروژه
from .models import User, UserSession, PasswordResetOTP, LoginAttempt, SecurityLog
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ProfileSerializer,
    UserSerializer,
    RoleSerializer,
    ForgotPasswordSerializer,
    VerifyOTPSerializer,
    PhoneVerificationSerializer,
    RoleChangeSerializer,
)
from .permissions import (
    IsAdmin,
    IsTeacher,
    TeacherOrAdminPermission
)
from .utils import (
    generate_otp,
    send_sms,
    check_login_attempts,
    record_login_attempt,
    send_verification_sms,
    send_password_reset_sms,
    calculate_otp_expiry,
)
from .decorators import log_security_action

# تنظیمات لاگ‌گیری
logger = logging.getLogger(__name__)


# ============================================================================
# 1. RegisterViewSet - ثبت‌نام کاربر جدید
# ============================================================================

class RegisterViewSet(viewsets.GenericViewSet):
    """
    ViewSet برای ثبت‌نام کاربران جدید در سیستم
    
    Endpoint:
        POST /api/accounts/register/
    
    دسترسی:
        عمومی (نیاز به احراز هویت ندارد)
    
    ورودی:
        JSON مطابق RegisterSerializer
    
    خروجی:
        JSON با پیام موفقیت و کد وضعیت 201
    """
    
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    @log_security_action('USER_CREATED')
    def create(self, request):
        """
        ایجاد کاربر جدید
        
        ورودی API:
            {
                "phone_number": "09123456789",
                "national_code": "1234567890",
                "password": "password123",
                "first_name": "علی",
                "last_name": "محمدی",
                ...
            }
        
        خروجی:
            {
                "message": "ثبت‌نام با موفقیت انجام شد",
                "user_id": 1
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # ذخیره کاربر در دیتابیس
        user = serializer.save()
        
        # ثبت لاگ امنیتی (با دکوراتور log_security_action)
        
        return Response(
            {
                "message": "ثبت‌نام با موفقیت انجام شد",
                "user_id": user.id,
                "phone_number": user.phone_number
            },
            status=status.HTTP_201_CREATED
        )


# ============================================================================
# 2. LoginViewSet - ورود کاربر به سیستم
# ============================================================================

class LoginViewSet(viewsets.GenericViewSet):
    """
    ViewSet برای احراز هویت و ورود کاربران
    
    Endpoint:
        POST /api/accounts/login/
    
    دسترسی:
        عمومی (نیاز به احراز هویت ندارد)
    
    خروجی:
        JSON حاوی access_token, refresh_token و اطلاعات کاربر
    """
    
    serializer_class = LoginSerializer

    @log_security_action('LOGIN_SUCCESS')
    def create(self, request):
        """
        احراز هویت کاربر و تولید توکن JWT
        
        مراحل:
        1. بررسی محدودیت تلاش‌های ورود
        2. اعتبارسنجی اطلاعات ورودی
        3. احراز هویت کاربر
        4. ثبت تلاش موفق
        5. تولید توکن‌های JWT
        6. ذخیره session در دیتابیس
        
        ورودی API:
            {
                "phone_number": "09123456789",
                "password": "password123"
            }
        
        خروجی:
            {
                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "user_id": 1,
                "phone_number": "09123456789",
                "role": "student",
                "phone_verified": false
            }
        """
        phone_number = request.data.get('phone_number')
        ip_address = request.META.get('REMOTE_ADDR')
        
        # مرحله ۱: بررسی محدودیت تلاش‌های ورود
        try:
            attempts_info = check_login_attempts(phone_number, ip_address)
            logger.debug(f"تلاش ورود برای {phone_number} - وضعیت: {attempts_info}")
        except Exception as e:
            # ثبت تلاش ناموفق برای لاگ‌گیری
            record_login_attempt(phone_number, ip_address, False)
            return Response(
                {"error": str(e)},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # مرحله ۲: اعتبارسنجی اطلاعات ورودی
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # ثبت تلاش ناموفق
            record_login_attempt(phone_number, ip_address, False)
            
            # افزایش شمارنده تلاش‌های ناموفق
            from django.core.cache import cache
            cache_key = f"login_attempts:{phone_number}:{ip_address}"
            attempts = cache.get(cache_key, 0) + 1
            cache.set(cache_key, attempts, timeout=900)  # 15 دقیقه
            
            raise serializers.ValidationError(serializer.errors)
        
        # مرحله ۳: احراز هویت کاربر
        user = serializer.validated_data['user']
        
        # بررسی فعال بودن حساب کاربری
        if not user.is_active:
            record_login_attempt(phone_number, ip_address, False)
            return Response(
                {"error": "حساب کاربری غیرفعال است"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # مرحله ۴: ثبت تلاش موفق
        record_login_attempt(phone_number, ip_address, True)
        
        # پاک کردن cache مربوط به تلاش‌های ناموفق
        from django.core.cache import cache
        cache_key = f"login_attempts:{phone_number}:{ip_address}"
        cache.delete(cache_key)
        
        # مرحله ۵: تولید توکن‌های JWT
        refresh = RefreshToken.for_user(user)
        
        # مرحله ۶: ذخیره session در دیتابیس
        UserSession.objects.create(
            user=user,
            refresh_token=str(refresh),
            ip=ip_address,
            device=request.META.get('HTTP_USER_AGENT', '')[:200],
            # expires_at=timezone.now() + timedelta(days=7)
        )
        
        # مرحله ۷: بازگرداندن پاسخ
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": user.id,
            "phone_number": user.phone_number,
            "role": user.role,
            "phone_verified": user.phone_verified,
            "full_name": f"{user.first_name} {user.last_name}",
            "expires_in": 3600  # زمان انقضای access_token به ثانیه
        })


# ============================================================================
# 3. LogoutViewSet - خروج کاربر از سیستم
# ============================================================================

class LogoutViewSet(viewsets.GenericViewSet):
    """
    ViewSet برای خروج کاربر و باطل کردن session
    
    Endpoint:
        POST /api/accounts/logout/
    
    دسترسی:
        نیاز به احراز هویت دارد
    """
    
    permission_classes = [IsAuthenticated]

    @log_security_action('LOGOUT')
    def create(self, request):
        """
        خروج کاربر و باطل کردن session
        
        ورودی API:
            {
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        
        خروجی:
            {
                "message": "خروج با موفقیت انجام شد"
            }
        """
        refresh_token = request.data.get("refresh")
        
        if refresh_token:
            # حذف session مربوطه از دیتابیس
            deleted_count = UserSession.objects.filter(
                user=request.user,
                refresh_token=refresh_token
            ).delete()[0]
            
            logger.info(f"Session حذف شد برای کاربر {request.user.phone_number} - تعداد: {deleted_count}")
            
            # سعی در باطل کردن توکن (اگر blacklist فعال باشد)
            try:
                from rest_framework_simplejwt.tokens import RefreshToken
                token = RefreshToken(refresh_token)
                token.blacklist()
                logger.debug(f"توکن refresh باطل شد: {refresh_token[:20]}...")
            except Exception as e:
                logger.warning(f"خطا در باطل کردن توکن: {str(e)}")
        
        return Response({
            "message": "خروج با موفقیت انجام شد"
        })


# ============================================================================
# 4. ProfileViewSet - مدیریت پروفایل کاربر
# ============================================================================

class ProfileViewSet(viewsets.GenericViewSet):
    """
    ViewSet برای نمایش و ویرایش پروفایل کاربر جاری
    
    Endpointها:
        GET /api/accounts/profile/    - مشاهده پروفایل
        PATCH /api/accounts/profile/  - ویرایش پروفایل
    
    دسترسی:
        نیاز به احراز هویت دارد
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    @log_security_action('PROFILE_VIEWED')
    def list(self, request):
        """
        نمایش پروفایل کاربر جاری
        
        خروجی:
            {
                "phone_number": "09123456789",
                "national_code": "1234567890",
                "first_name": "علی",
                "last_name": "محمدی",
                "phone_verified": true,
                ...
            }
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @log_security_action('PROFILE_UPDATED')
    def partial_update(self, request):
        """
        ویرایش پروفایل کاربر جاری
        
        ورودی API:
            {
                "first_name": "علی",
                "last_name": "احمدی",
                "city": "مشهد"
            }
        
        خروجی:
            {
                "message": "پروفایل با موفقیت بروزرسانی شد",
                "updated_fields": ["first_name", "last_name", "city"]
            }
        """
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # شناسایی فیلدهای تغییر کرده
        updated_fields = list(request.data.keys())
        
        return Response({
            "message": "پروفایل با موفقیت بروزرسانی شد",
            "updated_fields": updated_fields
        })


# ============================================================================
# 5. AdminViewSet - پنل مدیریت ادمین
# ============================================================================

class AdminViewSet(viewsets.ModelViewSet):
    """
    ViewSet برای مدیریت کاربران توسط ادمین
    
    Endpointها:
        GET    /api/accounts/admin-panel/          - لیست تمام کاربران
        GET    /api/accounts/admin-panel/{id}/     - مشاهده کاربر خاص
        PUT    /api/accounts/admin-panel/{id}/     - ویرایش کامل کاربر
        PATCH  /api/accounts/admin-panel/{id}/     - ویرایش جزئی کاربر
        DELETE /api/accounts/admin-panel/{id}/     - حذف کاربر
    
    دسترسی:
        فقط کاربران با نقش admin
    """
    
    permission_classes = [IsAdmin]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    
    def get_queryset(self):
        """
        فیلتر کردن کاربران بر اساس پارامترهای جستجو
        
        پارامترهای query string پشتیبانی شده:
            ?role=student      - فیلتر بر اساس نقش
            ?is_active=true    - فیلتر بر اساس وضعیت فعال
            ?phone_verified=true - فیلتر بر اساس تأیید موبایل
            ?search=0912       - جستجو در شماره موبایل و نام
        """
        queryset = User.objects.all()
        
        # فیلتر بر اساس نقش
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # فیلتر بر اساس وضعیت فعال
        is_active = self.request.query_params.get('is_active')
        if is_active:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        # فیلتر بر اساس تأیید موبایل
        phone_verified = self.request.query_params.get('phone_verified')
        if phone_verified:
            phone_verified_bool = phone_verified.lower() == 'true'
            queryset = queryset.filter(phone_verified=phone_verified_bool)
        
        # جستجوی ترکیبی
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(phone_number__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(national_code__icontains=search)
            )
        
        return queryset
    
    @log_security_action('USER_UPDATED_ADMIN')
    def update(self, request, *args, **kwargs):
        """ویرایش کاربر توسط ادمین"""
        return super().update(request, *args, **kwargs)
    
    @log_security_action('USER_DELETED')
    def destroy(self, request, *args, **kwargs):
        """حذف کاربر توسط ادمین"""
        return super().destroy(request, *args, **kwargs)


# ============================================================================
# 6. TeacherViewSet - پنل مدیریت معلم
# ============================================================================

class TeacherViewSet(viewsets.ViewSet):
    """
    ViewSet برای پنل اختصاصی معلم‌ها
    
    Endpoint:
        GET /api/accounts/teacher-panel/
    
    دسترسی:
        فقط کاربران با نقش teacher
    """
    
    permission_classes = [IsTeacher]

    def list(self, request):
        """
        نمایش پنل معلم
        
        در آینده می‌توان اطلاعات زیر را اضافه کرد:
            - لیست کلاس‌های تدریس
            - لیست دانش‌آموزان
            - برنامه هفتگی
            - نمرات و گزارشات
        """
        # در اینجا می‌توانید اطلاعات خاص معلم را از دیتابیس بخوانید
        # برای نمونه:
        
        teacher_info = {
            "message": "به پنل معلم خوش آمدید!",
            "teacher": {
                "full_name": f"{request.user.first_name} {request.user.last_name}",
                "phone_number": request.user.phone_number,
                "city": request.user.city or "تعیین نشده"
            },
            "features": [
                "مدیریت کلاس‌ها",
                "ثبت نمرات",
                "گزارش‌گیری",
                "ارتباط با دانش‌آموزان"
            ],
            "stats": {
                "total_classes": 0,  # بعداً از دیتابیس محاسبه شود
                "total_students": 0,
                "active_sessions": 1
            }
        }
        
        return Response(teacher_info)


# ============================================================================
# 7. ForgotPasswordViewSet - بازیابی رمز عبور
# ============================================================================

class ForgotPasswordViewSet(viewsets.GenericViewSet):
    """
    ViewSet برای درخواست کد بازیابی رمز عبور
    
    Endpoint:
        POST /api/accounts/forgot-password/
    
    دسترسی:
        عمومی (نیاز به احراز هویت ندارد)
    """
    
    serializer_class = ForgotPasswordSerializer

    @log_security_action('PASSWORD_RESET_REQUESTED')
    def create(self, request):
        """
        ارسال کد OTP برای بازیابی رمز عبور
        
        ورودی API:
            {
                "phone_number": "09123456789"
            }
        
        خروجی:
            {
                "message": "کد بازیابی ارسال شد",
                "expires_in": "10 دقیقه",
                "masked_phone": "0912***6789"
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        user = User.objects.get(phone_number=phone_number)
        
        # حذف OTPهای قبلی برای این کاربر
        PasswordResetOTP.objects.filter(phone_number=phone_number).delete()
        
        # تولید کد OTP جدید
        otp_code = generate_otp()
        expires_at = calculate_otp_expiry(minutes=10)
        
        # ذخیره OTP در دیتابیس
        otp_record = PasswordResetOTP.objects.create(
            user=user,
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=expires_at
        )
        
        # ارسال پیامک
        sms_result = send_password_reset_sms(phone_number, otp_code)
        
        if not sms_result['success']:
            # اگر ارسال پیامک ناموفق بود، OTP را حذف کن
            otp_record.delete()
            logger.error(f"خطا در ارسال پیامک بازیابی رمز به {phone_number}")
            
            return Response(
                {"error": "خطا در ارسال پیامک. لطفاً دوباره تلاش کنید."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # ماسک کردن شماره برای نمایش در پاسخ
        masked_phone = phone_number[:4] + '***' + phone_number[-4:]
        
        # ثبت لاگ
        logger.info(f"OTP بازیابی رمز ارسال شد به {masked_phone}")
        
        return Response({
            "message": "کد بازیابی ارسال شد",
            "expires_in": "10 دقیقه",
            "masked_phone": masked_phone,
            "message_id": sms_result.get('message_id')
        }, status=status.HTTP_200_OK)


# ============================================================================
# 8. VerifyOTPViewSet - تأیید OTP و تغییر رمز
# ============================================================================

class VerifyOTPViewSet(viewsets.GenericViewSet):
    """
    ViewSet برای تأیید کد OTP و تغییر رمز عبور
    
    Endpoint:
        POST /api/accounts/verify-otp/
    
    دسترسی:
        عمومی (نیاز به احراز هویت ندارد)
    """
    
    serializer_class = VerifyOTPSerializer

    @log_security_action('PASSWORD_CHANGED')
    def create(self, request):
        """
        تأیید کد OTP و تنظیم رمز عبور جدید
        
        ورودی API:
            {
                "phone_number": "09123456789",
                "otp_code": "123456",
                "new_password": "newpassword123"
            }
        
        خروجی:
            {
                "message": "رمز عبور با موفقیت تغییر کرد"
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        otp_record = data['otp_record']
        new_password = data['new_password']
        
        # تغییر رمز عبور کاربر
        user = otp_record.user
        user.set_password(new_password)
        user.save()
        
        # علامت‌گذاری OTP به عنوان استفاده شده
        otp_record.is_used = True
        otp_record.save()
        
        # حذف تمام sessionهای قبلی کاربر (برای امنیت)
        deleted_sessions = UserSession.objects.filter(user=user).delete()[0]
        
        # ثبت لاگ
        logger.info(f"رمز عبور تغییر کرد برای کاربر {user.phone_number} - {deleted_sessions} session حذف شد")
        
        return Response({
            "message": "رمز عبور با موفقیت تغییر کرد",
            "sessions_revoked": deleted_sessions
        }, status=status.HTTP_200_OK)


# ============================================================================
# 9. PhoneVerificationViewSet - تأیید شماره موبایل
# ============================================================================

class PhoneVerificationViewSet(viewsets.GenericViewSet):
    """
    ViewSet برای تأیید شماره موبایل کاربر
    
    Endpointها:
        POST /api/accounts/verify-phone/verify/      - تأیید کد
        POST /api/accounts/verify-phone/resend/      - ارسال مجدد کد
    
    دسترسی:
        نیاز به احراز هویت دارد
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = PhoneVerificationSerializer

    @action(detail=False, methods=['post'], url_path='verify')
    @log_security_action('PHONE_VERIFIED')
    def verify_phone(self, request):
        """
        تأیید شماره موبایل با کد ارسالی
        
        ورودی API:
            {
                "phone_number": "09123456789",
                "verification_code": "123456"
            }
        
        خروجی:
            {
                "message": "شماره موبایل با موفقیت تأیید شد",
                "verified_at": "2024-01-15T10:30:00Z"
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # در اینجا باید منطق تأیید کد OTP پیاده‌سازی شود
        # برای نمونه ساده، کد ثابت را بررسی می‌کنیم
        
        verification_code = serializer.validated_data['verification_code']
        phone_number = serializer.validated_data['phone_number']
        
        # بررسی تطابق شماره موبایل با کاربر جاری
        if phone_number != request.user.phone_number:
            return Response({
                "error": "شماره موبایل با حساب کاربری شما مطابقت ندارد"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: اینجا باید با OTP ذخیره شده در دیتابیس مقایسه شود
        # برای نمونه ساده، کد 123456 را معتبر در نظر می‌گیریم
        
        if verification_code == "123456":  # باید با OTP واقعی جایگزین شود
            user = request.user
            user.phone_verified = True
            user.phone_verified_at = timezone.now()
            user.save()
            
            # ثبت لاگ امنیتی
            SecurityLog.objects.create(
                user=user,
                action='PHONE_VERIFIED',
                ip_address=request.META.get('REMOTE_ADDR'),
                details={
                    'phone_number': phone_number,
                    'verification_method': 'SMS'
                }
            )
            
            return Response({
                "message": "شماره موبایل با موفقیت تأیید شد",
                "verified_at": user.phone_verified_at.isoformat(),
                "phone_number": phone_number
            })
        
        # اگر کد نامعتبر بود
        return Response({
            "error": "کد تأیید نامعتبر است",
            "hint": "کد 123456 برای محیط توسعه معتبر است"
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='resend')
    @log_security_action('PHONE_VERIFICATION_RESENT')
    def resend_code(self, request):
        """
        ارسال مجدد کد تأیید
        
        ورودی API:
            {
                "phone_number": "09123456789"
            }
        
        خروجی:
            {
                "message": "کد تأیید مجدداً ارسال شد",
                "expires_in": "10 دقیقه"
            }
        """
        phone_number = request.data.get('phone_number')
        
        if not phone_number:
            return Response({
                "error": "شماره موبایل الزامی است"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # بررسی تطابق شماره موبایل
        if phone_number != request.user.phone_number:
            return Response({
                "error": "شماره موبایل با حساب کاربری شما مطابقت ندارد"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # تولید و ارسال کد جدید
        otp_code = generate_otp()
        
        # TODO: ذخیره OTP در دیتابیس برای تأیید بعدی
        
        # ارسال پیامک
        sms_result = send_verification_sms(phone_number, otp_code)
        
        if sms_result['success']:
            return Response({
                "message": "کد تأیید مجدداً ارسال شد",
                "expires_in": "10 دقیقه",
                "masked_phone": phone_number[:4] + '***' + phone_number[-4:]
            })
        else:
            return Response({
                "error": "خطا در ارسال پیامک",
                "detail": sms_result.get('error')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# 10. RoleManagementViewSet - مدیریت نقش کاربران
# ============================================================================

class RoleManagementViewSet(viewsets.GenericViewSet):
    """
    ViewSet برای مدیریت نقش کاربران (فقط برای ادمین)
    
    Endpointها:
        GET /api/accounts/role-management/         - لیست کاربران و آمار
        POST /api/accounts/role-management/change_role/ - تغییر نقش کاربر
    
    دسترسی:
        فقط کاربران با نقش admin
    """
    
    permission_classes = [IsAdmin]

    @action(detail=False, methods=['get'])
    def list_roles(self, request):
        """
        لیست کاربران بر اساس نقش و آمار سیستم
        
        پارامترهای query string:
            ?role=student - فیلتر بر اساس نقش
        
        خروجی:
            {
                "stats": {
                    "total_users": 150,
                    "admin_count": 5,
                    "teacher_count": 20,
                    "student_count": 125,
                    "active_users": 140,
                    "phone_verified": 130
                },
                "users": [...]
            }
        """
        role = request.query_params.get('role')
        
        if role:
            users = User.objects.filter(role=role)
        else:
            users = User.objects.all()
        
        # محاسبه آمار
        stats = {
            'total_users': User.objects.count(),
            'admin_count': User.objects.filter(role='admin').count(),
            'teacher_count': User.objects.filter(role='teacher').count(),
            'student_count': User.objects.filter(role='student').count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'phone_verified': User.objects.filter(phone_verified=True).count(),
            'staff_users': User.objects.filter(is_staff=True).count(),
        }
        
        # سریالایز کردن کاربران
        serializer = UserSerializer(users, many=True)
        
        return Response({
            "stats": stats,
            "users": serializer.data,
            "role_filter": role or "همه"
        })

    @action(detail=False, methods=['post'], url_path='change_role')
    @log_security_action('ROLE_CHANGED')
    def change_role(self, request):
        """
        تغییر نقش کاربر توسط ادمین
        
        ورودی API:
            {
                "user_id": 5,
                "new_role": "teacher",
                "reason": "ارتقا به مربی"
            }
        
        خروجی:
            {
                "message": "نقش کاربر 09123456789 به teacher تغییر کرد",
                "user": {...},
                "changed_by": "ادمین علی"
            }
        """
        serializer = RoleChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        new_role = serializer.validated_data['new_role']
        reason = serializer.validated_data.get('reason', '')
        
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "کاربر یافت نشد"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # جلوگیری از تغییر نقش ادمین اصلی
        if target_user.is_superuser and new_role != 'admin':
            return Response(
                {"error": "نقش ادمین اصلی قابل تغییر نیست"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # جلوگیری از تغییر نقش خود ادمین
        if target_user.id == request.user.id:
            return Response(
                {"error": "نمی‌توانید نقش خود را تغییر دهید"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        old_role = target_user.role
        target_user.role = new_role
        target_user.save()
        
        # ثبت لاگ امنیتی
        SecurityLog.objects.create(
            user=request.user,
            action='ROLE_CHANGED',
            ip_address=request.META.get('REMOTE_ADDR'),
            details={
                'target_user_id': user_id,
                'target_user_phone': target_user.phone_number,
                'old_role': old_role,
                'new_role': new_role,
                'reason': reason,
                'changed_by': request.user.phone_number,
                'changed_by_name': f"{request.user.first_name} {request.user.last_name}"
            }
        )
        
        # سریالایز کردن کاربر برای پاسخ
        user_serializer = UserSerializer(target_user)
        
        return Response({
            "message": f"نقش کاربر {target_user.phone_number} به {new_role} تغییر کرد",
            "user": user_serializer.data,
            "old_role": old_role,
            "new_role": new_role,
            "changed_by": f"{request.user.first_name} {request.user.last_name}",
            "timestamp": timezone.now().isoformat()
        })


# ============================================================================
# 11. SessionManagementViewSet - مدیریت نشست‌های کاربر
# ============================================================================

class SessionManagementViewSet(viewsets.GenericViewSet):
    """
    ViewSet برای مدیریت نشست‌های کاربر
    
    Endpointها:
        GET /api/accounts/session-management/                  - لیست نشست‌ها
        POST /api/accounts/session-management/revoke_session/  - ابطال یک نشست
        POST /api/accounts/session-management/revoke_all_sessions/ - ابطال همه نشست‌ها
    
    دسترسی:
        نیاز به احراز هویت دارد
    """
    
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    @log_security_action('SESSIONS_VIEWED')
    def list_sessions(self, request):
        """
        لیست نشست‌های فعال کاربر
        
        خروجی:
            [
                {
                    "id": 1,
                    "created_at": "2024-01-15T10:30:00Z",
                    "expires_at": "2024-01-22T10:30:00Z",
                    "ip": "192.168.1.100",
                    "device": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
                    "current": true,
                    "location": "تهران, ایران"  # در صورت امکان
                },
                ...
            ]
        """
        sessions = UserSession.objects.filter(
            user=request.user,
            expires_at__gt=timezone.now()
        ).order_by('-created_at')
        
        # شناسایی session جاری
        current_refresh_token = None
        if hasattr(request, 'auth') and hasattr(request.auth, 'refresh_token'):
            current_refresh_token = request.auth.refresh_token
        
        data = []
        for session in sessions:
            is_current = (session.refresh_token == current_refresh_token)
            
            session_data = {
                'id': session.id,
                'created_at': session.created_at,
                'expires_at': session.expires_at,
                'ip': session.ip,
                'device': session.device[:100],  # محدود کردن طول
                'current': is_current,
                'is_expired': session.expires_at <= timezone.now(),
                'duration_days': (session.expires_at - session.created_at).days
            }
            
            data.append(session_data)
        
        return Response(data)

    @action(detail=False, methods=['post'], url_path='revoke_session')
    @log_security_action('SESSION_REVOKED')
    def revoke_session(self, request):
        """
        ابطال یک نشست خاص
        
        ورودی API:
            {
                "session_id": 5
            }
        
        خروجی:
            {
                "message": "Session با موفقیت باطل شد",
                "session_id": 5
            }
        """
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response(
                {"error": "شناسه session الزامی است"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            session = UserSession.objects.get(
                id=session_id,
                user=request.user  # فقط sessionهای خود کاربر
            )
            
            # جلوگیری از ابطال session جاری
            current_refresh_token = None
            if hasattr(request, 'auth') and hasattr(request.auth, 'refresh_token'):
                current_refresh_token = request.auth.refresh_token
            
            if session.refresh_token == current_refresh_token:
                return Response(
                    {"error": "نمی‌توانید session جاری را باطل کنید"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # حذف session
            session.delete()
            
            # ثبت لاگ امنیتی
            SecurityLog.objects.create(
                user=request.user,
                action='SESSION_REVOKED',
                ip_address=request.META.get('REMOTE_ADDR'),
                details={
                    'session_id': session_id,
                    'session_ip': session.ip,
                    'session_device': session.device[:50]
                }
            )
            
            return Response({
                "message": "Session با موفقیت باطل شد",
                "session_id": session_id
            })
        
        except UserSession.DoesNotExist:
            return Response(
                {"error": "Session یافت نشد یا متعلق به شما نیست"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'], url_path='revoke_all_sessions')
    @log_security_action('SESSIONS_REVOKED_ALL')
    def revoke_all_sessions(self, request):
        """
        ابطال همه نشست‌های کاربر به جز نشست جاری
        
        خروجی:
            {
                "message": "3 Session باطل شد",
                "revoked_count": 3,
                "current_session_preserved": true
            }
        """
        # شناسایی session جاری
        current_refresh_token = None
        if hasattr(request, 'auth') and hasattr(request.auth, 'refresh_token'):
            current_refresh_token = request.auth.refresh_token
        
        # دریافت همه sessionهای کاربر
        sessions = UserSession.objects.filter(user=request.user)
        
        revoked_count = 0
        for session in sessions:
            # اگر session جاری بود، آن را حذف نکن
            if current_refresh_token and session.refresh_token == current_refresh_token:
                continue
            
            session.delete()
            revoked_count += 1
        
        # ثبت لاگ امنیتی
        SecurityLog.objects.create(
            user=request.user,
            action='SESSIONS_REVOKED_ALL',
            ip_address=request.META.get('REMOTE_ADDR'),
            details={'revoked_count': revoked_count}
        )
        
        return Response({
            "message": f"{revoked_count} Session باطل شد",
            "revoked_count": revoked_count,
            "current_session_preserved": current_refresh_token is not None
        })


# ============================================================================
# 12. AdminDashboardViewSet - داشبورد مدیریت ادمین
# ============================================================================

class AdminDashboardViewSet(viewsets.GenericViewSet):
    """
    ViewSet برای داشبورد آمار و گزارشات ادمین
    
    Endpoint:
        GET /api/accounts/admin-dashboard/dashboard_stats/
    
    دسترسی:
        فقط کاربران با نقش admin
    """
    
    permission_classes = [IsAdmin]

    @action(detail=False, methods=['get'], url_path='dashboard_stats')
    def dashboard_stats(self, request):
        """
        دریافت آمار کلی سیستم
        
        پارامترهای query string:
            ?range=daily   - آمار روزانه
            ?range=weekly  - آمار هفتگی
            ?range=monthly - آمار ماهانه
        
        خروجی:
            {
                "time_range": "daily",
                "period": {
                    "start": "2024-01-15T00:00:00Z",
                    "end": "2024-01-15T23:59:59Z"
                },
                "user_stats": {...},
                "login_stats": {...},
                "system_stats": {...},
                "role_distribution": {...},
                "recent_activities": [...]
            }
        """
        # تعیین بازه زمانی
        time_range = request.query_params.get('range', 'daily').lower()
        
        if time_range == 'daily':
            start_date = timezone.now() - timedelta(days=1)
        elif time_range == 'weekly':
            start_date = timezone.now() - timedelta(days=7)
        elif time_range == 'monthly':
            start_date = timezone.now() - timedelta(days=30)
        else:
            start_date = timezone.now() - timedelta(days=1)
            time_range = 'daily'
        
        # آمار کاربران
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        phone_verified_users = User.objects.filter(phone_verified=True).count()
        
        # آمار ورودها در بازه زمانی
        successful_logins = LoginAttempt.objects.filter(
            successful=True,
            attempt_time__gte=start_date
        ).count()
        
        failed_logins = LoginAttempt.objects.filter(
            successful=False,
            attempt_time__gte=start_date
        ).count()
        
        total_logins = successful_logins + failed_logins
        success_rate = (successful_logins / total_logins * 100) if total_logins > 0 else 0
        
        # آمار فعالیت‌های امنیتی
        recent_activities = SecurityLog.objects.filter(
            created_at__gte=start_date
        ).values('action').annotate(count=models.Count('id'))
        
        # sessionهای فعال
        active_sessions = UserSession.objects.filter(
            expires_at__gt=timezone.now()
        ).count()
        
        # کاربران جدید در بازه زمانی
        new_users = User.objects.filter(
            date_joined__gte=start_date
        ).count()
        
        # آمار بر اساس نقش
        role_stats = {}
        for role_code, role_name in User.ROLE_CHOICES:
            role_count = User.objects.filter(role=role_code).count()
            active_in_role = User.objects.filter(role=role_code, is_active=True).count()
            
            role_stats[role_code] = {
                'name': role_name,
                'count': role_count,
                'active': active_in_role,
                'percentage': (role_count / total_users * 100) if total_users > 0 else 0
            }
        
        # آخرین فعالیت‌های امنیتی
        recent_security_logs = SecurityLog.objects.all().order_by('-created_at')[:10].values(
            'action', 'user__phone_number', 'ip_address', 'created_at', 'details'
        )
        
        return Response({
            "time_range": time_range,
            "period": {
                "start": start_date.isoformat(),
                "end": timezone.now().isoformat()
            },
            "user_stats": {
                "total": total_users,
                "active": active_users,
                "inactive": total_users - active_users,
                "phone_verified": phone_verified_users,
                "phone_not_verified": total_users - phone_verified_users,
                "new_users": new_users
            },
            "login_stats": {
                "successful": successful_logins,
                "failed": failed_logins,
                "total": total_logins,
                "success_rate": round(success_rate, 2),
                "failed_rate": round(100 - success_rate, 2) if total_logins > 0 else 0
            },
            "system_stats": {
                "active_sessions": active_sessions,
                "expired_sessions": UserSession.objects.filter(
                    expires_at__lte=timezone.now()
                ).count(),
                "recent_activities": list(recent_activities),
                "pending_otps": PasswordResetOTP.objects.filter(
                    is_used=False,
                    expires_at__gt=timezone.now()
                ).count()
            },
            "role_distribution": role_stats,
            "recent_security_logs": list(recent_security_logs),
            "timestamps": {
                "generated_at": timezone.now().isoformat(),
                "cache_key": f"dashboard_stats_{time_range}_{timezone.now().date()}"
            }
        })