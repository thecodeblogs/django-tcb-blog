# Generated by Django 3.0.3 on 2020-06-04 00:48

from django.db import migrations
from slugify import slugify


def populate_slugs(apps, schema_editor):
    EntryEnvelope = apps.get_model('blog', 'EntryEnvelope')
    ees = EntryEnvelope.objects.all()
    for ee in ees:
        if ee.title is not None:
            slug = ee.entry.get('slug')
            if slug is None:
                new_slug = slugify(ee.title).lower()
                ee.entry['slug'] = new_slug
            else:
                ee.slug = slug
            ee.save()


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_entryenvelope_slug'),
    ]

    operations = [
        migrations.RunPython(populate_slugs, reverse_code=migrations.RunPython.noop),
    ]
