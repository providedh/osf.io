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
