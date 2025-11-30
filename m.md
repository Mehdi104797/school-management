بیا کمک کن من بتونم موارد پله پله حتی با توضیح پیش نیاز ها انگار که داری جزوه میدی برای آموزش بیا این موارد به عنوان پروژه انجام بدیم 
چک‌لیست گام‌به‌گام
1️⃣ آماده‌سازی محیط

نصب Django و Django REST Framework (pip install django djangorestframework)

نصب پکیج JWT برای DRF (pip install djangorestframework-simplejwt)

ساخت پروژه و اپ جدید در Django (django-admin startproject myproject, python manage.py startapp accounts)

2️⃣ طراحی مدل کاربر سفارشی

از AbstractBaseUser یا AbstractUser ارث‌بری کن

فیلدهای مورد نظر:

کد ملی (national_code)

کد خدمات (service_code)

شماره موبایل (phone_number)

نام و نام خانوادگی (first_name, last_name)

نام پدر (father_name)

شهر (city)

نقش‌ها (roles) → می‌تونه یه ChoiceField باشه یا ManyToMany به مدل Role

تعریف UserManager برای ساخت کاربر و ادمین

3️⃣ پیاده‌سازی سیستم احراز هویت

JWT Authentication با rest_framework_simplejwt

Session سفارشی:

استفاده از DB یا Redis برای ذخیره Session به جای Session پیش‌فرض Django

هر بار ورود، توکن جدید صادر بشه و Session هم آپدیت بشه

4️⃣ سطوح دسترسی (Permissions)

تعریف Permissionهای سفارشی برای نقش‌ها (IsAdmin, IsTeacher, ...)

استفاده از کلاس‌های BasePermission در DRF

5️⃣ ساخت API ها

Register API → ثبت نام با تمام فیلدها

Login API → دریافت JWT + Session

User Profile API → نمایش اطلاعات کاربر

Role-based APIs → دسترسی محدود به نقش‌ها

6️⃣ Serializer ها

ساخت Serializer برای User و Role

مدیریت validation مثل یکتا بودن شماره موبایل و کد ملی

7️⃣ Routing و URLs

مسیرهای RESTful با router = DefaultRouter()

مسیر JWT: /api/token/, /api/token/refresh/

8️⃣ Vue2 Frontend

Axios برای درخواست API

ذخیره توکن JWT در LocalStorage یا Vuex

ارسال Authorization Header در هر درخواست

9️⃣ امنیت و بهینه‌سازی

Hash کردن پسورد با make_password و DRF

اعتبارسنجی توکن JWT و Session

محدود کردن درخواست‌ها به HTTPS

Refresh Token برای طول عمر








حتماً!
از این پیام به بعد **گام‌به‌گام، کاملاً آموزشی و شبیه یک جزوه درسی** پیش می‌رویم و هر بخش را همراه با **پیش‌نیازها، توضیح مفاهیم، کد، خط‌به‌خط و نکات مهم** جلو می‌بریم.

---

# 🎯 جلسه ۱ — آماده‌سازی محیط (مرحله 1️⃣ از چک‌لیست)

در این جلسه هدف ما این است که:

* محیط را آماده کنیم
* Django و DRF و JWT را نصب کنیم
* یک پروژه بسازیم
* یک اپ به نام accounts ایجاد کنیم
* ساختار اولیه را بشناسیم

---

# 🔰 بخش اول: پیش‌نیازهای مفهومی

## 📌 پیش‌نیازهای لازم

قبل از شروع باید این‌ها را نصب داشته باشید:

* **Python 3.9+**
* **pip**
* آشنایی اولیه با مفهوم:

  * پروژه (Project)
  * اپلیکیشن (App)
  * محیط مجازی (Virtual environment)
  * REST API و سرورها

---

# 🔹 گام 1: ساخت محیط مجازی

محیط مجازی باعث می‌شود پکیج‌های پروژه جدا از سایر پروژه‌ها نصب شوند.

```bash
python -m venv venv
source venv/bin/activate   # در ویندوز: venv\Scripts\activate
```

---

# 🔹 گام 2: نصب Django و DRF

