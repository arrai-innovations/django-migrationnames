from django.db import models


class ModelFourtyFive(models.Model):
    name = models.CharField(max_length=1024)
