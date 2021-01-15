from django.db import models


class Creator(models.Model):
    full_name = models.CharField(max_length=1000, blank=True)
    image_url = models.URLField(max_length=512, default="")


class Blog(models.Model):
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, blank=True)
    blog_date = models.DateTimeField(null=True, db_index=True)
    blog_html = models.TextField()
    tags = models.TextField()
    responses = models.TextField()
    image_url = models.URLField(max_length=512, default="")
    blog_url = models.URLField(max_length=512, default="")