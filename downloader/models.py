from django.db import models


class Task(models.Model):
    video_url = models.URLField(max_length=1000)
    audio_url = models.URLField(max_length=1000, null=True)
    otrkey = models.CharField(max_length=200)
    decrypted = models.CharField(max_length=200)
    cutlist = models.CharField(max_length=5000, null=True)
    log = models.CharField(max_length=50000)
    keep = models.BooleanField(default=False)