```bash
pip install django djangorestframework
```

## 💡 DRF چیست؟

Django REST Framework یک ابزار آماده است برای ساخت API
این یعنی:

* مدل را می‌دهیم → خروجی JSON می‌دهد
* درگیر HTML و Template نمی‌شویم
* Permission, Authentication, Serializer و … در اختیار ماست

---

# 🔹 گام 3: نصب SimpleJWT

این پکیج مسئول تولید JWT Token است:

```bash
pip install djangorestframework-simplejwt
```

---

# 🔹 گام 4: ساخت پروژه جنگو

```bash
django-admin startproject myproject
cd myproject
```

ساختار:

```
myproject/
    manage.py
    myproject/
        settings.py
        urls.py
        asgi.py
        wsgi.py
```

---

# 🔹 گام 5: ساخت اپ جدید به نام accounts

```bash
python manage.py startapp accounts
```

ساختار:

```
accounts/
    models.py
    views.py
    serializers.py (خودمان می‌سازیم)
    urls.py (خودمان می‌سازیم)
```

---

# 🔹 گام 6: فعال کردن اپ و DRF در settings.py

فایل `settings.py` را باز کن و در بخش `INSTALLED_APPS` این را اضافه کن:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'accounts',
]
```

و برای JWT:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}
```

---

# 🔹 گام 7: بررسی اینکه پروژه اجرا شود

```bash
python manage.py runserver
```

اگر آدرس زیر باز شد:

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

⇐ یعنی محیط آماده است

---

# ✨ نتیجه جلسه ۱

✔ محیط ایجاد شد
✔ Django + DRF + JWT نصب شد
✔ پروژه ساخته شد
✔ اپ accounts ساخته شد
✔ تنظیمات اولیه DRF انجام شد

---

# 🎒 آیا آماده‌ای برویم جلسه ۲؟

**در جلسه ۲ می‌رویم سراغ مهم‌ترین بخش: ساخت مدل کاربر سفارشی (Custom User Model).**

این بخش معمولاً برای مبتدی‌ها سخت است، ولی من آن را به ساده‌ترین شکل ممکن آموزش می‌دهم.

بگو:
**بله، بریم جلسه ۲**








عالیه!
می‌رویم سراغ **جلسه ۲ — طراحی مدل کاربر سفارشی (Custom User Model)**
این یکی از مهم‌ترین و پایه‌ای‌ترین بخش‌های پروژه است. اگر درست انجام نشود، کل پروژه مشکل پیدا می‌کند.

---

# 🎯 هدف جلسه ۲

1. انتخاب نوع مدل کاربر سفارشی
2. توضیح تفاوت `AbstractUser` و `AbstractBaseUser`
3. ساخت کاربر با فیلدهای مورد نیاز
4. ساخت UserManager
5. ثبت مدل در `settings.py`

---

# 🧠 پیش‌نیاز مفهومی — Custom User Model

## چرا به مدل کاربر سفارشی نیاز داریم؟

چون User پیش‌فرض Django فقط شامل:

* username
* email
* first_name
* last_name
* password

است، اما ما **کد ملی، شماره موبایل، نقش‌ها، نام پدر، شهر و...** می‌خواهیم.

---

# 🔥 انتخاب بین `AbstractUser` و `AbstractBaseUser`

### 🔹 AbstractUser (ساده‌تر)

* از مدل User Django ارث‌بری می‌کند
* username، password، first_name، last_name وجود دارد
* برای پروژه‌هایی مناسب است که فقط می‌خواهیم چند فیلد اضافه کنیم

### 🔹 AbstractBaseUser (پیشرفته‌تر، حرفه‌ای‌تر)

* ما همه چیز را از صفر تعریف می‌کنیم
* username را برمی‌داریم
* login بر اساس phone_number یا national_code می‌شود
* مناسب برای سیستم‌های سازمانی، مالی و پروژه‌های Enterprise

### 🔥 ما در این پروژه از **AbstractBaseUser** استفاده می‌کنیم

چون:

