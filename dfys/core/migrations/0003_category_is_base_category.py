# Generated by Django 2.2.5 on 2019-09-28 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20190928_1720'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_base_category',
            field=models.BooleanField(default=False),
        ),
    ]
