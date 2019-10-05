from django.contrib import admin

# Register your models here.
from dfys.core.models import Category, Activity, Skill, ActivityEntry

admin.site.register(Category)
admin.site.register(Skill)
admin.site.register(Activity)
admin.site.register(ActivityEntry)