* احراز هویت با شماره موبایل یا کد ملی می‌خواهیم
* نقش‌ها و ساختار پیچیده داریم
* Session سفارشی خواهیم داشت

---

# 🧩 مدل User — شروع کدنویسی

برویم فایل:

```
accounts/models.py
```

و کل محتویات آن را پاک کن، سپس:

---

# 🔹 مرحله 1: ایمپورت‌ها

```python
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
```

🔥 `PermissionsMixin` برای پشتیبانی از گروه‌ها و permission ها استفاده می‌شود.

---

# 🔹 مرحله 2: ساخت UserManager

UserManager مسئول ساخت:

* user
* superuser (admin)
* رمزنگاری رمز

کد:

```python
class UserManager(BaseUserManager):
    def create_user(self, phone_number, national_code, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")
        if not national_code:
            raise ValueError("National code is required")

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

        return self.create_user(phone_number, national_code, password, **extra_fields)
```

---

# 🔹 مرحله 3: ساخت Model اصلی User

این ساختار پیشنهادی مطابق چک‌لیست توست:

```python
class User(AbstractBaseUser, PermissionsMixin):
    national_code = models.CharField(max_length=10, unique=True)
    service_code = models.CharField(max_length=10, blank=True, null=True)
    phone_number = models.CharField(max_length=11, unique=True)

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    father_name = models.CharField(max_length=50, blank=True, null=True)

    city = models.CharField(max_length=50, blank=True, null=True)

    # نقش‌ها - فعلاً ChoiceField
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    # موارد سیستمی
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'  # login با موبایل
    REQUIRED_FIELDS = ['national_code']

    def __str__(self):
        return f"{self.phone_number} - {self.first_name} {self.last_name}"
```

---

# 📝 نکات مهم

### ✔ USERNAME_FIELD یعنی چه؟

یعنی کاربر با **phone_number** وارد می‌شود
نه username.

---

# 🔹 مرحله 4: معرفی User سفارشی به Django

در فایل:

```
myproject/settings.py
```

این خط را اضافه کن:

```python
AUTH_USER_MODEL = 'accounts.User'
```

این یکی از **حیاتی‌ترین** مراحل است.

⚠ اگر این مرحله انجام نشود → migration ها خراب می‌شوند
⚠ اگر این کار را دیر انجام دهیم → پروژه را باید از صفر ساخت

---

# 🔹 مرحله 5: ساخت و اعمال Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

اگر بدون خطا اجرا شد = مدل ما درست ساخته شده ✔

---

# 🎉 نتیجه جلسه ۲

✔ Custom User Model ساخته شد
✔ UserManager سفارشی داریم
✔ نقش‌ها اضافه شده‌اند
✔ سیستم Login با شماره موبایل آماده شد
✔ Django را به User جدید وصل کردیم

---

# 🧩 جلسه ۳ — پیاده‌سازی سیستم احراز هویت (JWT + Session سفارشی)

در جلسه ۳ یاد می‌گیریم:

* فعال کردن JWT
* ساخت Login API
* ثبت‌نام کاربر
* تولید Refresh/Access Token
* طراحی Session سفارشی روی DB یا Redis
* هر ورود → ایجاد Session جدید

اگر آماده‌ای بگو:

### **بریم جلسه سه**







عالیه!
می‌رویم سراغ **جلسه ۳ — پیاده‌سازی سیستم احراز هویت (Authentication)**
در این جلسه JWT را فعال می‌کنیم، API لاگین و ثبت‌نام را می‌سازیم و زیرساخت Session سفارشی را آماده می‌کنیم.

---

# 🎯 هدف جلسه ۳

در پایان این جلسه:

✔ JWT فعال شده است
✔ API ثبت‌نام داریم
✔ API لاگین داریم
✔ با ورود کاربر → توکن جدید صادر می‌شود
✔ زیرساخت Session سفارشی را می‌سازیم

---

# 🧠 پیش‌نیاز مفهومی — JWT چیست؟

JWT = JSON Web Token یعنی:

* کاربر login می‌کند
* سرور یک توکن رمزگذاری‌شده می‌دهد
* کاربر توکن را در هر درخواست می‌فرستد
* سرور بدون نیاز به Session به او اعتماد می‌کند

