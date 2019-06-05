# -*- coding: utf-8 -*-

import logging
from framework.celery_tasks import app as celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name='teiclose.channels_presence.tasks.prune_presences', bind=True)
def prune_presence(self):
    # Import here, because of bug in Celery v3.2.1 - https://github.com/celery/celery/issues/4699
    from channels_presence.models import Room

    Room.objects.prune_presences()


@celery_app.task(name='teiclose.channels_presence.tasks.prune_rooms', bind=True)
def prune_rooms(self):
    # Import here, because of bug in Celery v3.2.1 - https://github.com/celery/celery/issues/4699
    from channels_presence.models import Room

    Room.objects.prune_rooms()


@celery_app.task(name='teiclose.prune_orphaned_annotating_xml_contents', bind=True)
def prune_orphaned_annotating_xml_contents(self):
    # Import here, because of bug in Celery v3.2.1 - https://github.com/celery/celery/issues/4699
    from channels_presence.models import Room
    from models import AnnotatingXmlContent

    active_rooms = Room.objects.all()
    annotating_xml_contents = AnnotatingXmlContent.objects.all()

    active_rooms_symbols = []

    for room in active_rooms:
        active_rooms_symbols.append(room.channel_name)

    for xml_content in annotating_xml_contents:
        if xml_content.file_symbol not in active_rooms_symbols:
            xml_content.delete()
