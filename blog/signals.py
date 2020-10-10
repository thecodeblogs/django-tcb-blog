import logging

from django.dispatch import receiver
from django.db.models.signals import post_save

from blog.models import EntryEnvelope
from blog.serializers import EntrySerializer

from blog.tasks import sync_to_the_code_blogs


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=EntryEnvelope)
def entry_post_save(sender, instance, *args, **kwargs):
    if instance.published:
        if instance.author.profile.token:
            sync_to_the_code_blogs.delay(str(instance.id))
