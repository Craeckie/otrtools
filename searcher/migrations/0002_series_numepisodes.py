# Generated by Django 2.1.2 on 2018-11-26 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('searcher', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='series',
            name='numEpisodes',
            field=models.IntegerField(default=1),
        ),
    ]
