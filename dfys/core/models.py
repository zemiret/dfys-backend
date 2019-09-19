from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)


class Skill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    allowed_categories = models.ManyToManyField(Category)
    name = models.CharField(max_length=128)
    add_date = models.DateTimeField()


class Activity(models.Model):
    title = models.CharField(max_length=128)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    description = models.TextField()
    add_date = models.DateTimeField()
    modify_date = models.DateTimeField()


class ActivityEntry(models.Model):
    class Meta:
        abstract = True

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    add_date = models.DateTimeField()
    modify_date = models.DateTimeField()


class Comment(ActivityEntry):
    content = models.TextField()


class Attachment(ActivityEntry):
    content = models.FileField()
