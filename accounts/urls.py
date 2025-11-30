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