توکن‌ها دو نوع‌اند:

1. **Access Token** — عمر کوتاه (مثلاً ۵ دقیقه)
2. **Refresh Token** — برای گرفتن Access جدید

---

# 🔥 بخش اول — فعال کردن JWT در Django

فایل:

```
myproject/settings.py
```

اضافه کن:

```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

این یعنی:

Authorization: Bearer <token>

---

# 🔥 بخش دوم — ساخت Serializer ثبت‌نام و لاگین

فایل جدید بساز:

```
accounts/serializers.py
```

و داخل آن:

---

## 🔹 1) RegisterSerializer

```python
from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'phone_number', 'national_code', 'password',
            'first_name', 'last_name', 'father_name',
            'service_code', 'city', 'role'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
```

---

## 🔹 2) LoginSerializer

```python
from django.contrib.auth import authenticate

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(
            phone_number=data['phone_number'],
            password=data['password']
        )

        if user is None:
            raise serializers.ValidationError("شماره موبایل یا رمز اشتباه است")

        data['user'] = user
        return data
```

---

# 🔥 بخش سوم — View ها

فایل:

```
accounts/views.py
```

---

## 🔹 1) RegisterView

```python
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from .models import User


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "ثبت‌نام با موفقیت انجام شد"}, status=status.HTTP_201_CREATED)
```

---

## 🔹 2) LoginView با JWT

```python
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from django.utils.timezone import now

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # ایجاد توکن جدید برای هر ورود
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": user.id,
            "phone_number": user.phone_number,
        })
```

تا اینجا JWT کامل و سالم کار می‌کند.

---

# 🔥 بخش چهارم — پیاده‌سازی Session سفارشی

تو گفتی:

> از DB یا Redis استفاده کنیم برای Session سفارشی
> هر بار ورود، یک Session جدید ایجاد شود

### ما از DB شروع می‌کنیم (ساده‌تر است).

---

## 🔹 مدل Session سفارشی

فایل: `accounts/models.py`

بعد از User علاوه کنید:

```python
class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    device = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"Session of {self.user.phone_number}"
```

---

## 🔹 ذخیره Session هنگام لاگین

ویرایش LoginView:

```python
from .models import UserSession

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        # ذخیره Session
        UserSession.objects.create(
            user=user,
            refresh_token=str(refresh),
            ip=request.META.get('REMOTE_ADDR'),
            device=request.META.get('HTTP_USER_AGENT')
        )

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })
```

حالا:

✔ هر بار login → یک رکورد Session ساخته می‌شود
✔ امکان مدیریت Session‌ها وجود دارد
✔ می‌توانیم logout سفارشی بسازیم و Session را حذف کنیم

---

# 🔥 بخش پنجم — URL ها

فایل جدید بساز:

```
accounts/urls.py
```

```python
from django.urls import path
from .views import RegisterView, LoginView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
]
```

و در فایل اصلی:

```
myproject/urls.py
```

```python
from django.urls import path, include

