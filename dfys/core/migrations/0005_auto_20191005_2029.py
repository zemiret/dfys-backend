# Generated by Django 2.2.6 on 2019-10-05 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20190928_1928'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='type',
            field=models.SmallIntegerField(choices=[(0, 'Comment'), (1, 'Attachment')], default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comment',
            name='type',
            field=models.SmallIntegerField(choices=[(0, 'Comment'), (1, 'Attachment')], default=0),
            preserve_default=False,
        ),
    ]