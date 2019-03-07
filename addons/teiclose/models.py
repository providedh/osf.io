
from django.db import models

from osf.models.base import BaseModel
from osf.utils.datetime_aware_jsonfield import JSONField


class AnnotationHistory(BaseModel):
    project_guid = models.TextField()
    file_guid = models.TextField()
    history = JSONField(blank=True, default=list)



