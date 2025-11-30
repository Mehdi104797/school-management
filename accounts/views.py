from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User, UserSession
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ProfileSerializer,
    UserSerializer,
    RoleSerializer
)
from .permissions import (
    IsAdmin,
    IsTeacher,
    TeacherOrAdminPermission
)


# ───────────────────────────────────────
# 1. RegisterViewSet — ثبت‌نام
# ───────────────────────────────────────
class RegisterViewSet(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "ثبت‌نام با موفقیت انجام شد"},
            status=status.HTTP_201_CREATED
        )


# ───────────────────────────────────────
# 2. LoginViewSet — ورود + Session سفارشی
# ───────────────────────────────────────
class LoginViewSet(viewsets.GenericViewSet):
    serializer_class = LoginSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        # ذخیره Session سفارشی
        UserSession.objects.create(
            user=user,
            refresh_token=str(refresh),
            ip=request.META.get('REMOTE_ADDR'),
            device=request.META.get('HTTP_USER_AGENT', '')[:200]
        )

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": user.id,
        })


# ───────────────────────────────────────
# 3. LogoutViewSet — خروج + حذف Session
# ───────────────────────────────────────
class LogoutViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            UserSession.objects.filter(
                user=request.user,
                refresh_token=refresh_token
            ).delete()
        return Response({"message": "خروج با موفقیت انجام شد"})


# ───────────────────────────────────────
# 4. ProfileViewSet — نمایش و ویرایش پروفایل
# ───────────────────────────────────────
class ProfileViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def list(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def partial_update(self, request):
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "پروفایل با موفقیت بروزرسانی شد"})


# ───────────────────────────────────────
# 5. AdminViewSet — فقط برای ادمین‌ها
# ───────────────────────────────────────
class AdminViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = UserSerializer
    queryset = User.objects.all()


# ───────────────────────────────────────
# 6. TeacherViewSet — فقط برای معلم‌ها
# ───────────────────────────────────────
class TeacherViewSet(viewsets.ViewSet):
    permission_classes = [IsTeacher]

    def list(self, request):
        # می‌توانی در آینده اطلاعات کلاس‌ها، دروس و... را برگردانی
        return Response({"message": "به پنل معلم خوش آمدید!"})