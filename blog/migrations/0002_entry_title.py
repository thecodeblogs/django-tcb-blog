# Generated by Django 3.0.3 on 2020-03-01 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='title',
            field=models.TextField(null=True),
        ),
    ]
