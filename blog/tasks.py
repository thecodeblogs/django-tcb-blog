import logging
import requests
import datetime
import pytz

from backend.celery import app
from django.dispatch import receiver
from django.db.models.signals import post_save

from blog.models import EntryEnvelope
from blog.serializers import EntrySerializer


utc = pytz.UTC
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.task(name="publish_entries_if_scheduled")
def publish_entries_if_scheduled():
    now = utc.localize(datetime.datetime.now())
    published_list = []
    entries = EntryEnvelope.objects.filter(future_publish_date__isnull=False, should_publish_in_future=True,
                                           defunct=False).order_by('-edit_date', 'entry_id')
    for entry in entries:
        if entry.entry_id in published_list:
            logger.info('An entry for the id %s has already been published', str(entry.entry_id))
            entry.should_publish_in_future = False
            entry.defunct = True
            entry.published = False

            entry.entry['should_publish_in_future'] = False
            entry.entry['published'] = False
            entry.save()
        else:
            if entry.future_publish_date < now:
                entry.should_publish_in_future = False
                entry.published = True
                entry.publish_date = now
                entry.future_publish_processed_on = now

                entry.entry['should_publish_in_future'] = False
                entry.entry['published'] = True
                entry.entry['publish_date'] = now.isoformat()

                entry.save()


@app.task(name="sync_to_the_code_blogs")
def sync_to_the_code_blogs(entry_envelope_id):
    ee = EntryEnvelope.objects.get(pk=entry_envelope_id)
    token = ee.author.profile.token
    data = EntrySerializer(instance=ee)

    serializer = EntrySerializer(ee)

    if ee.author.profile.url:
        headers = {'Authorization': 'Token ' + token}
        r = requests.post(ee.author.profile.url + '/api/entries/', json=serializer.data, headers=headers)

        logger.info('Saved %s to TheCodeBlogs.com', str(ee.id))
    else:
        logger.info('No URL. Did not save %s to TheCodeBlogs.com', str(ee.id))


