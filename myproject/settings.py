"""
تنظیمات پروژه myproject - سیستم احراز هویت مبتنی بر نقش

این فایل شامل تمام تنظیمات مورد نیاز برای:
1. پیکربندی پایه Django
2. احراز هویت و امنیت
3. تنظیمات REST Framework و JWT
4. تنظیمات پایگاه داده
5. تنظیمات بین‌المللی‌سازی
6. تنظیمات استاتیک و مدیا
"""

import os
from pathlib import Path
from datetime import timedelta
from django.utils.translation import gettext_lazy as _

# ============================================================================
# بخش ۱: مسیرها و تنظیمات پایه
# ============================================================================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# امنیت: کلید مخفی باید در محیط تولید از متغیرهای محیطی خوانده شود
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-vzrxfl(kc5ep0pcf#y4rwhhzu0^#k+zy*4c0w@htdd7vax0u0p')

# حالت دیباگ: در محیط تولید باید False باشد
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

# میزبان‌های مجاز
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',') if os.environ.get('DJANGO_ALLOWED_HOSTS') else ['localhost', '127.0.0.1']

# ============================================================================
# بخش ۲: تعریف برنامه‌های نصب شده
# ============================================================================

INSTALLED_APPS = [
    # برنامه‌های پیش‌فرض Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # برنامه‌های شخص ثالث
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',  # برای مدیریت CORS
    'drf_yasg',  # برای مستندسازی خودکار API (اختیاری)
    
    # برنامه‌های داخلی پروژه
    'accounts',  # اپلیکیشن احراز هویت ما
]

# ============================================================================
# بخش ۳: میدل‌ورها (Middleware)
# ============================================================================

MIDDLEWARE = [
    # میدل‌ورهای امنیتی و CORS
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS باید قبل از CommonMiddleware باشد
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # میدل‌ورهای عمومی
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # میدل‌ورهای سفارشی (در صورت نیاز)
    # 'accounts.middleware.SecurityHeadersMiddleware',  # مثال برای میدل‌ور سفارشی
]

# ============================================================================
# بخش ۴: تنظیمات URL و تمپلیت
# ============================================================================

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # پوشه تمپلیت‌های پروژه
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'

# ============================================================================
# بخش ۵: تنظیمات پایگاه داده
# ============================================================================

# استفاده از متغیرهای محیطی برای اتصال به دیتابیس
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}

# ============================================================================
# بخش ۶: اعتبارسنجی رمز عبور
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'max_similarity': 0.7,  # کاهش تشابه با اطلاعات کاربر
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # حداقل طول رمز عبور
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============================================================================
# بخش ۷: بین‌المللی‌سازی
# ============================================================================

LANGUAGE_CODE = 'fa-ir'  # فارسی ایران

TIME_ZONE = 'Asia/Tehran'  # زمان تهران

USE_I18N = True  # فعال‌سازی بین‌المللی‌سازی

USE_L10N = True  # فعال‌سازی فرمت‌بندی محلی

USE_TZ = True  # استفاده از timezone

# زبان‌های پشتیبانی شده
LANGUAGES = [
    ('fa', _('Persian')),
    ('en', _('English')),
]

# مسیر فایل‌های ترجمه
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# ============================================================================
# بخش ۸: فایل‌های استاتیک و مدیا
# ============================================================================

# URL برای فایل‌های استاتیک
STATIC_URL = 'static/'

# مسیر جمع‌آوری فایل‌های استاتیک
STATIC_ROOT = BASE_DIR / 'staticfiles'

# پوشه‌های اضافی فایل‌های استاتیک
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# URL برای فایل‌های مدیا
MEDIA_URL = 'media/'

# مسیر ذخیره فایل‌های مدیا
MEDIA_ROOT = BASE_DIR / 'media'

# انواع فایل‌های استاتیک
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# ============================================================================
# بخش ۹: فیلد پیش‌فرض کلید اصلی
# ============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# بخش ۱۰: تنظیمات REST Framework
# ============================================================================

