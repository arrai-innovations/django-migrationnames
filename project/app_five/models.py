from django.db import models


class ModelEight(models.Model):
    name = models.CharField(max_length=1024)
