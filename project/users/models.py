from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import EmailField


class User(AbstractBaseUser):
    email = EmailField(unique=True)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
