# Generated by Django 3.1.2 on 2021-01-24 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0024_visitorprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitorprofile',
            name='family',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='visitorprofile',
            name='major',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='visitorprofile',
            name='minor',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='visitorprofile',
            name='name',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='visitorprofile',
            name='patch',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='visitorprofile',
            name='version',
            field=models.TextField(blank=True, null=True),
        ),
    ]