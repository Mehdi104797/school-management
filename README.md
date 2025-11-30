البته! در ادامه یک **جزوه کامل و آموزشی** از پروژه‌ات تهیه کردم که:

- ساختار پروژه را شرح می‌دهد  
- هر پوشه و فایل را توضیح می‌دهد  
- پیش‌نیازها و پکیج‌های مورد نیاز را لیست می‌کند  
- هدف و کارکرد کلی سیستم را برجسته می‌کند  

---

## 📘 معرفی پروژه: سیستم مدیریت کاربران مبتنی بر نقش (Role-Based School Management API)

این پروژه یک **API پایه** برای سیستم‌های مدیریتی (مثل سیستم مدرسه، آموزشگاه یا سازمان) است که با **Django + Django REST Framework** پیاده‌سازی شده و دارای ویژگی‌های زیر است:

- **مدل کاربر سفارشی** (بدون `username`، ورود با **شماره موبایل**)
- **ثبت‌نام و احراز هویت با JWT** (توکن‌های access/refresh)
- **Session سفارشی** ذخیره‌شده در دیتابیس برای ردیابی دستگاه‌ها
- **سیستم دسترسی مبتنی بر نقش** (Admin / Teacher / Student)
- **اعتبارسنجی پیشرفته** (کد ملی، شماره موبایل، یکتا بودن آن‌ها)
- **ساختار تمیز و قابل گسترش** با استفاده از `ViewSet` و `Router`

این API برای استفاده در **فرانت‌اند Vue.js (نسخه 2)** طراحی شده، اما با هر کلاینتی (React، Angular، موبایل، ...) کار می‌کند.

---

## 📁 ساختار پروژه

```
myproject/                     ← پوشه اصلی پروژه Django
├── manage.py
├── myproject/                 ← تنظیمات مرکزی پروژه
│   ├── __init__.py
│   ├── settings.py            ← تنظیمات اصلی (دیتابیس، JWT، اپلیکیشن‌ها و ...)
│   ├── urls.py                ← روت اصلی URLها (اتصال به accounts/urls.py)
│   ├── wsgi.py
│   └── asgi.py
│
└── accounts/                  ← اپلیکیشن اصلی کاربران و احراز هویت
    ├── __init__.py
    ├── models.py              ← مدل‌های User و UserSession
    ├── views.py               ← ViewSetها (ثبت‌نام، ورود، پروفایل، نقش‌ها و ...)
    ├── serializers.py         ← Serializerها (اعتبارسنجی و تبدیل داده)
    ├── permissions.py         ← مجوزهای دسترسی سفارشی (IsAdmin, IsTeacher و ...)
    └── urls.py                ← مسیرهای API مربوط به حساب کاربری
```

---

## 📦 پکیج‌های مورد نیاز (نصب با pip)

```bash
pip install django
pip install djangorestframework
pip install djangorestframework-simplejwt
```

> ✅ **نکته:** همه این پکیج‌ها با `pip install` نصب می‌شوند. توصیه می‌شود قبل از نصب، یک **محیط مجازی (virtual environment)** ایجاد کنید:

```bash
python -m venv venv
# ویندوز:
venv\Scripts\activate
# لینوکس/مک:
source venv/bin/activate
```

---

## 🔍 جزئیات هر پوشه و فایل

### ✅ `myproject/settings.py`
- `AUTH_USER_MODEL = 'accounts.User'`: استفاده از مدل کاربر سفارشی
- `REST_FRAMEWORK`: فعال‌سازی **احراز هویت با JWT**
- `SIMPLE_JWT`: تنظیم طول عمر توکن‌ها (10 دقیقه access، 7 روز refresh)
- `INSTALLED_APPS`: فعال‌سازی `rest_framework` و `accounts`

### ✅ `accounts/models.py`
- `User`: مدل کاربر با فیلدهای:
  - `phone_number` (ورود با موبایل)
  - `national_code`
  - `role` (admin / teacher / student)
  - و سایر اطلاعات فردی
