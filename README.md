# 📘 **آپدیت فایل README با تغییرات جدید**

## 🚀 **پروژه: سیستم احراز هویت و مدیریت کاربران پیشرفته**

### **✨ ویژگی‌های جدید اضافه شده:**

✅ **سیستم بازیابی رمز عبور با OTP**  
✅ **تأیید دو مرحله‌ای موبایل**  
✅ **محدودیت تلاش ورود (Anti-Brute Force)**  
✅ **لاگ‌گیری امنیتی کامل**  
✅ **مدیریت پیشرفته نقش‌ها**  
✅ **مدیریت نشست‌های کاربر**  
✅ **داشبورد ادمین با آمار زنده**  
✅ **تأیید ایمیل و پیامک**  
✅ **سیستم لاگین هوشمند با کش**

---

## 📁 **ساختار پروژه به‌روزرسانی شده:**

```
myproject/
├── 📁 accounts/                    # اپلیکیشن اصلی احراز هویت
│   ├── models.py                  # مدل‌های: User, UserSession, PasswordResetOTP, LoginAttempt, SecurityLog
│   ├── views.py                   # ViewSet‌های کامل (12 ViewSet)
│   ├── serializers.py             # 10 Serializer مختلف
│   ├── permissions.py             # سیستم مجوز مبتنی بر نقش
│   ├── utils.py                   # توابع کمکی: OTP, SMS, امنیت
│   ├── decorators.py              # دکوراتورهای لاگ‌گیری و امنیت
│   ├── urls.py                    # 15+ endpoint API
│   └── apps.py
│
├── 📁 logs/                       # پوشه لاگ‌های امنیتی
├── 📁 static/                     # فایل‌های استاتیک
├── 📁 media/                      # فایل‌های آپلود شده
│
├── 📄 requirements.txt            # لیست کامل پکیج‌ها
├── 📄 .env.example                # نمونه فایل متغیرهای محیطی
├── 📄 docker-compose.yml          # کانفیگ Docker (اختیاری)
└── 📄 README.md                   # همین فایل
```

---

## 🎯 **لیست کامل Endpointهای API:**

### **🔐 احراز هویت:**
```
POST   /api/accounts/register/          # ثبت‌نام
POST   /api/accounts/login/             # ورود (با محدودیت تلاش)
POST   /api/accounts/logout/            # خروج
```

### **🔒 امنیت و بازیابی:**
```
POST   /api/accounts/forgot-password/   # درخواست OTP بازیابی
POST   /api/accounts/verify-otp/        # تأیید OTP و تغییر رمز
POST   /api/accounts/verify-phone/      # تأیید شماره موبایل
POST   /api/accounts/verify-phone/resend/ # ارسال مجدد کد
```

### **👤 مدیریت پروفایل:**
```
GET    /api/accounts/profile/           # مشاهده پروفایل
PATCH  /api/accounts/profile/           # ویرایش پروفایل
```

### **💻 مدیریت نشست:**
```
GET    /api/accounts/session-management/           # لیست نشست‌ها
POST   /api/accounts/session-management/revoke_session/    # ابطال یک نشست
POST   /api/accounts/session-management/revoke_all_sessions/ # ابطال همه نشست‌ها
```

### **👑 مدیریت نقش‌ها (فقط ادمین):**
```
GET    /api/accounts/role-management/              # لیست کاربران و آمار
POST   /api/accounts/role-management/change_role/  # تغییر نقش کاربر
```

### **📊 داشبورد ادمین:**
```
GET    /api/accounts/admin-dashboard/dashboard_stats/  # آمار سیستم
```

### **🏫 پنل‌های اختصاصی:**
```
GET    /api/accounts/admin-panel/       # پنل ادمین (CRUD کاربران)
GET    /api/accounts/teacher-panel/     # پنل معلم
```

---

## 🔧 **پکیج‌های مورد نیاز:**

### **پکیج‌های اصلی:**
```txt
Django==5.2.8
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
django-cors-headers==4.3.1
psycopg2-binary==2.9.9      # برای PostgreSQL
redis==5.0.1                # برای کش و Rate Limiting
celery==5.3.4               # برای پردازش ناهمزمان
```

