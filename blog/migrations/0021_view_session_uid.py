# Generated by Django 3.1.2 on 2021-01-19 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0020_auto_20210119_1042'),
    ]

    operations = [
        migrations.AddField(
            model_name='view',
            name='session_uid',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]