from django.db import models


class ModelNine(models.Model):
    name = models.CharField(max_length=1024)


class ModelTen(models.Model):
    name = models.CharField(max_length=1024)


class ModelEleven(models.Model):
    name = models.CharField(max_length=1024)


class ModelTwelve(models.Model):
    name = models.CharField(max_length=1024)
