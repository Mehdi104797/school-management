from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    مجوز فقط برای کاربرانی که نقش آن‌ها 'admin' است.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsTeacher(BasePermission):
    """
    مجوز فقط برای کاربرانی که نقش آن‌ها 'teacher' است.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'teacher'
        )


class IsStudent(BasePermission):
    """
    مجوز فقط برای کاربرانی که نقش آن‌ها 'student' است.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'student'
        )


class HasRole(BasePermission):
    """
    کلاس پایه برای مجوزهای چند‌نقشی.
    زیرکلاس‌ها باید `allowed_roles` را تعریف کنند.
    """
    allowed_roles = []

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.allowed_roles
        )


class TeacherOrAdminPermission(HasRole):
    """
    مجوز برای 'teacher' یا 'admin'.
    """
    allowed_roles = ['admin', 'teacher']