urlpatterns = [
    path('api/accounts/', include('accounts.urls')),
]
```

---

# 🎉 نتیجه جلسه ۳

✔ JWT فعال شد
✔ API ثبت نام ساخته شد
✔ API لاگین ساخته شد
✔ تولید توکن در هر ورود انجام می‌شود
✔ Session سفارشی پیاده‌سازی شد
✔ Session ها در DB ذخیره می‌شوند

---

# 🎯 جلسه ۴ — سطوح دسترسی (RBAC + Permissions)

در جلسه بعد می‌سازیم:

* Permission برای نقش‌ها
* IsAdmin, IsTeacher, IsStudent
* اعمال دسترسی روی APIها
* جلوگیری از دسترسی کاربران غیرمجاز

اگر آماده‌ای بگو:

### **بریم جلسه چهارم**


بسیار عالی!
می‌رسیم به یکی از مهم‌ترین بخش‌های پروژه:

# 🎯 جلسه ۴ — پیاده‌سازی سطوح دسترسی (Role-Based Permissions)

در این جلسه:

✔ نقش‌ها را مدیریت می‌کنیم
✔ Permission سفارشی برای هر نقش می‌سازیم
✔ APIها را براساس نقش محدود می‌کنیم
✔ دسترسی Admin / Teacher / Student را بررسی می‌کنیم

---

# 🧠 پیش‌نیاز مفهومی — Permission در DRF چیست؟

Permissions در DRF نشان می‌دهد **آیا کاربر حق انجام یک عملیات را دارد یا نه؟**

به شکل کلی:

* Authentication ⇒ کاربر کیست؟
* Permission ⇒ آیا اجازه انجام این کار را دارد؟

ما می‌خواهیم:

* Admin → دسترسی کامل
* Teacher → فقط بخش‌های آموزشی
* Student → فقط پروفایل خودش

---

# 🔥 بخش اول — ساخت Role Permissions

می‌رویم داخل فایل:

```
accounts/permissions.py
```

اگر نیست بساز.
سپس این Permission ها را تعریف می‌کنیم:

---

## 🔹 1) Permission فقط برای Admin

```python
from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')
```

---

## 🔹 2) Permission فقط برای Teacher

```python
class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'teacher')
```

---

## 🔹 3) Permission فقط برای Student

```python
class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'student')
```

---

## 🔹 4) Permission عمومی‌تر برای مجموعه نقش‌ها

گاهی بخشی برای چند نقش مجاز است.

مثلاً:

* Admin و Teacher مجازند
* Student مجاز نیست

پس یک Permission قابل تنظیم می‌سازیم:

```python
class HasRole(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in self.allowed_roles
        )
```

برای استفاده:

```python
class TeacherOrAdminPermission(HasRole):
    allowed_roles = ['admin', 'teacher']
```

---

# 🔥 بخش دوم — اعمال Permission روی APIها

فرض کنیم API پروفایل داریم:

در فایل:

```
accounts/views.py
```

اضافه کنیم:

---

### 🔹 API پروفایل کاربر (فقط کاربر خودش مجاز است)

```python
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "phone_number": user.phone_number,
            "national_code": user.national_code,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        })
```

این API صرفاً احراز هویت می‌خواهد، نه نقش.

---

### 🔹 API فقط برای Admin ها

```python
from .permissions import IsAdmin

class AdminOnlyView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({"message": "فقط ادمین‌ها می‌توانند این را ببینند."})
```

---

### 🔹 API فقط برای Teacher ها

```python
from .permissions import IsTeacher

class TeacherOnlyView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        return Response({"message": "فقط معلم‌ها مجاز هستند."})
```

---

### 🔹 API مشترک Admin + Teacher

```python
from .permissions import TeacherOrAdminPermission

class TeacherAdminView(APIView):
    permission_classes = [TeacherOrAdminPermission]

    def get(self, request):
        return Response({"message": "ادمین و معلم دسترسی دارند"})
```

---

# 🔥 بخش سوم — اضافه کردن مسیرها (URLs)

فایل:

```
accounts/urls.py
```

به شکل کامل:

```python
from django.urls import path
from .views import (
    ProfileView,
    AdminOnlyView,
    TeacherOnlyView,
    TeacherAdminView
)

