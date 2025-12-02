# 📋 **لیست کامل API‌های سیستم احراز هویت**

## 🔐 **1. احراز هویت (Authentication)**

### **1.1 ثبت‌نام کاربر**
**Endpoint:** `POST /api/accounts/register/`  
**دسترسی:** عمومی  
**ورودی:**
```json
{
  "phone_number": "09399432714",
  "national_code": "1234567890",
  "password": "Test@1234",
  "first_name": "علی",
  "last_name": "رضایی",
  "role": "student"
}
```
**پاسخ موفق:**
```json
{
  "message": "ثبت‌نام با موفقیت انجام شد",
  "user_id": 1
}
```

### **1.2 ورود به سیستم**
**Endpoint:** `POST /api/accounts/login/`  
**دسترسی:** عمومی  
**ورودی:**
```json
{
  "phone_number": "09399432714",
  "password": "Test@1234"
}
```
**پاسخ موفق:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": 1,
  "role": "student"
}
```

### **1.3 خروج از سیستم**
**Endpoint:** `POST /api/accounts/logout/`  
**دسترسی:** نیاز به احراز هویت  
**ورودی:**
```json
{
  "refresh": "refresh_token_here"
}
```
**پاسخ موفق:**
```json
{
  "message": "خروج با موفقیت انجام شد"
}
```

---

## 👤 **2. مدیریت پروفایل (Profile)**

### **2.1 مشاهده پروفایل**
**Endpoint:** `GET /api/accounts/profile/`  
**دسترسی:** نیاز به احراز هویت  
**هدر:**
```
Authorization: Bearer <access_token>
```
**پاسخ موفق:**
```json
{
  "phone_number": "09399432714",
  "national_code": "1234567890",
  "first_name": "علی",
  "last_name": "رضایی",
  "role": "student"
}
```

### **2.2 ویرایش پروفایل**
**Endpoint:** `PATCH /api/accounts/profile/`  
**دسترسی:** نیاز به احراز هویت  
**ورودی:**
```json
{
  "first_name": "محمد",
  "last_name": "احمدی",
  "city": "تهران"
}
```
**پاسخ موفق:**
```json
{
  "message": "پروفایل با موفقیت بروزرسانی شد"
}
```

---

## 🔒 **3. امنیت (Security)**

### **3.1 درخواست بازیابی رمز عبور**
**Endpoint:** `POST /api/accounts/forgot-password/`  
**دسترسی:** عمومی  
**ورودی:**
```json
{
  "phone_number": "09399432714"
}
```
**پاسخ موفق:**
```json
{
  "message": "کد بازیابی ارسال شد",
  "expires_in": "10 دقیقه"
}
```

### **3.2 تأیید OTP و تغییر رمز**
**Endpoint:** `POST /api/accounts/verify-otp/`  
**دسترسی:** عمومی  
**ورودی:**
```json
{
  "phone_number": "09399432714",
  "otp_code": "123456",
  "new_password": "NewPass@1234"
}
```
**پاسخ موفق:**
```json
{
  "message": "رمز عبور با موفقیت تغییر کرد"
}
```

### **3.3 تأیید شماره موبایل**
**Endpoint:** `POST /api/accounts/verify-phone/verify/`  
**دسترسی:** نیاز به احراز هویت  
**ورودی:**
```json
{
  "phone_number": "09399432714",
  "verification_code": "123456"
}
```
**پاسخ موفق:**
```json
{
  "message": "شماره موبایل با موفقیت تأیید شد"
}
```

---

## 👑 **4. مدیریت نقش‌ها (Role Management)**

### **4.1 لیست کاربران بر اساس نقش**
**Endpoint:** `GET /api/accounts/role-management/`  
**دسترسی:** فقط ادمین  
**پارامترهای اختیاری:** `?role=student`  
**پاسخ موفق:**
```json
{
  "stats": {
    "total_users": 150,
    "admin_count": 5,
    "teacher_count": 20,
    "student_count": 125
  },
  "users": [...]
}
```

### **4.2 تغییر نقش کاربر**
**Endpoint:** `POST /api/accounts/role-management/change_role/`  
**دسترسی:** فقط ادمین  
**ورودی:**
```json
{
  "user_id": 5,
  "new_role": "teacher",
  "reason": "ارتقا به مربی"
}
```
**پاسخ موفق:**
```json
{
  "message": "نقش کاربر 09399432714 به teacher تغییر کرد"
}
```

---

## 💻 **5. مدیریت نشست‌ها (Session Management)**

### **5.1 لیست نشست‌های فعال**
**Endpoint:** `GET /api/accounts/session-management/`  
**دسترسی:** نیاز به احراز هویت  
**پاسخ موفق:**
```json
[
  {
    "id": 1,
    "created_at": "2024-01-15T10:30:00Z",
    "ip": "192.168.1.100",
    "device": "Chrome on Windows",
    "current": true
  }
]
```

### **5.2 ابطال یک نشست خاص**
**Endpoint:** `POST /api/accounts/session-management/revoke_session/`  
**دسترسی:** نیاز به احراز هویت  
**ورودی:**
```json
{
  "session_id": 2
}
```
**پاسخ موفق:**
```json
{
  "message": "Session با موفقیت باطل شد"
}
```

### **5.3 ابطال همه نشست‌ها**
**Endpoint:** `POST /api/accounts/session-management/revoke_all_sessions/`  
**دسترسی:** نیاز به احراز هویت  
**پاسخ موفق:**
```json
{
  "message": "3 Session باطل شد"
}
```

---

## 📊 **6. داشبورد و گزارشات**

### **6.1 آمار سیستم**
**Endpoint:** `GET /api/accounts/admin-dashboard/dashboard_stats/`  
**دسترسی:** فقط ادمین  
**پارامترهای اختیاری:** `?range=daily` (daily, weekly, monthly)  
**پاسخ موفق:**
```json
{
  "user_stats": {
    "total_users": 150,
    "active_users": 140,
    "new_users": 10
  },
  "login_stats": {
    "successful": 500,
    "failed": 20,
    "success_rate": 96.15
  }
}
```

---

## 🏫 **7. پنل‌های اختصاصی**

### **7.1 پنل ادمین**
**Endpoint:** `GET /api/accounts/admin-panel/`  
**دسترسی:** فقط ادمین  
**پاسخ:** لیست کامل کاربران

### **7.2 پنل معلم**
**Endpoint:** `GET /api/accounts/teacher-panel/`  
**دسترسی:** فقط معلم  
**پاسخ:**
```json
{
  "message": "به پنل معلم خوش آمدید!"
}
```

---

## 🧪 **اسکریپت تست خودکار همه API‌ها:**

```bash
#!/bin/bash
# test_all_apis.sh

