با توجه به کد و فایل‌هایی که تا الان ارسال کردی و ساختار پروژه‌ات، **همه سرویس‌های اصلی Backend برای یک سیستم مدیریت کاربر مبتنی بر نقش (Role-Based Auth API)** آماده هستند.

در ادامه لیست کامل **سرویس‌های (APIهای) موجود** در پروژه‌ات را با مسیر و توضیح عملکرد هر کدام می‌بینی:

---

## ✅ 1. **ثبت‌نام (Register)**
- **مسیر**: `POST /api/accounts/register/`
- **ورودی**:  
  ```json
  {
    "phone_number": "09121234567",
    "national_code": "1234567890",
    "password": "your_password",
    "first_name": "علی",
    "last_name": "رضایی",
    "father_name": "احمد",
    "service_code": "1234567890",
    "city": "تهران",
    "role": "student"  // یا "teacher" یا "admin"
  }
  ```
- **اعتبارسنجی**:  
  - شماره موبایل 11 رقم و شروع با `09`  
  - کد ملی 10 رقم  
  - یکتا بودن شماره و کد ملی  
- **خروجی**: پیام موفقیت

---

## ✅ 2. **ورود (Login)**
- **مسیر**: `POST /api/accounts/login/`
- **ورودی**:  
  ```json
  {
    "phone_number": "09121234567",
    "password": "your_password"
  }
  ```
- **عملکرد**:  
  - احراز هویت  
  - صدور `access_token` و `refresh_token`  
  - ذخیره `UserSession` در دیتابیس (IP + دستگاه)
- **خروجی**:  
  ```json
  {
    "access": "...",
    "refresh": "...",
    "user_id": 1
  }
  ```

---

## ✅ 3. **خروج (Logout)**
- **مسیر**: `POST /api/accounts/logout/`
- **نیازمند**: هدر `Authorization: Bearer <access_token>`
- **ورودی**:  
  ```json
  {
    "refresh": "<refresh_token>"
  }
  ```
- **عملکرد**:  
  - حذف رکورد `UserSession` مربوطه از دیتابیس  
  - نه blacklist کردن توکن (در حال حاضر)، بلکه حذف session

---

## ✅ 4. **پروفایل کاربر (Profile)**
- **مسیر**: `GET /api/accounts/profile/`
- **نیازمند**: هدر `Authorization: Bearer <access_token>`
- **خروجی**:  
  ```json
  {
    "phone_number": "09121234567",
    "national_code": "1234567890",
    "first_name": "علی",
    "last_name": "رضایی",
    "father_name": "احمد",
    "service_code": "1234567890",
    "city": "تهران",
    "role": "student"
  }
  ```

- **ویرایش پروفایل**: `PATCH /api/accounts/profile/`  
  - فقط فیلدهای قابل ویرایش (بدون `phone_number`, `national_code`, `role`)  
  - مثال: ویرایش `city`, `father_name`

---

## ✅ 5. **پنل ادمین (Admin Panel)**
- **مسیر**: `GET /api/accounts/admin-panel/`
- **نیازمند**: نقش `admin`
- **عملکرد**: نمایش لیست تمام کاربران
- **خروجی**: لیست JSON از تمام کاربران (با جزئیات)

---

## ✅ 6. **پنل معلم (Teacher Panel)**
- **مسیر**: `GET /api/accounts/teacher-panel/`
- **نیازمند**: نقش `teacher`
- **عملکرد**: پیام ساده برای تست دسترسی  
  (در آینده می‌توانی دروس، کلاس‌ها، غیبت و... را اینجا پیاده‌سازی کنی)

---

## 🔐 سیستم امنیت و دسترسی

- ✅ **احراز هویت با JWT** (`access_token` برای هر درخواست)
- ✅ **Session سفارشی** در دیتابیس (`UserSession`)
- ✅ **دسترسی مبتنی بر نقش**:
  - `IsAdmin`
  - `IsTeacher`
  - `IsStudent`
  - `TeacherOrAdminPermission` (برای APIهای مشترک)

---

## 📦 مدل‌های دیتابیس

1. **User**  
   - `phone_number`, `national_code`, `role`, `first_name`, `city`, ...
   - لاگین با `phone_number`
   - نقش: `admin` / `teacher` / `student`

2. **UserSession**  
   - ذخیره `refresh_token`, `IP`, `device`, `created_at`
   - برای مدیریت خروج و تشخیص دستگاه‌های فعال

---

## 🛠️ وضعیت فعلی

✅ تمام APIهای اصلی برای **ثبت‌نام، ورود، خروج، پروفایل، و دسترسی بر اساس نقش** پیاده‌سازی شده‌اند.  
✅ ساختار کاملاً تمیز، امن و قابل گسترش است.  
✅ آماده برای اتصال به **فرانت‌اند Vue.js** (یا هر کلاینت دیگری).

---

## 🔜 کارهای بعدی (اختیاری)

اگر بخواهی پروژه را کامل‌تر کنی:

1. **Refresh سفارشی**: بررسی `refresh_token` در `UserSession` قبل از صدور access جدید
2. **Blacklist توکن**: استفاده از `SimpleJWT` با `BLACKLIST_AFTER_ROTATION`
3. **ایمیل تأیید**: برای فعال‌سازی حساب
4. **فراموشی رمز عبور**
5. **آپلود تصویر پروفایل** (با `MEDIA_URL`)

---

## 🧪 نحوه تست

تو می‌تونی این APIها را با ابزارهای زیر تست کنی:

- **Postman** یا **Thunder Client** (در VS Code)
- **curl** در ترمینال
- یا مستقیماً در **فرانت‌اند Vue.js** (در آینده)

---

اگر بخوای، می‌تونم یک **فایل Postman Collection** یا **دستورات curl** برای تست هر سرویس برات بنویسم.

آماده‌ای بگی: **بریم سراغ تست یا جلسه فرانت‌اند؟**