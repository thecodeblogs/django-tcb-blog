import hashlib
import uuid

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from backend.celery import app

# new imports!
import json
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


GRAVATAR_URL = 'https://www.gravatar.com/avatar/'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    comments_public = models.BooleanField(
        null=False, blank=False, default=False
    )
    gravatar_url = models.CharField(max_length=255, null=True, blank=True)
    token = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True, default="https://www.thecodeblogs.com")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    elif not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):

    if not instance.profile.gravatar_url:
        if instance.email:
            g_hash = hashlib.md5()
            g_hash.update(instance.email.lower().strip().encode('utf-8'))
            instance.profile.gravatar_url = GRAVATAR_URL + g_hash.hexdigest()
            instance.profile.save()

    instance.profile.save()


class Tag(models.Model):
    label = models.CharField(max_length=255, null=False, blank=False)


class EntryEnvelope(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entry_id = models.UUIDField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="author"
    )
    entry = JSONField()
    title = models.TextField(null=True)
    slug = models.TextField(null=True)

    tags = models.ManyToManyField(Tag, related_name="entries")

    version = models.IntegerField(null=True, blank=True, default=1)
    published = models.BooleanField(null=False, default=False)
    publish_date = models.DateTimeField(null=True)

    create_date = models.DateTimeField(null=True)
    edit_date = models.DateTimeField(null=True)

    defunct = models.BooleanField(null=False, default=False)

    def entry_formatted(self):
        # dump the json with indentation set

        # example for detail_text TextField
        # json_obj = json.loads(self.detail_text)
        # data = json.dumps(json_obj, indent=2)

        # with JSON field, no need to do .loads
        data = json.dumps(self.entry, indent=2)

        # format it with pygments and highlight it
        formatter = HtmlFormatter(style='colorful')
        response = highlight(data, JsonLexer(), formatter)

        # include the style sheet
        style = "<style>" + formatter.get_style_defs() + "</style><br/>"

        return mark_safe(style + response)

    entry_formatted.short_description = 'Entry Formatted'

    def populate_stuff(self):
        self.title = self.entry.get('title')
        self.create_date = self.entry.get('create_date')
        self.edit_date = self.entry.get('edit_date')
        self.entry_id = self.entry.get('id')
        self.slug = self.entry.get('slug')
        self.published = self.entry.get('published')
        self.publish_date = self.entry.get('publish_date')
        self.version = self.entry.get('version')

        tags = self.entry.get('tags')
        if tags:
            for entry_tag in tags:
                tag, created = Tag.objects.get_or_create(label=entry_tag)

    class Meta:
        abstract = False


@receiver(pre_save, sender=EntryEnvelope)
def entry_pre_save(sender, instance, *args, **kwargs):
    instance.populate_stuff()


@app.task(name="make_all_other_entries_unpublished")
def manage_publish_states(entry_envelope_id):
    ee = EntryEnvelope.objects.get(pk=entry_envelope_id)
    entry_id = ee.entry_id
    logger.info('Marking all other entries unpublished for %s', entry_id)
    all_other_entries = EntryEnvelope.objects.filter(entry_id=entry_id, version__lt=ee.version).exclude(id=entry_envelope_id)
    all_other_entries.update(published=False, defunct=True)


@receiver(post_save, sender=EntryEnvelope)
def entry_post_save(sender, instance, *args, **kwargs):
    tags = instance.entry.get('tags')
    if tags:
        for entry_tag in tags:
            tag, created = Tag.objects.get_or_create(label=entry_tag)
            instance.tags.add(tag)
    if instance.published:
        manage_publish_states.delay(str(instance.id))


class Comment(models.Model):
    entry_envelope = models.ForeignKey(
        EntryEnvelope,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=False)

