# Generated by Django 3.1.5 on 2021-01-16 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0004_searchhistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=1000)),
                ('last_recent_year', models.IntegerField(default=0)),
                ('blogs', models.ManyToManyField(to='crawler.Blog')),
            ],
        ),
        migrations.DeleteModel(
            name='SearchHistory',
        ),
    ]
