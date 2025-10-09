from django.db import models


class ModelFourteen(models.Model):
    name = models.CharField(max_length=1024)
