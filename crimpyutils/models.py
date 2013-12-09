from jsonfield import JSONField
from django.db import models

class PropertiesMixin(models.Model):
    properties_json = JSONField(blank=True, default="{}")

    class Meta:
        abstract = True