urlpatterns = [
    path('profile/', ProfileView.as_view()),
    path('admin-only/', AdminOnlyView.as_view()),
    path('teacher-only/', TeacherOnlyView.as_view()),
    path('teacher-admin/', TeacherAdminView.as_view()),
]
```

---

# 🔥 بخش چهارم — تست نقش‌ها

کاربر Admin:

```json
{
  "phone_number": "09121234567",
  "national_code": "1234567890",
  "password": "1234",
  "role": "admin"
}
```

کاربر Teacher:

```json
{
  "phone_number": "09351234567",
  "national_code": "0987654321",
  "password": "1234",
  "role": "teacher"
}
```

تست APIها:

### 1. `/api/accounts/admin-only/`

* Admin: ✔
* Teacher: ❌
* Student: ❌

### 2. `/api/accounts/teacher-only/`

* Teacher: ✔
* Admin: ❌ (عمداً)
* Student: ❌

### 3. `/api/accounts/teacher-admin/`

* Teacher: ✔
* Admin: ✔
* Student: ❌

---

# 🎉 نتیجه جلسه ۴

✔ Permissionهای پایه ایجاد شد
✔ دسترسی نقش‌ها کنترل شد
✔ APIهای محدود به نقش ساخته شد
✔ زیرساخت RBAC تکمیل شد

---

# 🎯 جلسه ۵ — ساخت API های اصلی پروژه

در جلسه بعد:

* Register API
* Login API
* Profile API
* Logout و حذف Session
* API هایی که بر اساس نقش متفاوت‌اند
* استفاده از ViewSet و Router

اگر آماده‌ای بگو:

### **بریم جلسه پنجم**



عالیه!
می‌رویم سراغ یکی از کاربردی‌ترین جلسات پروژه:

# 🎯 جلسه ۵ — ساخت APIهای اصلی (Register, Login, Profile, Logout + Role-based API)

در این جلسه همه APIهای هسته پروژه را پیاده‌سازی می‌کنیم، شامل:

✔ Register
✔ Login
✔ Profile
✔ Logout + مدیریت Session
✔ Role-based API با ViewSet و Router DRF

این جلسه زیربنای اصلی Backend ما را تکمیل می‌کند.

---

# 🧩 بخش اول — ساخت API با ViewSet (به جای View معمولی)

تا الان از `APIView` استفاده کردیم
ولی برای APIهای جدی باید از `ViewSet` و `routers` استفاده کنیم.

مزایا:

* endpoint خودکار ساخته می‌شود
* کد تمیزتر و ماژولار
* استاندارد REST بهتر رعایت می‌شود

---

# 🔥 بخش دوم — Register API (ViewSet)

فایل:

```
accounts/views.py
```

اضافه کن:

```python
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import RegisterSerializer
from .models import User


class RegisterViewSet(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def create(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "ثبت‌نام با موفقیت انجام شد"}, status=status.HTTP_201_CREATED)
```

بعداً با Router وصلش می‌کنیم.

---

# 🔥 بخش سوم — Login API (ViewSet)

در همین فایل:

```python
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from .models import UserSession


class LoginViewSet(viewsets.GenericViewSet):
    serializer_class = LoginSerializer

    def create(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # تولید توکن
        refresh = RefreshToken.for_user(user)

        # ذخیره session در DB
        UserSession.objects.create(
            user=user,
            refresh_token=str(refresh),
            ip=request.META.get('REMOTE_ADDR'),
            device=request.META.get('HTTP_USER_AGENT')
        )

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": user.id
        })
```

---

# 🔥 بخش چهارم — Logout API (حذف Session)

برای خروج:

* Refresh Token را از DB حذف می‌کنیم
* (اختیاری) خود RefreshToken را blacklist می‌کنیم (SimpleJWT این قابلیت را دارد)

در اینجا روش ساده‌تر را پیاده‌سازی می‌کنیم.

در `views.py`:

```python
from rest_framework.permissions import IsAuthenticated


class LogoutViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        refresh_token = request.data.get("refresh")

        # حذف session از DB
        UserSession.objects.filter(
            user=request.user,
            refresh_token=refresh_token
        ).delete()

        return Response({"message": "خروج با موفقیت انجام شد"})
```

نکته:
در آینده می‌توانیم blacklist token را هم فعال کنیم.

---

# 🔥 بخش پنجم — Profile API (GET + UPDATE)

در `views.py`:

```python
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer  # فعلاً از همان استفاده می‌کنیم


class ProfileViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        serializer = RegisterSerializer(user)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        user = request.user
        serializer = RegisterSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "ویرایش پروفایل انجام شد"})
```

ویژگی‌ها:

* `GET /profile/` → نمایش اطلاعات
* `PATCH /profile/` → ویرایش بخشی

---

# 🔥 بخش ششم — API بر اساس نقش (Role-based)

### Admin API

```python
from .permissions import IsAdmin

class AdminViewSet(viewsets.ViewSet):
    permission_classes = [IsAdmin]

    def list(self, request):
        users = User.objects.all()
        data = RegisterSerializer(users, many=True).data
        return Response(data)
