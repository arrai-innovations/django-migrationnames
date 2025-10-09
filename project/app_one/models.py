from django.db import models


class ModelOne(models.Model):
    name = models.CharField(max_length=1024)

