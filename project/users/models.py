from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import EmailField


class User(AbstractBaseUser):
    email = EmailField(
        db_collation="case_insensitive", unique=True, verbose_name="field_eight address"
    )

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
