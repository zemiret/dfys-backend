from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Category(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=False)
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
    COMMENT = 0
    ATTACHMENT = 1

    TYPE_CHOICES = (
        (COMMENT, 'Comment'),
        (ATTACHMENT, 'Attachment'),
    )

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    add_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    # This is acting as a 2-base class. Maybe not the best solution
    type = models.SmallIntegerField(choices=TYPE_CHOICES)
    comment_content = models.TextField(null=True, blank=True)
    attachment_content = models.FileField(null=True, blank=True)