echo "🚀 شروع تست کامل API‌های سیستم احراز هویت"
echo "==========================================="

BASE_URL="http://127.0.0.1:8000"

# 1. تست ثبت‌نام
echo "1. تست ثبت‌نام..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/accounts/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "09391111111",
    "national_code": "1111111111",
    "password": "Test@1234",
    "first_name": "تست",
    "last_name": "کاربر",
    "role": "student"
  }')

echo "   پاسخ: $REGISTER_RESPONSE"

# 2. تست ورود
echo "2. تست ورود..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/accounts/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "09391111111",
    "password": "Test@1234"
  }')

echo "   پاسخ: $LOGIN_RESPONSE"

# استخراج توکن از پاسخ
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ خطا: توکن دریافت نشد"
  exit 1
fi

echo "   توکن دریافت شد: ${ACCESS_TOKEN:0:20}..."

# 3. تست مشاهده پروفایل
echo "3. تست مشاهده پروفایل..."
PROFILE_RESPONSE=$(curl -s -X GET "$BASE_URL/api/accounts/profile/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "   پاسخ: $PROFILE_RESPONSE"

# 4. تست بازیابی رمز
echo "4. تست درخواست بازیابی رمز..."
FORGOT_PASS_RESPONSE=$(curl -s -X POST "$BASE_URL/api/accounts/forgot-password/" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "09391111111"}')

echo "   پاسخ: $FORGOT_PASS_RESPONSE"

# 5. تست لیست نشست‌ها
echo "5. تست لیست نشست‌ها..."
SESSIONS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/accounts/session-management/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "   پاسخ: $SESSIONS_RESPONSE"

# 6. تست خروج
echo "6. تست خروج..."
LOGOUT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/accounts/logout/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "refresh_token_here"}')

echo "   پاسخ: $LOGOUT_RESPONSE"