```

### Teacher API

```python
from .permissions import IsTeacher

class TeacherViewSet(viewsets.ViewSet):
    permission_classes = [IsTeacher]

    def list(self, request):
        return Response({"message": "دسترسی معلم"})
```

---

# 🔥 بخش هفتم — Routing با DefaultRouter

فایل:

```
accounts/urls.py
```

کد کامل:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterViewSet,
    LoginViewSet,
    LogoutViewSet,
    ProfileViewSet,
    AdminViewSet,
    TeacherViewSet,
)

router = DefaultRouter()
router.register('register', RegisterViewSet, basename='register')
router.register('login', LoginViewSet, basename='login')
router.register('logout', LogoutViewSet, basename='logout')
router.register('profile', ProfileViewSet, basename='profile')
router.register('admin-panel', AdminViewSet, basename='admin_panel')
router.register('teacher-panel', TeacherViewSet, basename='teacher_panel')

urlpatterns = [
    path('', include(router.urls)),
]
```

نتیجه:

```
/api/accounts/register/ POST
/api/accounts/login/ POST
/api/accounts/logout/ POST
/api/accounts/profile/ GET
/api/accounts/profile/ PATCH
/api/accounts/admin-panel/ GET   (فقط Admin)
/api/accounts/teacher-panel/ GET (فقط Teacher)
```

---

# 🎉 نتیجه جلسه ۵

✔ Register API کامل شد
✔ Login API همراه با تولید JWT و Session
✔ Logout API با حذف Session
✔ Profile API (GET + PATCH)
✔ Role-based APIها با ViewSet
✔ Routing واقعی با DefaultRouter

پشت‌ساخت اصلی Backend تمام شد!

---

# 🎯 جلسه ۶ — Serializer ها (Validation کامل + Serializer جدا برای User و Role)

در جلسه بعد یاد می‌گیریم:

* ساخت UserSerializer حرفه‌ای
* مدیریت validation شماره موبایل و کد ملی
* جلوگیری از تکراری بودن فیلدها
* جدا کردن RegisterSerializer از ProfileSerializer
* مدیریت RoleSerializer در آینده

اگر آماده‌ای بگو:

### **بریم جلسه ششم**



عالیه!
می‌رویم سراغ **جلسه ۶ — Serializer ها (Validation کامل، تمیزسازی، تفکیک Register/Profile)**

این یکی از مهم‌ترین جلسات است چون **مدیریت ورودی کاربر = امنیت پروژه**
و اگر Serializer درست پیاده‌سازی شود، نیمه بزرگی از Backend حرفه‌ای کامل شده است.

---

# 🎯 هدف جلسه ۶

در پایان این جلسه:

✔ Serializerهای پروژه کاملاً حرفه‌ای می‌شوند
✔ Register و Profile از هم جدا می‌شوند
✔ Validation شماره موبایل و کد ملی اضافه می‌شود
✔ Password hashing صحیح مدیریت می‌شود
✔ RoleSerializer (در صورت نیاز) پایه‌ریزی می‌شود

---

# 🧠 پیش‌نیاز مفهومی — Serializer چیست؟

Serializer داده‌ای که:

* از کاربر می‌گیرد را معتبرسازی می‌کند
* تبدیل به مدل Django می‌کند
* داده مدل را تبدیل به JSON خروجی می‌کند

تمثیل ساده:

> Serializer = فیلتر + مترجم + امنیت

---

# 🔥 بخش اول — تمیزسازی فایل serializers.py

برویم فایل:

```
accounts/serializers.py
```

ما این Serializerها را خواهیم ساخت:

1. **UserSerializer** — نمایش اطلاعات کاربر
2. **RegisterSerializer** — ثبت‌نام
3. **LoginSerializer** — لاگین
4. **ProfileSerializer** — مدیریت پروفایل
5. **RoleSerializer** (اختیاری)

---

# 🔥 بخش دوم — UserSerializer (خواندن اطلاعات کاربر)

این Serializer فقط برای نمایش کاربرد دارد.

