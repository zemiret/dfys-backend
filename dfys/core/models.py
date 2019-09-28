from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Category(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    is_base_category = models.BooleanField(default=False)


class Skill(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)
    name = models.CharField(max_length=128)
    add_date = models.DateTimeField(auto_now_add=True)


class Activity(models.Model):
    title = models.CharField(max_length=128)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    description = models.TextField(blank=True, default='')
    add_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)


class ActivityEntry(models.Model):
    class Meta:
        abstract = True

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    add_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)


class Comment(ActivityEntry):
    content = models.TextField()


class Attachment(ActivityEntry):
    content = models.FileField()