REST_FRAMEWORK = {
    # کلاس‌های احراز هویت پیش‌فرض
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # برای پنل ادمین
    ),
    
    # دسترسی پیش‌فرض (نیاز به احراز هویت)
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # صفحه‌بندی پیش‌فرض
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    
    # رندررهای پیش‌فرض
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # فقط در حالت دیباگ
    ],
    
    # پارسرهای پیش‌فرض
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    
    # تنظیمات اعتبارسنجی
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    
    # تنظیمات مستندسازی
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    
    # محدودیت نرخ درخواست
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',  # 100 درخواست در روز برای کاربران ناشناس
        'user': '1000/day',  # 1000 درخواست در روز برای کاربران احراز هویت شده
    }
}

# ============================================================================
# بخش ۱۱: مدل کاربر سفارشی
# ============================================================================

# مشخص کردن مدل کاربر سفارشی
AUTH_USER_MODEL = 'accounts.User'

# ============================================================================
# بخش ۱۲: تنظیمات JWT (JSON Web Token)
# ============================================================================

SIMPLE_JWT = {
    # زمان انقضای توکن دسترسی
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    
    # زمان انقضای توکن بازیابی
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    
    # چرخش توکن‌های بازیابی
    'ROTATE_REFRESH_TOKENS': True,
    
    # بلاک کردن توکن‌های بازیابی پس از چرخش
    'BLACKLIST_AFTER_ROTATION': True,
    
    # الگوریتم امضا
    'ALGORITHM': 'HS256',
    
    # کلید امضا (در محیط تولید باید از SECRET_KEY متفاوت باشد)
    'SIGNING_KEY': SECRET_KEY,
    
    # کلیدهای تأیید
    'VERIFYING_KEY': None,
    
    # نوع هدر احراز هویت
    'AUTH_HEADER_TYPES': ('Bearer',),
    
    # نام هدر احراز هویت
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    
    # شناسه کاربر در توکن
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    # کلیدهای سفارشی در توکن
    'TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSerializer',
    
    # تنظیمات ادعاهای سفارشی (اختیاری)
    # 'TOKEN_OBTAIN_SERIALIZER': 'accounts.serializers.CustomTokenObtainPairSerializer',
}

# ============================================================================
# بخش ۱۳: تنظیمات امنیتی پروژه
# ============================================================================

SECURITY_SETTINGS = {
    # محدودیت تلاش ورود
    'MAX_LOGIN_ATTEMPTS': 5,  # حداکثر ۵ تلاش ناموفق
    
    # زمان قفل شدن حساب پس از تلاش‌های ناموفق (ثانیه)
    'LOGIN_ATTEMPT_TIMEOUT': 900,  # 15 دقیقه
    
    # مدت اعتبار کد OTP (دقیقه)
    'OTP_VALIDITY_MINUTES': 10,
    
    # مدت اعتبار session (روز)
    'SESSION_TIMEOUT_DAYS': 7,
    
    # مدت اعتبار درخواست بازیابی رمز (ثانیه)
    'PASSWORD_RESET_TIMEOUT': 3600,  # 1 ساعت
    
    # حداقل طول رمز عبور
    'PASSWORD_MIN_LENGTH': 8,
    
    # تاریخ انقضای رمز عبور (روز)
    'PASSWORD_EXPIRY_DAYS': 90,  # 90 روز
    
    # فعال‌سازی تأیید دو مرحله‌ای
    'TWO_FACTOR_AUTH_ENABLED': False,
    
    # محدودیت نرخ API
    'API_RATE_LIMIT_PER_MINUTE': 60,
    
    # لاگ‌گیری سطح بالا
    'SECURITY_LOGGING_LEVEL': 'INFO',
}

# ============================================================================
# بخش ۱۴: تنظیمات CORS (Cross-Origin Resource Sharing)
# ============================================================================

# فعال‌سازی CORS
CORS_ALLOW_ALL_ORIGINS = DEBUG  # فقط در حالت دیباگ اجازه همه

# لیست دامنه‌های مجاز
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    # دامنه‌های تولید:
    # "https://example.com",
    # "https://www.example.com",
]

# یا از regex patterns استفاده کنید
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://\w+\.example\.com$",  # همه زیردامنه‌های example.com
]

# متدهای HTTP مجاز
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# هدرهای مجاز
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# اجازه ارسال کوکی‌ها
CORS_ALLOW_CREDENTIALS = True

# ============================================================================
# بخش ۱۵: تنظیمات امنیتی پیشرفته Django
# ============================================================================

