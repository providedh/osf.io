from django.db import models
from osf.models.base import BaseModel
from osf.utils.datetime_aware_jsonfield import JSONField


class AnnotationHistory(BaseModel):
    project_guid = models.CharField(max_length=255)
    file_guid = models.CharField(max_length=255)
    history = JSONField(blank=True, default=list)


class AnnotatingXmlContent(BaseModel):
    file_symbol = models.CharField(max_length=255)
    xml_content = models.TextField()
