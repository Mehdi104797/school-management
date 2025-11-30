from django.contrib.auth.models import UserManager

class CustomUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        # مطمئن شو national_code و phone_number پر شده
        if not extra_fields.get('national_code'):
            raise ValueError("The National Code must be set")
        return super()._create_user(username, email, password, **extra_fields)
    
    