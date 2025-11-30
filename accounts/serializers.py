from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


# ───────────────────────────────────────
# 1. RegisterSerializer — ثبت‌نام
# ───────────────────────────────────────
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            'phone_number', 'national_code', 'password',
            'first_name', 'last_name', 'father_name',
            'service_code', 'city', 'role'
        ]

    def validate_phone_number(self, value):
        if not (value.isdigit() and len(value) == 11 and value.startswith('09')):
            raise serializers.ValidationError("شماره موبایل معتبر نیست.")
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("این شماره موبایل قبلاً ثبت شده است.")
        return value

    def validate_national_code(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise serializers.ValidationError("کد ملی باید 10 رقم عددی باشد.")
        if User.objects.filter(national_code=value).exists():
            raise serializers.ValidationError("این کد ملی قبلاً ثبت شده است.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ───────────────────────────────────────
# 2. LoginSerializer — ورود
# ───────────────────────────────────────
class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            phone_number=data['phone_number'],
            password=data['password']
        )
        if not user:
            raise serializers.ValidationError("شماره موبایل یا رمز عبور اشتباه است.")
        data['user'] = user
        return data


# ───────────────────────────────────────
# 3. UserSerializer — خروجی کامل کاربر (برای Admin)
# ───────────────────────────────────────
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'national_code', 'service_code',
            'first_name', 'last_name', 'father_name', 'city', 'role'
        ]
        read_only_fields = ['id']


# ───────────────────────────────────────
# 4. ProfileSerializer — ویرایش پروفایل کاربر
# ───────────────────────────────────────
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'phone_number', 'national_code', 'service_code',
            'first_name', 'last_name', 'father_name', 'city', 'role'
        ]
        read_only_fields = ['phone_number', 'national_code', 'role']


# ───────────────────────────────────────
# 5. RoleSerializer — (اختیاری، برای آینده)
# ───────────────────────────────────────
class RoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['admin', 'teacher', 'student'])