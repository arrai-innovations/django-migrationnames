from django.db import models


class ModelTwenty(models.Model):
    name = models.CharField(max_length=1024)
