# Generated by Django 3.1.5 on 2021-01-15 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0002_auto_20210115_0933'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='blog_url',
            field=models.URLField(default='', max_length=512),
        ),
    ]