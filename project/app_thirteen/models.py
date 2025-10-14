from django.db import models
from django.db.models import DO_NOTHING
from django.db.models import fields
from django.db.models.fields import related


class ModelThirty(models.Model):
    project = related.OneToOneField(
        "ModelThirtyOne", on_delete=DO_NOTHING, related_name="project_data"
    )
    active = fields.BooleanField(default=True)

    class Meta:
        db_table = "app_thirteen_projectdata"
        managed = False
        default_related_name = "project_data"


class ModelThirtyOne(models.Model):
    name = fields.CharField(max_length=1024)
    full_number = fields.CharField(max_length=1024, unique=True)
    non_billable = fields.BooleanField(default=False)
    # Refer to project/utils/globals.py for the hard code client name, used to determine if is_australian.
    is_australian = fields.BooleanField(default=False)

    class Meta:
        ordering = ("-full_number",)


class ModelThirtyTwo(models.Model):
    project = related.ForeignKey("ModelThirtyOne", on_delete=models.CASCADE)
    field_eleven = fields.CharField(
        max_length=1024,
        choices=(
            ("one", "One"),
            ("two", "Two"),
        ),
    )
    effective = fields.DateField()

    class Meta:
        default_related_name = "project_status_history"
        ordering = ("-effective",)
        unique_together = ("project", "effective")
