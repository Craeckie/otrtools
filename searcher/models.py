from django.db import models

# Create your models here.
# class Title(models.Model):
#     title = models.CharField(max_length=200)
#     length = models.DateTime()

class Series(models.Model):
    url = models.URLField(max_length=300)
    website = models.CharField(max_length=2)
    series = models.CharField(max_length=200)
