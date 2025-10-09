from django.db import models
from django.db.models import fields


class ModelThirteen(models.Model):
    name = models.CharField(max_length=1024)