# SSL/HTTPS تنظیمات (در محیط تولید فعال شوند)
if not DEBUG:
    # اجبار به استفاده از HTTPS
    SECURE_SSL_REDIRECT = True
    
    # کوکی‌های امن فقط از طریق HTTPS ارسال شوند
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    
    # جلوگیری از sniffing نوع محتوا
    SECURE_CONTENT_TYPE_NOSNIFF = True
    
    # فعال‌سازی XSS Filter مرورگر
    SECURE_BROWSER_XSS_FILTER = True
    
    # جلوگیری از clickjacking
    X_FRAME_OPTIONS = 'DENY'
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Referrer Policy
    SECURE_REFERRER_POLICY = 'same-origin'
    
    # پروکسی‌های قابل اعتماد (اگر پشت load balancer هستید)
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

else:
    # تنظیمات محیط توسعه
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False

# ============================================================================
# بخش ۱۶: تنظیمات لاگ‌گیری
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'security': {
            'format': '{asctime} - {levelname} - USER:{user} - IP:{ip} - ACTION:{action} - {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/django.log',
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/security.log',
            'formatter': 'security',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
    },
}

# ============================================================================
# بخش ۱۷: تنظیمات ایمیل
# ============================================================================

# تنظیمات ایمیل (برای بازیابی رمز و اطلاع‌رسانی)
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'webmaster@localhost')

# ============================================================================
# بخش ۱۸: تنظیمات کش (Cache)
# ============================================================================

# تنظیمات کش (برای Rate Limiting و OTP)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 3600,  # 1 ساعت
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    },
    # برای محیط تولید از Redis استفاده کنید
    # 'default': {
    #     'BACKEND': 'django_redis.cache.RedisCache',
    #     'LOCATION': 'redis://127.0.0.1:6379/1',
    #     'OPTIONS': {
    #         'CLIENT_CLASS': 'django_redis.client.DefaultClient',
    #     }
    # }
}

# ============================================================================
# بخش ۱۹: تنظیمات مستندسازی API (Swagger)
# ============================================================================

# تنظیمات drf-yasg برای مستندسازی خودکار API
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'DOC_EXPANSION': 'none',
    'APIS_SORTER': 'alpha',
    'SHOW_REQUEST_HEADERS': True,
}

# ============================================================================
# بخش ۲۰: تنظیمات سرویس پیامک
# ============================================================================

# تنظیمات سرویس پیامک (کاوه نگار، فارابیت، ...)
SMS_CONFIG = {
    'ENABLED': DEBUG,  # در محیط توسعه فعال
    'PROVIDER': 'console',  # console, kavenegar, faraboot, ...
    'API_KEY': os.environ.get('SMS_API_KEY', ''),
    'SENDER_NUMBER': os.environ.get('SMS_SENDER_NUMBER', ''),
    'API_URL': os.environ.get('SMS_API_URL', ''),
    'VERIFICATION_TEMPLATE': 'کد تأیید شما: {code}',
    'PASSWORD_RESET_TEMPLATE': 'کد بازیابی رمز: {code} - اعتبار: 10 دقیقه',
}

# ============================================================================
# بخش ۲۱: تنظیمات مدیریت نشست
# ============================================================================

# تنظیمات session
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # یا 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_AGE = 86400  # 24 ساعت به ثانیه
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True

# ============================================================================
# بخش ۲۲: تنظیمات فایل .env (اختیاری)
# ============================================================================

# برای استفاده از python-dotenv (اگر نصب شده باشد)
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
    print("✅ فایل .env بارگذاری شد")
except ImportError:
    print("⚠️ python-dotenv نصب نشده است. از متغیرهای محیطی سیستم استفاده می‌شود.")
except Exception as e:
    print(f"⚠️ خطا در بارگذاری .env: {e}")

# ============================================================================
# بخش ۲۳: بررسی تنظیمات امنیتی
# ============================================================================

if DEBUG:
    print("=" * 60)
    print("⚠️  هشدار امنیتی: پروژه در حالت DEBUG است!")
    print("برای محیط تولید موارد زیر را تنظیم کنید:")
    print("1. DEBUG = False")
    print("2. SECRET_KEY از متغیر محیطی خوانده شود")
    print("3. ALLOWED_HOSTS تنظیم شود")
    print("4. تنظیمات SSL/HTTPS فعال شود")
    print("5. از دیتابیس production استفاده شود")
    print("=" * 60)