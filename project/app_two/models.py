from django.db import models


class ModelTwo(models.Model):
    name = models.CharField(max_length=1024)
