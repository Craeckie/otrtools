from django.db import models


# Create your models here.
# class Title(models.Model):
#     title = models.CharField(max_length=200)
#     length = models.DateTime()

class Series(models.Model):
    url = models.URLField(max_length=300)
    website = models.CharField(max_length=2)
    series = models.CharField(max_length=200)
    german = models.BooleanField()
    otrNameFormat = models.CharField(max_length=200, blank=True)
    numSeasons = models.IntegerField(default=1)
    hidden = models.BooleanField(default=False)

    def get_season_range(self):
        return range(1, self.numSeasons + 1)

    def get_url(self, season=1):
        return self.url.format(season=season)

    def __str__(self):
        return self.series