```python
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'phone_number',
            'national_code',
            'service_code',
            'first_name',
            'last_name',
            'father_name',
            'city',
            'role',
        ]
        read_only_fields = ['id', 'role']
```

---

# 🔥 بخش سوم — Validation حرفه‌ای برای ثبت‌نام

چند نکته مهم:

* Validation شماره موبایل
* Validation یکتابودن شماره موبایل و کد ملی
* Password باید هش شود
* اگر نقش داده نشود → student شود

کد:

```python
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'phone_number',
            'national_code',
            'password',
            'first_name',
            'last_name',
            'father_name',
            'service_code',
            'city',
            'role',
        ]

    # Validation شماره موبایل
    def validate_phone_number(self, value):
        if len(value) != 11 or not value.startswith("09"):
            raise serializers.ValidationError("شماره موبایل معتبر نیست")
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("این شماره موبایل قبلاً ثبت شده")
        return value

    # Validation کد ملی
    def validate_national_code(self, value):
        if len(value) != 10:
            raise serializers.ValidationError("کد ملی باید 10 رقم باشد")
        if User.objects.filter(national_code=value).exists():
            raise serializers.ValidationError("این کد ملی قبلاً ثبت شده")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # hashing
        user.save()
        return user
```

نتیجه:

✔شماره موبایل باید 11 رقم باشد
✔باید با 09 شروع شود
✔یکتا باشد
✔کد ملی 10 رقمی و یکتا
✔Password hashing امن

---

# 🔥 بخش چهارم — LoginSerializer (بدون تغییر زیاد)

قبلاً ساختیم؛ فقط خواناتر می‌کنیم:

```python
from django.contrib.auth import authenticate

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            phone_number=data['phone_number'],
            password=data['password']
        )
        if not user:
            raise serializers.ValidationError("شماره موبایل یا رمز عبور اشتباه است")

        data['user'] = user
        return data
```

---

# 🔥 بخش پنجم — ProfileSerializer (برای GET و PATCH)

از RegisterSerializer جداست، چون:

* Register شامل password است
* Profile شامل password نیست
* Profile داده‌های read-only دارد

کد:

```python
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'phone_number',
            'national_code',
            'service_code',
            'first_name',
            'last_name',
            'father_name',
            'city',
            'role',
        ]
        read_only_fields = ['phone_number', 'national_code', 'role']
```

این یعنی:

* کاربر نمی‌تواند شماره موبایل را تغییر دهد
* نمی‌تواند کد ملی را تغییر دهد
* نمی‌تواند نقش خود را تغییر دهد

کاملاً منطقی و امن.

---

# 🔥 بخش ششم — افزودن RoleSerializer (در صورت نیاز)

اگر در آینده نقش‌ها را مدل جدا کردیم، این نیاز می‌شود
فعلاً یک نسخه ساده می‌گذاریم:

```python
class RoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['admin', 'teacher', 'student'])
```

---

# 🔥 بخش هفتم — اتصال Serializerها به View ها

### ProfileViewSet را به ProfileSerializer وصل می‌کنیم:

در فایل:

```
accounts/views.py
```

تغییر:

```python
from .serializers import ProfileSerializer

class ProfileViewSet(viewsets.GenericViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "پروفایل بروز شد"})
```

---

# 🎉 نتیجه جلسه ۶

✔ Serializerها کامل و حرفه‌ای شدند
✔ Validation شماره موبایل و کد ملی
✔ Password hashing درست
✔ Register از Profile جدا شد
✔ Serializer مخصوص نمایش User ساخته شد

از اینجا به بعد APIهای ما **استاندارد، امن و کاملاً سازمانی** هستند.

---

# 🎯 جلسه ۷ — Routing و ساخت مسیرهای RESTful + JWT Token URLs

در جلسه بعد:

* router ها را تمیز می‌کنیم
* مسیرهای JWT کامل می‌شود
* مسیر token/refresh/ را اضافه می‌کنیم
* ساختار RESTful نهایی می‌شود

اگر آماده‌ای بگو:

### **بریم جلسه هفتم**