- `UserSession`: ذخیره توکن refresh + IP + دستگاه برای مدیریت session

### ✅ `accounts/serializers.py`
- `RegisterSerializer`: اعتبارسنجی و ثبت‌نام (شماره موبایل 11 رقم، شروع با 09، یکتا بودن)
- `LoginSerializer`: احراز هویت با شماره موبایل و رمز
- `ProfileSerializer`: فقط خواندن/ویرایش اطلاعات پروفایل (بدون دسترسی به password یا role)

### ✅ `accounts/permissions.py`
- `IsAdmin`, `IsTeacher`, `IsStudent`: کنترل دسترسی بر اساس نقش
- `TeacherOrAdminPermission`: مجوز مشترک برای دو نقش

### ✅ `accounts/views.py`
- `RegisterViewSet`: ثبت‌نام
- `LoginViewSet`: ورود + ایجاد session جدید
- `LogoutViewSet`: حذف session از دیتابیس
- `ProfileViewSet`: مشاهده و ویرایش پروفایل
- `AdminViewSet`, `TeacherViewSet`: APIهای خاص هر نقش

### ✅ `accounts/urls.py`
- از `DefaultRouter` استفاده می‌کند
- مسیرهای خودکار:
  - `/api/accounts/register/`
  - `/api/accounts/login/`
  - `/api/accounts/logout/`
  - `/api/accounts/profile/`
  - `/api/accounts/admin-panel/` (فقط admin)
  - `/api/accounts/teacher-panel/` (فقط teacher)

### ✅ `myproject/urls.py`
- تنها یک مسیر اصلی:
  ```python
  path('api/accounts/', include('accounts.urls')),
  ```
- (در این پروژه **نیازی به `/api/token/` نیست** چون لاگین سفارشی همه چیز را مدیریت می‌کند)

---

## 🔐 امنیت و ویژگی‌های کلیدی

| ویژگی | توضیح |
|-------|--------|
| 🔑 **ورود با شماره موبایل** | بدون نیاز به `username` |
| 🛡️ **اعتبارسنجی ورودی** | شماره موبایل = 11 رقم، شروع با `09`، یکتا |
| ⏳ **توکن منقضی‌شونده** | access = 10 دقیقه، refresh = 7 روز |
| 💾 **Session سفارشی** | ذخیره در دیتابیس برای مدیریت فعالیت کاربران |
| 👮 **Role-Based Access** | دسترسی متفاوت برای admin, teacher, student |
| 🧼 **Serializerهای جداگانه** | Register ≠ Profile → جلوگیری از دسترسی غیرمجاز |

---

## 🚀 نحوه اجرای پروژه

1. محیط مجازی ایجاد و فعال کن:
   ```bash
   python -m venv venv && venv\Scripts\activate  # ویندوز
   ```
2. پکیج‌ها را نصب کن:
   ```bash
   pip install django djangorestframework djangorestframework-simplejwt
   ```
3. مایگریشن‌ها را اعمال کن:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. سرور را اجرا کن:
   ```bash
   python manage.py runserver
   ```
5. APIها را تست کن (مثلاً با Postman یا curl):
   - ثبت‌نام: `POST /api/accounts/register/`
   - ورود: `POST /api/accounts/login/`
   - پروفایل: `GET /api/accounts/profile/` (با هدر `Authorization: Bearer <access_token>`)

---

## 📌 نکته پایانی

این پروژه **کاملاً آماده برای اتصال به Vue.js** است. در فرانت‌اند کافی است:

- توکن `access` را در `LocalStorage` ذخیره کنی  
- در هر درخواست، هدر `Authorization: Bearer <token>` را ارسال کنی  
- از `refresh token` برای دریافت توکن جدید استفاده کنی

---

اگر خواستی، می‌تونم یک **README.md** کامل برای گیت‌هاب هم برات بنویسم!  
یا اگر می‌خوای بریم سراغ **اتصال این API به Vue 2**، فقط بگو:  
**بریم جلسه ۸ — فرانت‌اند با Vue.js** 🎯
