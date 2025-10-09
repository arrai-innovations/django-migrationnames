from django.db import models


class ModelSeven(models.Model):
    name = models.CharField(max_length=1024)