### **پکیج‌های امنیتی و توسعه:**
```txt
python-dotenv==1.0.0        # مدیریت متغیرهای محیطی
drf-yasg==1.21.7            # مستندسازی خودکار API
django-debug-toolbar==4.3.0 # ابزار دیباگ
gunicorn==21.2.0            # سرور تولید
whitenoise==6.6.0           # سرویس فایل‌های استاتیک
sentry-sdk==1.44.0          # مانیتورینگ خطاها
```

---

## ⚙️ **مراحل راه‌اندازی:**

### **1. نصب و تنظیم اولیه:**
```bash
# کلون کردن پروژه
git clone <repository-url>
cd school-auth-system

# ایجاد محیط مجازی
python -m venv venv

# فعال‌سازی (ویندوز)
venv\Scripts\activate

# فعال‌سازی (لینوکس/مک)
source venv/bin/activate

# نصب پکیج‌ها
pip install -r requirements.txt
```

### **2. تنظیمات محیط:**
```bash
# کپی فایل نمونه
cp .env.example .env

# ویرایش فایل .env با اطلاعات خود
nano .env
```

**محتوای فایل `.env`:**
```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# SMS Service (اختیاری)
SMS_API_KEY=your-sms-api-key
SMS_SENDER_NUMBER=10004346
```

### **3. اعمال مایگریشن‌ها:**
```bash
# ساخت پوشه‌های مورد نیاز
mkdir -p logs static media

# اعمال مایگریشن
python manage.py makemigrations
python manage.py migrate

# ایجاد کاربر ادمین
python manage.py createsuperuser
```

### **4. اجرای سرور:**
```bash
# حالت توسعه
python manage.py runserver

# یا با Docker
docker-compose up --build
```

---

## 🧪 **تست API:**

### **1. تست با curl:**
```bash
# ثبت‌نام
curl -X POST http://127.0.0.1:8000/api/accounts/register/ \
     -H "Content-Type: application/json" \
     -d '{
          "phone_number": "09123456789",
          "national_code": "1234567890",
          "password": "Test@1234",
          "first_name": "علی",
          "last_name": "رضایی"
        }'

# ورود
curl -X POST http://127.0.0.1:8000/api/accounts/login/ \
     -H "Content-Type: application/json" \
     -d '{
          "phone_number": "09123456789",
          "password": "Test@1234"
        }'
```

### **2. تست با Postman:**
- Import Collection از فایل `postman_collection.json`
- تنظیم Environment Variables:
  ```
  base_url: http://127.0.0.1:8000
  access_token: {{login_response.access}}
  ```

### **3. اسکریپت تست خودکار:**
```bash
# اجرای تست کامل
python manage.py test accounts

# یا تست دستی
python test_all_apis.py
```

---

## 🔐 **ویژگی‌های امنیتی:**

| ویژگی | توضیح | فعال‌سازی |
|-------|--------|-----------|
| **Rate Limiting** | محدودیت 5 تلاش ورود در 15 دقیقه | خودکار |
| **OTP با انقضا** | کدهای 6 رقمی با انقضای 10 دقیقه | نیاز به SMS Provider |
| **Session Management** | مدیریت چند دستگاه | خودکار |
| **Security Logging** | ثبت تمام فعالیت‌ها | خودکار |
| **Password Validation** | اعتبارسنجی پیچیدگی رمز | خودکار |
| **CORS Protection** | کنترل دامنه‌های مجاز | در settings.py |
| **JWT Blacklist** | باطل کردن توکن‌های استفاده شده | خودکار |

---

## 📊 **مدل‌های دیتابیس:**

### **1. User:**
- `phone_number` (unique, 11 digits)
- `national_code` (unique, 10 digits)
- `role` (admin/teacher/student)
- `phone_verified` (boolean)
- `is_active`, `is_staff`

### **2. UserSession:**
- `user` (ForeignKey)
- `refresh_token` (Text)
- `expires_at` (DateTime)
- `ip`, `device`
- `created_at` (auto)

