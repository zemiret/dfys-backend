from django.contrib.auth.models import User
from django.db import models


class TrackCreateModel(models.Model):
    class Meta:
        abstract = True

    add_date = models.DateTimeField(auto_now_add=True)


class TrackCreateUpdateModel(TrackCreateModel):
    class Meta:
        abstract = True

    modify_date = models.DateTimeField(auto_now=True)


class Category(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=False)
    is_base_category = models.BooleanField(default=False)


class Skill(TrackCreateModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)
    name = models.CharField(max_length=128)


class Activity(TrackCreateUpdateModel):
    title = models.CharField(max_length=128)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    description = models.TextField(blank=True, default='')


class ActivityEntry(TrackCreateUpdateModel):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
