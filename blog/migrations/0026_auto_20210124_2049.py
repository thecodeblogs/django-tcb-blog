# Generated by Django 3.1.2 on 2021-01-24 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0025_auto_20210124_1919'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitorprofile',
            name='device',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='visitorprofile',
            name='os_version',
            field=models.TextField(blank=True, null=True),
        ),
    ]
