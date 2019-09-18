from django.db import models


# Create your models here.
class Skill(models.Model):
    name = models.CharField(max_length=128)


class Category(models.Model):
    name = models.CharField(max_length=128)


class Activity(models.Model):
    title = models.CharField(max_length=128)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    description = models.TextField()
    last_edit_date = models.DateTimeField()


class Comment(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)


class Attachment(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