### **3. PasswordResetOTP:**
- `user` (ForeignKey)
- `otp_code` (6 digits)
- `expires_at`, `is_used`

### **4. LoginAttempt:**
- `phone_number`, `ip_address`
- `successful` (boolean)
- `attempt_time` (auto)

### **5. SecurityLog:**
- `user` (ForeignKey, nullable)
- `action` (choices)
- `ip_address`, `user_agent`
- `details` (JSON)
- `created_at` (auto)

---

## 🎨 **پنل‌های مدیریتی:**

### **🔧 پنل ادمین (Django Admin):**
```
http://127.0.0.1:8000/admin/
```
- مدیریت کامل کاربران
- مشاهده لاگ‌ها
- مدیریت OTPها

### **📈 داشبورد ادمین (API):**
```
GET /api/accounts/admin-dashboard/dashboard_stats/?range=daily
```
- آمار کاربران
- گزارش ورودها
- توزیع نقش‌ها
- فعالیت‌های اخیر

---

## 🐳 **استقرار با Docker:**

### **1. ساخت و اجرا:**
```bash
docker-compose up --build
```

### **2. سرویس‌های در حال اجرا:**
- **Web**: Django روی پورت 8000
- **Database**: PostgreSQL
- **Cache**: Redis
- **Worker**: Celery برای پردازش ناهمزمان

### **3. محیط‌های مختلف:**
```bash
# توسعه
docker-compose -f docker-compose.dev.yml up

# تولید
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📈 **مستندات API:**

### **1. Swagger UI:**
```
http://127.0.0.1:8000/swagger/
```

### **2. ReDoc:**
```
http://127.0.0.1:8000/redoc/
```

### **3. Schema خام:**
```
http://127.0.0.1:8000/swagger.json
```

---

## 🚨 **عیب‌یابی:**

### **مشکل ۱: خطای Database**
```bash
# پاک کردن و شروع مجدد
rm db.sqlite3
python manage.py migrate
```

### **مشکل ۲: خطای Port در حال استفاده**
```bash
# تغییر پورت
python manage.py runserver 8001

# یا کشتن پروسه
sudo lsof -t -i tcp:8000 | xargs kill -9
```

### **مشکل ۳: خطای Import**
```bash
# بررسی نصب پکیج‌ها
pip list | grep django

# نصب مجدد
pip install --force-reinstall -r requirements.txt
```

---

## 🤝 **مشارکت:**

### **گایدلاین‌ها:**
1. از محیط مجازی استفاده کنید
2. قبل از commit، تست‌ها را اجرا کنید
3. مستندات را به‌روز نگه دارید
4. از PEP8 پیروی کنید

### **برچسب‌گذاری commit:**
```
✨ feat:    افزودن ویژگی جدید
🐛 fix:     رفع باگ
📚 docs:    تغییرات مستندات
🎨 style:   تغییرات ظاهری (فرمت، نیم‌فاصله و...)
♻️  refactor: بازنویسی کد
✅ test:    افزودن تست
```

---

## 📞 **پشتیبانی:**

### **راه‌های ارتباطی:**
- **Issues**: گزارش باگ در GitHub
- **Discussions**: پیشنهاد ویژگی‌های جدید
- **Email**: پشتیبانی فنی

### **منابع آموزشی:**
- [Django Documentation](https://docs.djangoproject.com/)
- [DRF Documentation](https://www.django-rest-framework.org/)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc7519)

---

## 🏆 **نکات نهایی:**

1. **همیشه از HTTPS در تولید استفاده کنید**
2. **SECRET_KEY را در محیط تولید مخفی نگه دارید**
3. **لاگ‌های امنیتی را به طور منظم بررسی کنید**
4. **از Rate Limiting برای endpointهای حساس استفاده کنید**
5. **به‌روزرسانی‌های امنیتی Django را پیگیری کنید**

---

**🌟 پروژه شما اکنون یک سیستم احراز هویت حرفه‌ای است که آماده استقرار در محیط تولید می‌باشد!**