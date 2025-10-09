from django.db import models


class ModelSix(models.Model):
    name = models.CharField(max_length=1024)


class ModelFive(models.Model):
    name = models.CharField(max_length=1024)


class ModelFour(models.Model):
    name = models.CharField(max_length=1024)