echo "✅ تست‌ها تکمیل شد!"
```

---

## 📱 **تست با Postman:**

### **1. Import Collection:**
```json
{
  "info": {
    "name": "Auth System API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Register",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "url": "http://127.0.0.1:8000/api/accounts/register/",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"phone_number\": \"09391111111\",\n  \"national_code\": \"1111111111\",\n  \"password\": \"Test@1234\",\n  \"first_name\": \"تست\",\n  \"last_name\": \"کاربر\",\n  \"role\": \"student\"\n}"
        }
      }
    },
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "url": "http://127.0.0.1:8000/api/accounts/login/",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"phone_number\": \"09391111111\",\n  \"password\": \"Test@1234\"\n}"
        }
      }
    },
    {
      "name": "Profile",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}"
          }
        ],
        "url": "http://127.0.0.1:8000/api/accounts/profile/"
      }
    }
  ]
}
```

### **2. Environment Variables در Postman:**
```json
{
  "id": "auth-env",
  "name": "Auth Environment",
  "values": [
    {
      "key": "base_url",
      "value": "http://127.0.0.1:8000",
      "type": "default",
      "enabled": true
    },
    {
      "key": "access_token",
      "value": "",
      "type": "secret",
      "enabled": true
    },
    {
      "key": "refresh_token",
      "value": "",
      "type": "secret",
      "enabled": true
    }
  ]
}
```

---

## 🐍 **تست با Python:**

```python
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_register():
    """تست ثبت‌نام"""
    url = f"{BASE_URL}/api/accounts/register/"
    data = {
        "phone_number": "09392222222",
        "national_code": "2222222222",
        "password": "Test@1234",
        "first_name": "پایتون",
        "last_name": "تست",
        "role": "student"
    }
    
    response = requests.post(url, json=data)
    print(f"ثبت‌نام: {response.status_code} - {response.json()}")
    return response.json()

def test_login():
    """تست ورود"""
    url = f"{BASE_URL}/api/accounts/login/"
    data = {
        "phone_number": "09392222222",
        "password": "Test@1234"
    }
    
    response = requests.post(url, json=data)
    print(f"ورود: {response.status_code}")
    
    if response.status_code == 200:
        tokens = response.json()
        print(f"توکن: {tokens['access'][:50]}...")
        return tokens
    return None

def test_profile(access_token):
    """تست پروفایل"""
    url = f"{BASE_URL}/api/accounts/profile/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    print(f"پروفایل: {response.status_code} - {response.json()}")
    return response.json()

def test_all_apis():
    """تست همه API‌ها"""
    print("🚀 شروع تست API‌ها\n")
    
    # 1. ثبت‌نام
    register_result = test_register()
    
    # 2. ورود
    tokens = test_login()
    if not tokens:
        print("❌ خطا در ورود")
        return
    
    # 3. پروفایل
    profile_result = test_profile(tokens['access'])
    
    # 4. بازیابی رمز
    url = f"{BASE_URL}/api/accounts/forgot-password/"
    data = {"phone_number": "09392222222"}
    response = requests.post(url, json=data)
    print(f"بازیابی رمز: {response.status_code} - {response.json()}")
    
    print("\n✅ تست‌ها تکمیل شد!")

if __name__ == "__main__":
    test_all_apis()
```

---

## 📝 **چک‌لیست تست:**

### **✅ تست‌های اصلی:**
1. [ ] ثبت‌نام کاربر جدید
2. [ ] ورود با اطلاعات صحیح
3. [ ] ورود با اطلاعات نادرست
4. [ ] مشاهده پروفایل با توکن
5. [ ] ویرایش پروفایل
6. [ ] درخواست بازیابی رمز
7. [ ] تغییر رمز با OTP
8. [ ] لیست نشست‌ها
9. [ ] خروج از سیستم

### **✅ تست‌های ادمین:**
1. [ ] مشاهده لیست کاربران
2. [ ] فیلتر کاربران بر اساس نقش
3. [ ] تغییر نقش کاربر
4. [ ] مشاهده آمار سیستم

### **✅ تست‌های خطا:**
1. [ ] ثبت‌نام با شماره تکراری
2. [ ] ثبت‌نام با کد ملی تکراری
3. [ ] ورود با رمز اشتباه
4. [ ] دسترسی بدون توکن
5. [ ] دسترسی با توکن منقضی شده

---

## 🎯 **نکات مهم تست:**

1. **همیشه از شماره موبایل‌های مختلف استفاده کن**
2. **توکن‌ها را در جای امن ذخیره کن**
3. **پس از هر تست، sessionها را پاک کن**
4. **برای تست ادمین، اول یک کاربر ادمین بساز**
5. **از Postman Variables برای مدیریت توکن‌ها استفاده کن**

این لیست کامل تمام API‌های سیستم را پوشش می‌دهد. می‌توانی آن را کپی کنی و در پست خودت ذخیره کنی! 🚀