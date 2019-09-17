from django.db import models


# Create your models here.
class Skill(models.Model):
    name = models.CharField(max_length=128)


class Activity(models.Model):
    title = models.CharField(max_length=128)
    # category
    description = models.TextField()
    last_edit_date = models.DateTimeField()


class Comment(models.Model):
    pass


class Attachment(models.Model):
    pass


class Category(models.Model):
    name = models.CharField(max_length=128)
