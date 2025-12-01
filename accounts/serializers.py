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
    
    
    
# ───────────────────────────────────────
# Serializer برای درخواست OTP
# ───────────────────────────────────────

class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate_phone_number(self, value):
        if not User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("این شماره ثبت نشده است.")
        return value




# ───────────────────────────────────────
#   View: ارسال OTP
# ───────────────────────────────────────

class ForgotPasswordViewSet(viewsets.GenericViewSet):
    serializer_class = ForgotPasswordSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone_number"]

        code = str(random.randint(100000, 999999))
        expires = timezone.now() + timedelta(minutes=3)

        OTP.objects.create(
            phone_number=phone,
            code=code,
            expires_at=expires
        )

        return Response({
            "message": "کد ارسال شد",
            "code": code  # موقت؛ بعداً حذف می‌شود
        })





# ───────────────────────────────────────
# تأیید OTP + ثبت رمز جدید
# ───────────────────────────────────────


class ResetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()
    new_password = serializers.CharField(min_length=6)



# ───────────────────────────────────────
# View: ریست رمز
# ───────────────────────────────────────

class ResetPasswordViewSet(viewsets.GenericViewSet):
    serializer_class = ResetPasswordSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        otp = OTP.objects.filter(
            phone_number=data["phone_number"],
            code=data["otp"],
            is_used=False
        ).last()

        if not otp or not otp.is_valid():
            return Response({"error": "کد نامعتبر یا منقضی شده"}, status=400)

        otp.is_used = True
        otp.save()

        user = User.objects.get(phone_number=data["phone_number"])
        user.set_password(data["new_password"])
        user.save()

        return Response({"message": "رمز با موفقیت تغییر کرد"})


# ───────────────────────────────────────
#محدودیت تلاش ورود (Anti-Brute-Force) 
# ───────────────────────────────────────
class LoginAttempt(models.Model):
    phone_number = models.CharField(max_length=11)
    ip = models.GenericIPAddressField()
    attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(auto_now=True)




# ───────────────────────────────────────
# 
# ───────────────────────────────────────


# ───────────────────────────────────────
# 
# ───────────────────────────────────────

# ───────────────────────────────────────
# 
# ───────────────────────────────────────

# ───────────────────────────────────────
# 
# ───────────────────────────────────────
