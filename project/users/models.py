from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import EmailField
from django.db.models.fields import related


class User(AbstractBaseUser, PermissionsMixin):
    email = EmailField(
        db_collation="case_insensitive", unique=True, verbose_name="field_eight address"
    )
    is_staff = models.BooleanField(
        "staff field_eleven",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text="Designates whether this user should be treated as active. "
        "Unselect this instead of deleting accounts.",
    )

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ("email",)


class ModelFiftyTwo(models.Model):
    name = models.CharField(max_length=1024)
